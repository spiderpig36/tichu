from enum import Enum
from functools import reduce

NORMAL_CARD_VALUES = range(2, 15)


class Color(Enum):
    JADE = 0
    SWORD = 1
    PAGODE = 2
    STAR = 3
    SPECIAL = 4


class SpecialCard(Enum):
    DOG = 0
    MAH_JONG = 1
    PHOENIX = 50
    DRAGON = 100

    @staticmethod
    def values() -> list[int]:
        return [card.value for card in SpecialCard]


class Card:
    def __init__(self, color: Color, value: int):
        self.color = color
        if color != Color.SPECIAL and value not in NORMAL_CARD_VALUES:
            msg = "Card value for normal cards must be between 2 and 14."
            raise ValueError(msg)
        if color == Color.SPECIAL and value not in SpecialCard.values():
            msg = "Special cards can only have values 0 (Dog), 1, 15 (Phoenix), or 16 (Dragon)."
            raise ValueError(msg)
        self.value = value

    def get_score(self) -> int:
        match self.value:
            case SpecialCard.DOG.value:
                return 0
            case SpecialCard.PHOENIX.value:
                return -25
            case SpecialCard.DRAGON.value:
                return 25
            case 5:
                return 5
            case 10 | 13:
                return 10
            case _:
                return 0

    @staticmethod
    def count_card_scores(cards: list["Card"]) -> int:
        return reduce(lambda total, card: total + card.get_score(), cards, 0)

    def __str__(self):
        if self.color == Color.SPECIAL:
            return SpecialCard(self.value).name
        return f"{self.color.name}  {self.value}"

    def __repr__(self):
        return f"Card(color={self.color}, value={self.value})"

    def __eq__(self, value):
        return self.color == value.color and self.value == value.value

    def __hash__(self):
        return hash((self.color, self.value))
