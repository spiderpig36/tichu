import abc
from typing import Literal

from tichu.card import Color
from tichu.player_state import PlayerState
from tichu.tichu_state import CardPlay, TichuState


class Player(abc.ABC):
    def __init__(self, name: str = "Anonymous"):
        self.name = name

    def set_game(self, game_state: TichuState, player_idx: int):
        self.game_state = game_state
        self.state = PlayerState(player_idx)

    def _get_input(self, prompt: str) -> str:
        return input(prompt).lower()

    @abc.abstractmethod
    def get_card_play(self) -> CardPlay:
        pass

    @abc.abstractmethod
    def get_grand_tichu_play(self) -> Literal["pass", "grand_tichu"]:
        pass

    @abc.abstractmethod
    def get_push_play(self) -> set[int]:
        pass

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

    def get_opponents(self):
        if self.state.player_idx % 2 == 0:
            return [1, 3]
        else:
            return [0, 2]

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
