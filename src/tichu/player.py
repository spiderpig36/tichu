from enum import Enum
import logging
from typing import Literal
from tichu import HAND_SIZE, NUM_PLAYERS
from tichu.card import Card, Color, NORMAL_CARD_VALUES


class PlayerType(Enum):
    HUMAN = "human"
    MINI_MAXI = "mini_maxi"
    CHAT_GPT = "chat_gpt"
    RANDOM = "random"


class Player:
    def __init__(
        self, name: str = "Anonymous", player_type: PlayerType = PlayerType.HUMAN
    ):
        self.name = name
        self.hand: list[Card] = []
        self.card_stack: list[Card] = []
        self.reset_for_new_round()
        self.player_type = player_type

    def get_play(self, prompt: str) -> str:
        match self.player_type:
            case PlayerType.HUMAN:
                return input(prompt).lower()
            case _:
                raise NotImplementedError(
                    f"Player type {self.player_type} not implemented yet."
                )

    def get_card_play(self) -> Literal["pass", "tichu"] | set[int]:
        play = self.get_play(
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
            return self.get_card_play()

    def get_grand_tichu_play(self) -> Literal["pass", "grand_tichu"]:
        play = self.get_play("Enter 'grand_tichu' to call a grand tichu or 'pass': ")
        if play == "pass":
            return "pass"
        if play == "grand_tichu":
            return "grand_tichu"
        logging.error(
            "Invalid input. Please enter 'pass' or 'grand_tichue'. Try again."
        )
        return self.get_grand_tichu_play()

    def get_dragon_stack_recipient_play(self) -> int:
        recipient = self.get_play(
            "Enter the index of the player who will receive the dragon stack: "
        )
        try:
            return int(recipient)
        except ValueError:
            logging.error(
                "Invalid input. Please enter a valid player index. Try again."
            )
            return self.get_dragon_stack_recipient_play()

    def get_mahjong_wish_play(self) -> int:
        wish = self.get_play("Enter the value of the card you wish for (2-14): ")
        try:
            value = int(wish)
            if value in NORMAL_CARD_VALUES:
                return value
            logging.error(
                "Invalid input. Please enter a value between 2 and 14. Try again."
            )
            return self.get_mahjong_wish_play()
        except ValueError:
            logging.error(
                "Invalid input. Please enter a numeric card value. Try again."
            )
            return self.get_mahjong_wish_play()

    def get_push_play(self) -> set[int]:
        push = self.get_play(
            "Enter cards to push, first player to the left, next partner player and last player to the right, separated by commas: "
        )
        try:
            card_indices = [int(idx.strip()) for idx in push.split(",")]
            if len(card_indices) != NUM_PLAYERS - 1:
                logging.error("You must enter exactly three card indices. Try again.")
                return self.get_push_play()
            if not all(0 <= idx < HAND_SIZE for idx in card_indices):
                logging.error("One or more card indices are out of range. Try again.")
                return self.get_push_play()
            return set(card_indices)
        except ValueError:
            logging.error(
                "Invalid input. Please enter valid card indices separated by commas. Try again."
            )
            return self.get_push_play()

    def reset_for_new_round(self):
        """Reset the player's state for a new round."""
        self.hand.clear()
        self.card_stack.clear()
        self.has_passed = False
        self.tichu_called = False
        self.grand_tichu_called = False

    def add_card(self, card):
        """Add a card to the player's hand."""
        self.hand.append(card)

    def play_card(self, card):
        """Play a card from the player's hand."""
        if card in self.hand:
            self.hand.remove(card)
            return card
        msg = f"Card {card} not in hand"
        raise ValueError(msg)

    def has_mahjong(self):
        """Check if the player has the Mah Jong card."""
        return any(
            card
            for card in self.hand
            if card.color == Color.SPECIAL and card.value == 1
        )

    def __repr__(self):
        return f"Player(name={self.name})"

    def __str__(self):
        hand = "\n  ".join([""] + [f"{i}: {card}" for i, card in enumerate(self.hand)])
        return f"Player {self.name} with hand: {hand}"
