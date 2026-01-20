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

    def __str__(self):
        return f"""Current Game State:
- Scores: {self.scores}
- Current combination: {self.current_combination}
- Winning Player Index: {self.winning_player_idx}
- Current wish: {self.current_wish}
- Card stack: {self.card_stack}
- Player rankings: {self.player_rankings}
"""
