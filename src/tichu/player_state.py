from dataclasses import dataclass, field

from tichu.card import Card


@dataclass
class PlayerState:
    hand: list[Card] = field(default_factory=list)
    card_stack: list[Card] = field(default_factory=list)
    has_passed: bool = False
    tichu_called: bool = False
    grand_tichu_called: bool = False
    push_selection: set[int] = field(default_factory=set)

    def __str__(self):
        hand_str = "\n".join(f"\t{i}: {card}" for i, card in enumerate(self.hand))
        card_stack_str = ", ".join(str(card) for card in self.card_stack)
        return f"""Player State:
- Hand: 
{hand_str}
- Card Stack: {card_stack_str}
- Has Passed: {self.has_passed}
- Tichu Called: {self.tichu_called}
- Grand Tichu Called: {self.grand_tichu_called}"""
