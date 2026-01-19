import logging
import random
from typing import Literal
from tichu import HAND_SIZE, NUM_PLAYERS
from tichu.card import Color, NORMAL_CARD_VALUES
from tichu.combination import Combination
from tichu.player_state import PlayerState, PlayerType
from tichu.tichu_state import TichuState


class Player:
    def __init__(
        self,
        name: str = "Anonymous",
        player_type: PlayerType = PlayerType.HUMAN,
    ):
        self.name = name
        self.state = PlayerState(player_type=player_type)

    def set_game(self, game_state: TichuState):
        self.game_state = game_state

    def _get_input(self, prompt: str) -> str:
        return input(prompt).lower()

    def get_card_play(self) -> Literal["pass", "tichu"] | set[int]:
        match self.state.player_type:
            case PlayerType.HUMAN:
                return self._get_card_play_human()
            case PlayerType.RANDOM:
                return self._get_card_play_random()
            case _:
                raise NotImplementedError(
                    f"Player type {self.state.player_type} not implemented yet."
                )

    def _get_card_play_human(self) -> Literal["pass", "tichu"] | set[int]:
        play = self._get_input(
            "Enter the index of the card to play separated by a comma, 'pass' or 'tichu': "
        )
        if play == "pass":
            return "pass"
        if play == "tichu":
            return "tichu"
        try:
            card_indices = [int(idx.strip()) for idx in play.split(",")]
            return set(card_indices)
        except ValueError:
            logging.error(
                "Invalid input. Please enter valid card indices separated by commas. Try again."
            )
            return self._get_card_play_human()

    def _get_card_play_random(self) -> Literal["pass", "tichu"] | set[int]:
        possible_plays = Combination.possible_plays(
            self.game_state.current_combination, self.state.hand
        )
        if not possible_plays:
            return "pass"
        chosen_play = random.choice(possible_plays)
        return {self.state.hand.index(card) for card in chosen_play}

    def get_grand_tichu_play(self) -> Literal["pass", "grand_tichu"]:
        match self.state.player_type:
            case PlayerType.HUMAN:
                return self._get_grand_tichu_play_human()
            case PlayerType.RANDOM:
                return self._get_grand_tichu_play_random()
            case _:
                raise NotImplementedError(
                    f"Player type {self.state.player_type} not implemented yet."
                )

    def _get_grand_tichu_play_human(self) -> Literal["pass", "grand_tichu"]:
        play = self._get_input("Enter 'grand_tichu' to call a grand tichu or 'pass': ")
        if play == "pass":
            return "pass"
        if play == "grand_tichu":
            return "grand_tichu"
        logging.error("Invalid input. Please enter 'pass' or 'grand_tichu'. Try again.")
        return self._get_grand_tichu_play_human()

    def _get_grand_tichu_play_random(self) -> Literal["pass", "grand_tichu"]:
        return random.choice(["pass", "grand_tichu"])

    def get_dragon_stack_recipient_play(self) -> int:
        match self.state.player_type:
            case PlayerType.HUMAN:
                return self._get_dragon_stack_recipient_play_human()
            case PlayerType.RANDOM:
                return self._get_dragon_stack_recipient_play_random()
            case _:
                raise NotImplementedError(
                    f"Player type {self.state.player_type} not implemented yet."
                )

    def _get_dragon_stack_recipient_play_human(self) -> int:
        recipient = self._get_input(
            "Enter the index of the player who will receive the dragon stack: "
        )
        try:
            return int(recipient)
        except ValueError:
            logging.error(
                "Invalid input. Please enter a valid player index. Try again."
            )
            return self._get_dragon_stack_recipient_play_human()

    def _get_dragon_stack_recipient_play_random(self) -> int:
        return random.randint(0, NUM_PLAYERS - 1)

    def get_mahjong_wish_play(self) -> int:
        match self.state.player_type:
            case PlayerType.HUMAN:
                return self._get_mahjong_wish_play_human()
            case PlayerType.RANDOM:
                return self._get_mahjong_wish_play_random()
            case _:
                raise NotImplementedError(
                    f"Player type {self.state.player_type} not implemented yet."
                )

    def _get_mahjong_wish_play_human(self) -> int:
        wish = self._get_input("Enter the value of the card you wish for (2-14): ")
        try:
            value = int(wish)
            if value in NORMAL_CARD_VALUES:
                return value
            logging.error(
                "Invalid input. Please enter a value between 2 and 14. Try again."
            )
            return self._get_mahjong_wish_play_human()
        except ValueError:
            logging.error(
                "Invalid input. Please enter a numeric card value. Try again."
            )
            return self._get_mahjong_wish_play_human()

    def _get_mahjong_wish_play_random(self) -> int:
        return random.choice(NORMAL_CARD_VALUES)

    def get_push_play(self) -> set[int]:
        match self.state.player_type:
            case PlayerType.HUMAN:
                return self._get_push_play_human()
            case PlayerType.RANDOM:
                return self._get_push_play_random()
            case _:
                raise NotImplementedError(
                    f"Player type {self.state.player_type} not implemented yet."
                )

    def _get_push_play_human(self) -> set[int]:
        push = self._get_input(
            "Enter cards to push, first player to the left, next partner player and last player to the right, separated by commas: "
        )
        try:
            card_indices = [int(idx.strip()) for idx in push.split(",")]
            if len(card_indices) != NUM_PLAYERS - 1:
                logging.error("You must enter exactly three card indices. Try again.")
                return self._get_push_play_human()
            if not all(0 <= idx < HAND_SIZE for idx in card_indices):
                logging.error("One or more card indices are out of range. Try again.")
                return self._get_push_play_human()
            return set(card_indices)
        except ValueError:
            logging.error(
                "Invalid input. Please enter valid card indices separated by commas. Try again."
            )
            return self._get_push_play_human()

    def _get_push_play_random(self) -> set[int]:
        return set(random.sample(range(HAND_SIZE), NUM_PLAYERS - 1))

    def reset_for_new_round(self):
        """Reset the player's state for a new round."""
        self.state.hand.clear()
        self.state.card_stack.clear()
        self.state.has_passed = False
        self.state.tichu_called = False
        self.state.grand_tichu_called = False

    def add_card(self, card):
        """Add a card to the player's hand."""
        self.state.hand.append(card)

    def play_card(self, card):
        """Play a card from the player's hand."""
        if card in self.state.hand:
            self.state.hand.remove(card)
            return card
        msg = f"Card {card} not in hand"
        raise ValueError(msg)

    def has_mahjong(self):
        """Check if the player has the Mah Jong card."""
        return any(
            card
            for card in self.state.hand
            if card.color == Color.SPECIAL and card.value == 1
        )

    def __repr__(self):
        return f"Player(name={self.name})"

    def __str__(self):
        hand = "\n  ".join(
            [""] + [f"{i}: {card}" for i, card in enumerate(self.state.hand)]
        )
        return f"Player {self.name} with hand: {hand}"
