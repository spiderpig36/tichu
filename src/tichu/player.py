import abc
from enum import Enum
from typing import Literal

from tichu.card import Color
from tichu.player_state import PlayerState
from tichu.tichu_state import CardPlay, TichuState


class PlayerType(Enum):
    HUMAN = "human"
    MINI_MAXI = "mini_maxi"
    LLM = "llm"
    RANDOM = "random"


class Player(abc.ABC):
    def __init__(self, name: str = "Anonymous"):
        self.name = name
        self.player_idx: int | None = None
        self.player_type = PlayerType.HUMAN

    def set_game(self, game_state: TichuState, player_idx: int):
        self.game_state = game_state
        self.player_idx = player_idx
        self.state = PlayerState()

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

    def get_opponents(self):
        if self.player_idx % 2 == 0:
            return [1, 3]
        else:
            return [0, 2]

    def __repr__(self):
        return f"Player(name={self.name})"

    def __str__(self):
        hand = "\n  ".join(
            [""] + [f"{i}: {card}" for i, card in enumerate(self.state.hand)]
        )
        return f"Player {self.name} with index {self.player_idx} and hand: {hand}"
