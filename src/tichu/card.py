from enum import Enum
from functools import reduce
from typing import Iterable

NORMAL_CARD_VALUES = range(2, 15)
SPECIAL_CARD_VALUES = [0, 1, 50, 100]


class Color(Enum):
    JADE = 0
    SWORDS = 1
    PAGODE = 2
    STAR = 3
    SPECIAL = 4


class Card:
    def __init__(self, color: Color, value: int):
        self.color = color
        if color != Color.SPECIAL and value not in NORMAL_CARD_VALUES:
            msg = "Card value for normal cards must be between 2 and 14."
            raise ValueError(msg)
        if color == Color.SPECIAL and value not in SPECIAL_CARD_VALUES:
            msg = "Special cards can only have values 0 (Dog), 1, 50 (Phoenix), or 100 (Dragon)."
            raise ValueError(msg)
        self.value = value

    def get_score(self) -> int:
        match self.value:
            case 50:
                return -25
            case 100:
                return 25
            case 5:
                return 5
            case 10 | 13:
                return 10
            case _:
                return 0

    @staticmethod
    def count_card_scores(cards: Iterable["Card"]) -> int:
        return reduce(lambda total, card: total + card.get_score(), cards, 0)

    def __str__(self):
        match self.value:
            case 0:
                return "Dog"
            case 1:
                return "Mah Jong"
            case 50:
                return "Phoenix"
            case 100:
                return "Dragon"
            case 11:
                return f"{self.color.name} Jack"
            case 12:
                return f"{self.color.name} Queen"
            case 13:
                return f"{self.color.name} King"
            case 14:
                return f"{self.color.name} Ace"
            case _:
                return f"{self.color.name} {self.value}"

    def __repr__(self):
        return f"Card(color={self.color}, value={self.value})"

    def __eq__(self, value):
        return self.color == value.color and self.value == value.value

    def __hash__(self):
        return hash((self.color, self.value))


DOG = Card(Color.SPECIAL, 0)
MAH_JONG = Card(Color.SPECIAL, 1)
PHOENIX = Card(Color.SPECIAL, 50)
DRAGON = Card(Color.SPECIAL, 100)


def build_full_deck() -> list[Card]:
    """Build a full Tichu deck containing all standard and special cards.

    Parameters:
        None.
    Returns:
        list[Card]: A list with 56 cards including all four special cards.
    Exceptions raised:
        None.
    """
    deck = [
        Card(color, value)
        for color in Color
        if color != Color.SPECIAL
        for value in NORMAL_CARD_VALUES
    ]
    deck.extend([DOG, MAH_JONG, PHOENIX, DRAGON])
    return deck
