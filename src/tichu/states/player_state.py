from dataclasses import dataclass, field

from tichu.card import Card


class Hand(set[Card]):
    """Represent a player's hand with candidate cards and a logical hand length.

    Parameters:
        cards: Cards visible as possible hand contents.
        length: The logical number of cards in the hand.
    Returns:
        None.
    Exceptions raised:
        None.
    """

    def __init__(self, cards: set[Card] | None = None, length: int | None = None):
        cards = cards or set()
        super().__init__(cards)
        self.length = len(cards) if length is None else length

    def __len__(self) -> int:
        """Return the logical hand length.

        Parameters:
            None.
        Returns:
            int: The logical number of cards in the hand.
        Exceptions raised:
            None.
        """
        return self.length

    def add(self, element: Card) -> None:
        """Add a card and increase logical length when it was not already present.

        Parameters:
            element: The card to add.
        Returns:
            None.
        Exceptions raised:
            None.
        """
        if element not in self:
            self.length += 1
        super().add(element)

    def remove(self, element: Card) -> None:
        """Remove a card and decrease logical length.

        Parameters:
            element: The card to remove.
        Returns:
            None.
        Exceptions raised:
            KeyError: If the card is not present.
        """
        super().remove(element)
        self.length -= 1

    def discard(self, element: Card) -> None:
        """Discard a card and decrease logical length when it was present.

        Parameters:
            element: The card to discard.
        Returns:
            None.
        Exceptions raised:
            None.
        """
        if element in self:
            self.length -= 1
        super().discard(element)

    def pop(self) -> Card:
        """Remove and return an arbitrary card while decreasing logical length.

        Parameters:
            None.
        Returns:
            Card: The removed card.
        Exceptions raised:
            KeyError: If the hand has no visible cards.
        """
        card = super().pop()
        self.length -= 1
        return card

    def clear(self) -> None:
        """Remove all cards and reset logical length to zero.

        Parameters:
            None.
        Returns:
            None.
        Exceptions raised:
            None.
        """
        super().clear()
        self.length = 0

    def copy(self) -> "Hand":
        """Copy the hand while preserving logical length.

        Parameters:
            None.
        Returns:
            Hand: A copy with the same visible cards and logical length.
        Exceptions raised:
            None.
        """
        return Hand(set(self), self.length)


@dataclass
class PlayerState:
    hand: Hand = field(default_factory=Hand)
    card_stack: set[Card] = field(default_factory=set)
    has_passed: bool = False
    tichu_called: bool = False
    grand_tichu_called: bool = False
    push_selection: set[int] = field(default_factory=set)

    def __setattr__(self, name: str, value):
        """Convert assigned hand sets to Hand instances.

        Parameters:
            name: The attribute name being assigned.
            value: The value being assigned.
        Returns:
            None.
        Exceptions raised:
            None.
        """
        if name == "hand" and not isinstance(value, Hand):
            value = Hand(set(value))
        super().__setattr__(name, value)

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
