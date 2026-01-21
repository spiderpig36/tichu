from enum import Enum
from functools import reduce

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
        if self.color == Color.SPECIAL:
            match self:
                case SpecialCard.DOG.value:
                    return 0
                case SpecialCard.PHOENIX.value:
                    return -25
                case SpecialCard.DRAGON.value:
                    return 25
        else:
            match self.value:
                case 5:
                    return 5
                case 10 | 13:
                    return 10
        return 0

    @staticmethod
    def count_card_scores(cards: list["Card"]) -> int:
        return reduce(lambda total, card: total + card.get_score(), cards, 0)

    def __str__(self):
        if self.color == Color.SPECIAL:
            return str(SpecialCard(self))
        match self.value:
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


class SpecialCard(Enum):
    DOG = Card(color=Color.SPECIAL, value=0)
    MAH_JONG = Card(color=Color.SPECIAL, value=1)
    PHOENIX = Card(color=Color.SPECIAL, value=50)
    DRAGON = Card(color=Color.SPECIAL, value=100)

    def __str__(self):
        return self.name
