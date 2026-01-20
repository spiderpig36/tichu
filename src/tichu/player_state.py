from dataclasses import dataclass, field
from enum import Enum
from tichu.card import Card


class PlayerType(Enum):
    HUMAN = "human"
    MINI_MAXI = "mini_maxi"
    LLM = "llm"
    RANDOM = "random"


@dataclass
class PlayerState:
    hand: list[Card] = field(default_factory=list)
    card_stack: list[Card] = field(default_factory=list)
    player_type: PlayerType = PlayerType.HUMAN
    has_passed: bool = False
    tichu_called: bool = False
    grand_tichu_called: bool = False
