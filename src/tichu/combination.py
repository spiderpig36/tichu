
from enum import Enum
from typing import Optional

from .card import Card, Color, SpecialCard

class InvalidCombinationError(Exception):
    pass

class CombinationType(Enum):
    SINGLE = 0
    PAIR = 1
    TRIPLE = 2
    STAIR = 3
    FULL_HOUSE = 4
    STRAIGHT = 5
    BOMB = 6
    STRAIGHT_BOMB = 7

class Combination():
    @classmethod
    def from_cards(cls, cards: list[Card]) -> Optional["Combination"]:
        if len(cards) <= 3 and all(card.value == cards[0].value or card.value == SpecialCard.PHOENIX.value for card in cards) :
            match len(cards):
                case 1:
                    return cls(CombinationType.SINGLE, cards[0].value)
                case 2:
                    return cls(CombinationType.PAIR, cards[0].value)
                case 3:
                    return cls(CombinationType.TRIPLE, cards[0].value)
        if any([card for card in cards if card.value == SpecialCard.DOG.value]):
            raise InvalidCombinationError("Dog cannot be played in combinations.")
        if any([card for card in cards if card.value == SpecialCard.DRAGON.value]):
            raise InvalidCombinationError("Dragon cannot be played in combinations.")
        if len(cards) == 4 and all(card.value == cards[0].value for card in cards):
                return cls(CombinationType.BOMB, cards[0].value)
        cards.sort(key=lambda c: c.value)
        if len(cards) >= 5:
            if cards[-1].value - cards[0].value == len(cards) - 1:
                if all(cards[i].color == cards[i + 1].color for i in range(len(cards) - 1)):
                    return cls(CombinationType.STRAIGHT_BOMB, cards[-1].value, len(cards))
                return cls(CombinationType.STRAIGHT, cards[-1].value, len(cards))
            if cards[-2].value - cards[0].value == len(cards) - 1 and cards[-1].value == SpecialCard.PHOENIX.value:
                return cls(CombinationType.STRAIGHT, cards[-2].value, len(cards))
            if cards[-2].value - cards[0].value == len(cards) - 2 and cards[-1].value == SpecialCard.PHOENIX.value:
                if cards[-2].value == 14:
                    return cls(CombinationType.STRAIGHT, cards[-2].value, len(cards))
                return cls(CombinationType.STRAIGHT, cards[-2].value + 1, len(cards))
        if len(cards) >= 4 and len(cards) % 2 == 0:
            is_stair = True
            for i in range(0, len(cards), 2):
                if cards[i].value != cards[i + 1].value:
                    is_stair = False
                    break
                if i > 0 and cards[i].value != cards[i - 2].value + 1:
                    is_stair = False
                    break
            if is_stair:
                return cls(CombinationType.STAIR, cards[-1].value, len(cards) // 2)
        if len(cards) == 5:
            values: dict[int, int] = {}
            for card in cards:
                values[card.value] = values.get(card.value, 0) + 1
            if any([card for card in cards if card.value == SpecialCard.PHOENIX.value]):
                del values[SpecialCard.PHOENIX.value]
                to_add = next((key for key, val in sorted(values.items(), key=lambda item: item[0], reverse=True) if val == 2), -1)
                if to_add != -1:
                    values[to_add] += 1
            if sorted(values.values()) == [2, 3]:
                return cls(CombinationType.FULL_HOUSE, next(key for key, val in values.items() if val == 3))
        raise InvalidCombinationError("Invalid combination of cards.")

    def __init__(self, combination_type: CombinationType, value: int, length: int = 1):
        self.combination_type = combination_type
        self.value = value
        self.length = length
