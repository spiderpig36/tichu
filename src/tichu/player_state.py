from dataclasses import dataclass, field

from tichu.card import Card


@dataclass
class PlayerState:
    hand: list[Card] = field(default_factory=list)
    card_stack: list[Card] = field(default_factory=list)
    has_passed: bool = False
    tichu_called: bool = False
    grand_tichu_called: bool = False
