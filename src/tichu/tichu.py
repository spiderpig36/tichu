import random
import sys
from typing import IO, Literal

from tichu.card import NORMAL_CARD_VALUES, Card, Color, SpecialCard
from tichu.combination import Combination, CombinationType
from tichu.player import Player


class OutputManager:
    """Manages output to configurable destinations."""

    def __init__(self, output: IO | None = None):
        self.output = output if output is not None else sys.stdout

    def write(self, message: str):
        """Write a message to the configured output."""
        print(message, file=self.output)


class TichuError(Exception):
    """Base class for Tichu-related exceptions."""


class InvalidPlayError(TichuError):
    """Raised when a player makes an invalid play."""


NUM_PLAYERS = 4
TICHU_SCORE = 100
GRAND_TICHU_SCORE = 200
MATCH_SCORE = 200
HAND_SIZE = 14
GRAND_TICHU_HAND_SIZE = 8


class Tichu:
    def __init__(
        self, goal_score: int = 1000, seed: int | None = None, output: IO | None = None
    ):
        self.goal_score = goal_score
        self.output_manager = OutputManager(output)
        self.scores = [0, 0]
        self.current_round = 0
        self.players = [Player(f"Player {i}") for i in range(NUM_PLAYERS)]
        self.random = random.Random(seed)

        self.current_player_idx: int = 0
        self.winning_player_idx: int | None = None
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
        deck.extend([Card(Color.SPECIAL, card.value) for card in SpecialCard])

        self.random.shuffle(deck)
        for i, card in enumerate(deck):
            player = self.players[i % NUM_PLAYERS]
            player.add_card(card)
            if (
                len(player.hand) == GRAND_TICHU_HAND_SIZE
                and self.get_grand_tichu() == "grand_tichu"
            ):
                player.grand_tichu_called = True

        for player in self.players:
            player.hand.sort(key=lambda c: c.value)

        self.current_player_idx = next(
            i for i, p in enumerate(self.players) if p.has_mahjong()
        )
        self.winning_player_idx = None
        self.current_combination = None
        self.current_wish = None
        self.card_stack.clear()
        self.player_rankings.clear()

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]

    @property
    def winning_player(self) -> Player | None:
        if self.winning_player_idx is None:
            return None
        return self.players[self.winning_player_idx]

    def get_play(self) -> Literal["pass", "tichu"] | set[int]:
        prompt = input(
            "Enter the index of the card to play separated by a comma, 'pass' or 'tichu': "
        )
        if prompt.lower() == "pass":
            return "pass"
        if prompt.lower() == "tichu":
            return "tichu"
        try:
            card_indices = [int(idx.strip()) for idx in prompt.split(",")]
            return set(card_indices)
        except ValueError:
            self.output_manager.write(
                "Invalid input. Please enter valid card indices separated by commas. Try again."
            )
            return self.get_play()

    def get_grand_tichu(self) -> Literal["pass", "grand_tichu"]:
        prompt = input("Enter 'grand_tichu' to call a grand tichu or 'pass': ").lower()
        if prompt == "pass":
            return "pass"
        if prompt == "grand_tichu":
            return "grand_tichu"
        self.output_manager.write(
            "Invalid input. Please enter 'pass' or 'grand_tichue'. Try again."
        )
        return self.get_grand_tichu()

    def get_dragon_stack_recipient(self) -> int:
        recipient = input(
            "Enter the index of the player who will receive the dragon stack: "
        )
        try:
            return int(recipient)
        except ValueError:
            self.output_manager.write(
                "Invalid input. Please enter a valid player index. Try again."
            )
            return self.get_dragon_stack_recipient()

    def get_mahjong_wish(self) -> int:
        wish = input("Enter the value of the card you wish for (2-14): ")
        try:
            value = int(wish)
            if value in NORMAL_CARD_VALUES:
                return value
            self.output_manager.write(
                "Invalid input. Please enter a value between 2 and 14."
            )
            return self.get_mahjong_wish()
        except ValueError:
            self.output_manager.write(
                "Invalid input. Please enter a numeric card value. Try again."
            )
            return self.get_mahjong_wish()

    def get_push(self) -> set[int]:
        push = input(
            "Enter cards to push, first player to the left, next partner player and last player to the right, separated by commas: "
        )
        try:
            card_indices = [int(idx.strip()) for idx in push.split(",")]
            if len(card_indices) != NUM_PLAYERS - 1:
                self.output_manager.write(
                    "You must enter exactly three card indices. Try again."
                )
                return self.get_push()
            if not all(0 <= idx < HAND_SIZE for idx in card_indices):
                self.output_manager.write(
                    "One or more card indices are out of range. Try again."
                )
                return self.get_push()
            return set(card_indices)
        except ValueError:
            self.output_manager.write(
                "Invalid input. Please enter valid card indices separated by commas. Try again."
            )
            return self.get_push()

    @property
    def end_of_round(self) -> bool:
        return len(self.player_rankings) == NUM_PLAYERS - 1 or (
            len(self.player_rankings) == NUM_PLAYERS / 2
            and self.player_rankings[0] % 2 == self.player_rankings[1] % 2
        )

    def push_cards(self):
        cards_for_players = [[], [], [], []]
        for player_idx, player in enumerate(self.players):
            card_indices = self.get_push()
            cards_to_push = [
                card
                for card_idx, card in enumerate(player.hand)
                if card_idx in card_indices
            ]
            for card in cards_to_push:
                player.play_card(card)
            cards_for_players[(player_idx - 1) % NUM_PLAYERS].append(cards_to_push[0])
            cards_for_players[(player_idx + 2) % NUM_PLAYERS].append(cards_to_push[1])
            cards_for_players[(player_idx + 1) % NUM_PLAYERS].append(cards_to_push[2])
        for player_idx, player in enumerate(self.players):
            for card in cards_for_players[player_idx]:
                player.add_card(card)
            player.hand.sort(key=lambda c: c.value)

    def next_turn(self):
        self.output_manager.write(str(self.current_player))
        if self.current_player_idx in self.player_rankings:
            self.output_manager.write(
                f"{self.current_player.name} has no cards left and is skipped!"
            )
        else:
            current_hand = self.current_player.hand
            play = self.get_play()
            if play == "pass":
                if self.current_wish is not None and Combination.can_fulfill_wish(
                    self.current_combination, self.current_wish, current_hand
                ):
                    msg = f"You can fulfill the wish for card value {self.current_wish} and cannot pass."
                    raise InvalidPlayError(msg)
                self.output_manager.write(f"{self.current_player.name} has passed.")
                self.current_player.has_passed = True
                if all(
                    player.has_passed
                    for player in self.players
                    if player != self.winning_player
                ):

                    self.output_manager.write(
                        "All other players have passed. Resetting current combination."
                    )
                    if self.winning_player_idx is None or self.winning_player is None:
                        return
                    for player in self.players:
                        player.has_passed = False
                    if (
                        self.current_combination
                        and self.current_combination.combination_type
                        == CombinationType.SINGLE
                        and self.current_combination.value == SpecialCard.DRAGON.value
                    ):
                        self.output_manager.write(
                            f"{self.winning_player.name} wins the single card round and collects the card stack."
                        )
                        recipient_id = None
                        while not recipient_id:
                            recipient_id = self.get_dragon_stack_recipient()
                            if recipient_id < 0 or recipient_id >= NUM_PLAYERS:
                                self.output_manager.write(
                                    "Invalid player index. Try again."
                                )
                                recipient_id = None
                            elif recipient_id % 2 == self.winning_player_idx % 2:
                                self.output_manager.write(
                                    "Cannot give the dragon stack to your teammate. Try again."
                                )
                                recipient_id = None
                            else:
                                self.winning_player_idx = recipient_id
                    self.current_combination = None
                    self.winning_player.card_stack.extend(self.card_stack)
                    self.card_stack.clear()
                    self.current_player_idx = self.winning_player_idx
                    return
            elif play == "tichu":
                if self.current_player.grand_tichu_called:
                    msg = "Grand Tichu was already called."
                    raise InvalidPlayError(msg)
                if len(self.current_player.hand) != HAND_SIZE:
                    msg = "Tichu can only be called at the start of a turn with a full hand."
                    raise InvalidPlayError(msg)
                self.output_manager.write(
                    f"{self.current_player.name} has called Tichu!"
                )
                self.current_player.tichu_called = True
                return
            else:
                try:
                    played_cards = [current_hand[idx] for idx in play]
                except IndexError as ie:
                    msg = "One or more card indices are out of range."
                    raise InvalidPlayError(msg) from ie

                next_combination = Combination.from_cards(played_cards)
                if (
                    self.current_combination is not None
                    and not next_combination.can_be_played_on(self.current_combination)
                ):
                    msg = "Played combination must be of the same kind as the current combination and higher than the current combination."
                    raise InvalidPlayError(msg)
                if self.current_wish is not None:
                    if self.current_wish in [card.value for card in played_cards]:
                        self.output_manager.write(
                            f"{self.current_player.name} has fulfilled the wish for card value {self.current_wish}."
                        )
                        self.current_wish = None
                    elif self.current_wish in [
                        card.value for card in self.current_player.hand
                    ]:
                        if Combination.can_fulfill_wish(
                            next_combination,
                            self.current_wish,
                            self.current_player.hand,
                        ):
                            msg = f"The played combination does not fulfill the wish for card value {self.current_wish}."
                            raise InvalidPlayError(msg)

                self.current_combination = next_combination
                self.winning_player_idx = self.current_player_idx
                for card in played_cards:
                    self.current_player.play_card(card)
                if len(self.current_player.hand) == 0:
                    self.output_manager.write(
                        f"{self.current_player.name} has played all their cards and finished the round!"
                    )
                    self.player_rankings.append(self.current_player_idx)
                self.card_stack.extend(played_cards)

                self.output_manager.write(
                    f"Played combination: {self.current_combination.combination_type.name}"
                )
                self.output_manager.write(
                    ", ".join([str(card) for card in played_cards])
                )

                if (
                    self.current_combination.combination_type == CombinationType.SINGLE
                    and self.current_combination.value == SpecialCard.DOG.value
                ):
                    self.output_manager.write(
                        f"{self.current_player.name} played the Dog and passes the turn to their teammate."
                    )
                    self.current_player_idx = (
                        self.current_player_idx + 2
                    ) % NUM_PLAYERS
                    return
                if (
                    self.current_combination.combination_type == CombinationType.SINGLE
                    and self.current_combination.value == SpecialCard.PHOENIX.value
                ):
                    self.current_combination.value = (
                        self.card_stack[-2] + 0.5
                        if len(self.card_stack) > 1
                        else NORMAL_CARD_VALUES[0]
                    )
                if (
                    self.current_combination.combination_type == CombinationType.SINGLE
                    and self.current_combination.value == SpecialCard.MAH_JONG.value
                ):
                    self.current_wish = self.get_mahjong_wish()
                    self.output_manager.write(
                        f"{self.current_player.name} wishes for card value {self.current_wish}."
                    )

        self.current_player_idx = (self.current_player_idx + 1) % NUM_PLAYERS

    def end_round_scoring(self):
        team_scores = [0, 0]
        for i, player in enumerate(self.players):
            if player.tichu_called or player.grand_tichu_called:
                if self.player_rankings[0] == i:
                    team_scores[i % 2] += (
                        GRAND_TICHU_SCORE if player.grand_tichu_called else TICHU_SCORE
                    )
                else:
                    team_scores[i % 2] -= (
                        GRAND_TICHU_SCORE if player.grand_tichu_called else TICHU_SCORE
                    )
        if (
            len(self.player_rankings) == NUM_PLAYERS / 2
            and self.player_rankings[0] % 2 == self.player_rankings[1] % 2
        ):
            team_scores[self.player_rankings[0] % 2] += MATCH_SCORE
        else:
            loosing_player = next(
                i for i in range(NUM_PLAYERS) if i not in self.player_rankings
            )
            self.players[self.player_rankings[0]].card_stack.extend(
                self.players[loosing_player].card_stack
            )
            team_scores[(loosing_player + 1) % 2] += Card.count_card_scores(
                self.players[loosing_player].hand
            )
            for i, player in enumerate(self.players):
                team_id = i % 2
                team_scores[team_id] += Card.count_card_scores(player.card_stack)
        for i in range(len(team_scores)):
            self.scores[i] += team_scores[i]
            self.output_manager.write(
                f"Team {i} scored {team_scores[i]} points this round. Total score: {self.scores[i]}"
            )


if __name__ == "__main__":
    game = Tichu()
    game.start_new_round()
    while not game.end_of_round:
        try:
            game.next_turn()
        except InvalidPlayError as e:
            game.output_manager.write(f"Invalid play: {e}")
            continue
