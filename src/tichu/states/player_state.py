from dataclasses import dataclass, field

from tichu.card import Card


@dataclass
class PlayerState:
    hand: set[Card] = field(default_factory=set)
    card_stack: set[Card] = field(default_factory=set)
    has_passed: bool = False
    tichu_called: bool = False
    grand_tichu_called: bool = False
    push_selection: set[int] = field(default_factory=set)

    def get_sorted_hand(self) -> list[Card]:
        """Get the hand as a sorted list for deterministic index-based access.

        Parameters:
            None.
        Returns:
            list[Card]: Cards sorted by value and color.
        Exceptions raised:
            None.
        """
        return sorted(self.hand, key=lambda card: (card.value, card.color.value))

    def __str__(self):
        hand_str = "\n".join(
            f"\t{i}: {card}" for i, card in enumerate(self.get_sorted_hand())
        )
        card_stack_str = ", ".join(
            str(card) for card in sorted(self.card_stack, key=lambda card: card.value)
        )
        return f"""Player State:
- Hand: 
{hand_str}
- Card Stack: {card_stack_str}
- Has Passed: {self.has_passed}
- Tichu Called: {self.tichu_called}
- Grand Tichu Called: {self.grand_tichu_called}"""
