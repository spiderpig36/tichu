import random
import sys
from typing import IO, Literal
from .combination import Combination, CombinationType
from .card import NORMAL_CARD_VALUES, Card, Color, SpecialCard
from .player import Player

class OutputManager:
    """Manages output to configurable destinations."""
    def __init__(self, output: IO | None = None):
        self.output = output if output is not None else sys.stdout
    
    def write(self, message: str):
        """Write a message to the configured output."""
        print(message, file=self.output)

class TichuError(Exception):
    """Base class for Tichu-related exceptions."""
    pass

class InvalidPlayError(TichuError):
    """Raised when a player makes an invalid play."""
    pass


NUM_PLAYERS = 4

class Tichu:
    def __init__(self, goal_score: int = 1000, seed: int | None = None, output: IO | None = None):
        self.goal_score = goal_score
        self.output_manager = OutputManager(output)
        self.scores = [0, 0] 
        self.current_round = 0
        self.players = [Player(f"Player {i}") for i in range(NUM_PLAYERS)]
        self.random = random.Random(seed)

        self.current_player_id = 0
        self.winning_player_id: int | None = None
        self.current_combination: Combination | None = None
        self.current_wish: int | None = None
        self.card_stack: list[Card] = []
        self.player_rankings: list[int] = []

    def start_new_round(self):
        self.current_round += 1
        for player in self.players:
            player.reset_for_new_round()
        deck = []
        for color in Color:
            if color == Color.SPECIAL:
                continue
            for value in NORMAL_CARD_VALUES:
                card = Card(color, value)
                deck.append(card)
        for card in SpecialCard:
            deck.append(Card(Color.SPECIAL, card.value))

        self.random.shuffle(deck)
        for i, card in enumerate(deck):
            self.players[i % NUM_PLAYERS].add_card(card)
        for player in self.players:
            player.hand.sort(key=lambda c: c.value)

        self.current_player_id = next(i for i, p in enumerate(self.players) if p.has_mahjong())
        self.winning_player_id = None
        self.current_combination = None
        self.current_wish = None
        self.card_stack.clear()
        self.player_rankings.clear()

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_id]

    @property
    def winning_player(self) -> Player | None:
        if self.winning_player_id is None:
            return None
        return self.players[self.winning_player_id]

    def get_play(self) -> set[int] | Literal["pass"] | Literal["tichu"]:
        prompt = input("Enter the index of the card to play separated by a comma or 'pass': ")
        if prompt.lower() == "pass":
            return "pass"
        if prompt.lower() == "tichu":
            return "tichu"
        try:
            card_indices = [int(idx.strip()) for idx in prompt.split(",")]
            return set(card_indices)
        except ValueError:
            self.output_manager.write("Invalid input. Please enter valid card indices separated by commas. Try again.")
            return self.get_play()

    def get_dragon_stack_recipient(self) -> int:
        recipient = input("Enter the index of the player who will receive the dragon stack: ")
        try:
            return int(recipient)
        except ValueError:
            self.output_manager.write("Invalid input. Please enter a valid player index. Try again.")
            return self.get_dragon_stack_recipient()
        
    def get_mahjong_wish(self) -> int:
        wish = input("Enter the value of the card you wish for (2-14): ")
        try:
            value = int(wish)
            if value in NORMAL_CARD_VALUES:
                return value
            else:
                self.output_manager.write("Invalid input. Please enter a value between 2 and 14.")
                return self.get_mahjong_wish()
        except ValueError:
            self.output_manager.write("Invalid input. Please enter a numeric card value. Try again.")
            return self.get_mahjong_wish()

    @property    
    def end_of_round(self) -> bool:
        return len(self.player_rankings) == 3 or (len(self.player_rankings) == 2 and self.player_rankings[0] % 2 == self.player_rankings[1] % 2)

    def next_turn(self):
        self.output_manager.write(str(self.current_player))
        if self.current_player_id in self.player_rankings:
            self.output_manager.write(f"{self.current_player.name} has no cards left and is skipped!")
        else:
            current_hand = self.current_player.hand
            play = self.get_play() 
            if play == "pass":
                self.output_manager.write(f"{self.current_player.name} has passed.")
                self.current_player.has_passed = True
                if all(player.has_passed for player in self.players if player != self.winning_player):
                    self.output_manager.write("All other players have passed. Resetting current combination.")
                    for player in self.players:
                        player.has_passed = False
                    if self.current_combination.combination_type == CombinationType.SINGLE and self.current_combination.value == SpecialCard.DRAGON.value:
                        self.output_manager.write(f"{self.winning_player.name} wins the single card round and collects the card stack.")
                        recipient_id = None
                        while not recipient_id:
                            recipient_id = self.get_dragon_stack_recipient()
                            if recipient_id < 0 or recipient_id >= NUM_PLAYERS:
                                self.output_manager.write("Invalid player index. Try again.")
                                recipient_id = None
                            if recipient_id % 2 == self.winning_player_id % 2:
                                self.output_manager.write("Cannot give the dragon stack to your teammate. Try again.")
                                recipient_id = None
                            self.winning_player_id = recipient_id
                    self.current_combination = None
                    self.winning_player.card_stack.extend(self.card_stack)
                    self.card_stack.clear()
                    self.current_player_id = self.winning_player_id
                    return
            elif play == "tichu":
                if len(self.current_player.hand) != 14:
                    raise InvalidPlayError("Tichu can only be called at the start of a turn with a full hand.")
                self.output_manager.write(f"{self.current_player.name} has called Tichu!")
                self.current_player.tichu_called = True
                return
            else:
                try:
                    played_cards = [card for i, card in enumerate(current_hand) if i in play]
                except IndexError:
                    raise InvalidPlayError("One or more card indices are out of range.")

                next_combination = Combination.from_cards(played_cards)
                if next_combination is None:
                    raise InvalidPlayError("No valid combination could be formed with the played cards.")
                if self.current_combination is not None:
                    if (next_combination.combination_type == self.current_combination.combination_type or next_combination.combination_type.get_bomb_strength() > self.current_combination.combination_type.get_bomb_strength()) and next_combination.length == self.current_combination.length:
                        if next_combination.value <= self.current_combination.value:
                            raise InvalidPlayError("Played combination must be higher than the current combination.")
                    else:
                        raise InvalidPlayError("Played combination must match the current combination type with the same length.")
            
                self.current_combination = next_combination
                self.winning_player_id = self.current_player_id
                for card in played_cards:
                    self.current_player.play_card(card)
                if len(self.current_player.hand) == 0:
                    self.output_manager.write(f"{self.current_player.name} has played all their cards and finished the round!")
                    self.player_rankings.append(self.current_player_id)
                self.card_stack.extend(played_cards)

                self.output_manager.write(f"Played combination: {self.current_combination.combination_type.name}")
                self.output_manager.write(", ".join([str(card) for card in played_cards]))

                if self.current_combination.combination_type == CombinationType.SINGLE and self.current_combination.value == SpecialCard.DOG.value:
                    self.output_manager.write(f"{self.current_player.name} played the Dog and passes the turn to their teammate.")
                    self.current_player_id = (self.current_player_id + 2) % NUM_PLAYERS
                    return
                if self.current_combination.combination_type == CombinationType.SINGLE and self.current_combination.value == SpecialCard.PHOENIX.value:
                    self.current_combination.value = self.card_stack[-2] + 1 if len(self.card_stack) > 1 else NORMAL_CARD_VALUES[0]
                if self.current_combination.combination_type == CombinationType.SINGLE and self.current_combination.value == SpecialCard.MAH_JONG.value:
                    self.current_wish = self.get_mahjong_wish()
                    self.output_manager.write(f"{self.current_player.name} wishes for card value {self.current_wish}.")
            
        self.current_player_id = (self.current_player_id + 1) % NUM_PLAYERS

    def end_round_scoring(self):
        if len(self.player_rankings) == 2 and self.player_rankings[0] % 2 == self.player_rankings[1] % 2:
            self.scores[self.player_rankings[0] % 2] += 200
        else:
            team_scores = [0, 0]
            for i, player in enumerate(self.players):
                if player.tichu_called:
                    if self.player_rankings[0] == i:
                        team_scores[i % 2] += 100
                    else:
                        team_scores[i % 2] -= 100
            loosing_player = next(i for i in range(NUM_PLAYERS) if i not in self.player_rankings)
            self.players[self.player_rankings[0]].card_stack.extend(self.players[loosing_player].card_stack)
            team_scores[(loosing_player + 1) % 2] += Card.count_card_scores(self.players[loosing_player].hand)
            for i, player in enumerate(self.players):
                team_id = i % 2 
                team_scores[team_id] += Card.count_card_scores(player.card_stack) 
            for i in range(len(team_scores)):
                self.scores[i] += team_scores[i]
                self.output_manager.write(f"Team {i} scored {team_scores[i]} points this round. Total score: {self.scores[i]}")


if __name__ == "__main__":
    game = Tichu()
    game.start_new_round()
    while not game.end_of_round:
        try: 
            game.next_turn()
        except InvalidPlayError as e:
            game.output_manager.write(f"Invalid play: {e}")
            continue
    
