from enum import Enum

NORMAL_CARD_VALUES = range(2, 15)
SPECIAL_CARD_VALUES = [0, 1, 15, 16]

class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    SPECIAL = 4

class SpecialCard(Enum):
    DOG = 0
    MAH_JONG = 1
    PHOENIX = 15
    DRAGON = 16

class Card:
    def __init__(self, color: Color, value: int):
        self.color = color
        if color != Color.SPECIAL and value not in NORMAL_CARD_VALUES:
            raise ValueError("Card value for normal cards must be between 2 and 14.")
        if color == Color.SPECIAL and value not in SPECIAL_CARD_VALUES:
            raise ValueError("Special cards can only have values 0 (Dog), 1, 15 (Phoenix), or 16 (Dragon).")
        self.value = value

    def __str__(self):
        if self.color == Color.SPECIAL:
            return SpecialCard(self.value).name
        return f"{self.color.name}  {self.value}"

    def __repr__(self):
        return f"Card(color={self.color}, value={self.value})"
