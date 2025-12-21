import random
from typing import Literal
from .combination import Combination, CombinationType, InvalidCombinationError
from .card import NORMAL_CARD_VALUES, Card, Color, SpecialCard
from .player import Player

class InvalidPlayError(Exception):
    pass

class Tichu:
    def __init__(self, num_players: int = 4, goal_score: int = 1000):
        self.num_players = num_players
        self.goal_score = goal_score
        if self.num_players % 2 != 0:
            raise ValueError("Number of players must be even.")
        self.scores = [0] * (self.num_players // 2)
        self.current_round = 0
        self.players = [Player(f"Player {i}") for i in range(num_players)]

        self.current_player_id = 0
        self.winning_player_id: int | None = None
        self.current_combination: Combination | None = None
        self.current_wish: int | None = None
        self.card_stack: list[Card] = []

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
        for card in SpecialCard.values():
            deck.append(Card(Color.SPECIAL, card.value))

        random.shuffle(deck)
        for i, card in enumerate(deck):
            self.players[i % self.num_players].add_card(card)
        for player in self.players:
            player.hand.sort(key=lambda c: c.value)

        self.current_player_id = next(i for i, p in enumerate(self.players) if p.has_mahjong())
        self.winning_player_id = None
        self.current_combination = None
        self.current_wish = None
        self.card_stack.clear()

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
            print("Invalid input. Please enter valid card indices separated by commas.")
            return self.get_play()

    def get_dragon_stack_recipient(self) -> int:
        recipient = input("Enter the index of the player who will receive the dragon stack: ")
        try:
            return int(recipient)
        except ValueError:
            print("Invalid input. Please enter a valid player index.")
            return self.get_dragon_stack_recipient()
        
    def get_mahjong_wish(self) -> int:
        wish = input("Enter the value of the card you wish for (2-14): ")
        try:
            value = int(wish)
            if value in NORMAL_CARD_VALUES:
                return value
            else:
                print("Invalid card value. Please enter a value between 2 and 14.")
                return self.get_mahjong_wish()
        except ValueError:
            print("Invalid input. Please enter a numeric card value.")
            return self.get_mahjong_wish()

    def next_turn(self):
        print(self.current_player)
        current_hand = self.current_player.hand
        if len(current_hand) == 0:
            print(f"{self.current_player.name} has no cards left and is skipped!")
        else:
            played_cards = []
            while not played_cards:
                play = self.get_play() 
                if play == "pass":
                    print(f"{self.current_player.name} has passed.")
                    self.current_player.has_passed = True
                    if all(player.has_passed for player in self.players if player != self.winning_player):
                        print("All other players have passed. Resetting current combination.")
                        for player in self.players:
                            player.has_passed = False
                        if self.current_combination.combination_type == CombinationType.SINGLE and self.current_combination.value == SpecialCard.DRAGON.value:
                            print(f"{self.winning_player.name} wins the single card round and collects the card stack.")
                            recipient_id = None
                            while not recipient_id:
                                recipient_id = self.get_dragon_stack_recipient()
                                if recipient_id < 0 or recipient_id >= self.num_players:
                                    print("Invalid player index. Try again.")
                                    recipient_id = None
                                if recipient_id % 2 == self.winning_player_id % 2:
                                    print("Cannot give the dragon stack to your teammate. Try again.")
                                    recipient_id = None
                                self.winning_player_id = recipient_id
                        self.current_combination = None
                        self.winning_player.card_stack.extend(self.card_stack)
                        self.card_stack.clear()
                    break
                if play == "tichu":
                    if self.current_player.current_hand.size() != 14:
                        print("Tichu can only be called before playing any cards.")
                        continue
                    print(f"{self.current_player.name} has called Tichu!")
                    self.current_player.tichu_called = True
                    continue
                try:
                    played_cards = [card for i, card in enumerate(current_hand) if i in play]
                except IndexError:
                    print("One or more card indices are invalid. Try again.")
                    continue

                try:
                    next_combination = Combination.from_cards(played_cards)
                    if self.current_combination is not None:
                        if (next_combination.combination_type == self.current_combination.combination_type or next_combination.combination_type.get_bomb_strength() > self.current_combination.combination_type.get_bomb_strength()) and next_combination.length == self.current_combination.length:
                            if next_combination.value <= self.current_combination.value:
                                raise InvalidPlayError("Played combination must be higher than the current combination.")
                        else:
                            raise InvalidPlayError("Played combination must match the current combination type with the same length.")
                except InvalidPlayError as e:
                    print(f"Invalid play: {e}")
                    played_cards = []
                    continue
                except InvalidCombinationError:
                    print("Invalid combination of cards played. Try again.")
                    played_cards = []
                    continue
        
            self.current_combination = next_combination
            self.winning_player_id = self.current_player_id
            for card in played_cards:
                self.current_player.play_card(card)
            self.card_stack.extend(played_cards)

            print(f"Played combination: {self.current_combination.combination_type.name}")
            print(", ".join([str(card) for card in played_cards]))

            if self.current_combination.combination_type == CombinationType.SINGLE and self.current_combination.value == SpecialCard.DOG.value:
                print(f"{self.current_player.name} played the Dog and passes the turn to their teammate.")
                self.current_player_id = (self.current_player_id + 2) % self.num_players
                return
            if self.current_combination.combination_type == CombinationType.SINGLE and self.current_combination.value == SpecialCard.PHOENIX.value:
                self.current_combination.value = self.card_stack[-2] + 1 if len(self.card_stack) > 1 else NORMAL_CARD_VALUES[0]
            if self.current_combination.combination_type == CombinationType.SINGLE and self.current_combination.value == SpecialCard.MAH_JONG.value:
                self.current_wish = self.get_mahjong_wish()
                print(f"{self.current_player.name} wishes for card value {self.current_wish}.")
            
        self.current_player_id = (self.current_player_id + 1) % self.num_players

if __name__ == "__main__":
    print("Starting Tichu Game")
    game = Tichu()
    game.start_new_round()
    while True:
        game.next_turn()


