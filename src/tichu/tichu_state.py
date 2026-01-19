from dataclasses import dataclass, field
from tichu.card import Card
from tichu.combination import Combination


@dataclass
class TichuState:
    scores: list[int] = field(default_factory=lambda: [0, 0])
    current_round: int = 0
    current_player_idx: int = 0
    winning_player_idx: int = 0
    current_combination: Combination | None = None
    current_wish: int | None = None
    card_stack: list[Card] = field(default_factory=list)
    player_rankings: list[int] = field(default_factory=list)
