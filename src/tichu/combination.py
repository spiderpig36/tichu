from enum import Enum

from .card import Card, SpecialCard

class CombinationType(Enum):
    SINGLE = 0
    PAIR = 1
    TRIPLE = 2
    STAIR = 3
    FULL_HOUSE = 4
    STRAIGHT = 5
    BOMB = 6
    STRAIGHT_BOMB = 7

    def get_bomb_strength(self):
        match self:
            case CombinationType.BOMB:
                return 1
            case CombinationType.STRAIGHT_BOMB:
                return 2
            case _:
                return 0

class Combination():
    @classmethod
    def from_cards(cls, cards: list[Card]) -> Combination | None:
        if len(cards) <= 3 and all(card.value == cards[0].value or card.value == SpecialCard.PHOENIX.value for card in cards) :
            match len(cards):
                case 1:
                    return cls(CombinationType.SINGLE, cards[0].value)
                case 2:
                    return cls(CombinationType.PAIR, cards[0].value)
                case 3:
                    return cls(CombinationType.TRIPLE, cards[0].value)
        if len(cards) == 4 and all(card.value == cards[0].value for card in cards):
                return cls(CombinationType.BOMB, cards[0].value)
        cards.sort(key=lambda c: c.value)
        if len(cards) >= 5:
            if cards[-1].value - cards[0].value == len(cards) - 1:
                if all(cards[i].color == cards[i + 1].color for i in range(len(cards) - 1)):
                    return cls(CombinationType.STRAIGHT_BOMB, cards[-1].value, len(cards))
                return cls(CombinationType.STRAIGHT, cards[-1].value, len(cards))
            if cards[-1].value == SpecialCard.PHOENIX.value:
                if cards[-2].value - cards[0].value == len(cards) - 1:
                    return cls(CombinationType.STRAIGHT, cards[-2].value, len(cards))
                if cards[-2].value - cards[0].value == len(cards) - 2:
                    if cards[-2].value == 14:
                        return cls(CombinationType.STRAIGHT, cards[-2].value, len(cards))
                    return cls(CombinationType.STRAIGHT, cards[-2].value + 1, len(cards))
        if len(cards) >= 4 and len(cards) % 2 == 0:
            card_count: dict[int, int] = {}
            for card in cards:
                card_count[card.value] = card_count.get(card.value, 0) + 1
            if any([card for card in cards if card.value == SpecialCard.PHOENIX.value]):
                del card_count[SpecialCard.PHOENIX.value]
                to_add = next((key for key, val in card_count.items() if val == 1), -1)
                if to_add != -1:
                    card_count[to_add] += 1
            straight_values = sorted(card_count.keys())
            if all(val == 2 for val in card_count.values()) and straight_values[-1] - straight_values[0] == len(card_count) - 1:
                return cls(CombinationType.STAIR, max(card_count.keys()), len(cards) // 2)
        if len(cards) == 5:
            card_count = {}
            for card in cards:
                card_count[card.value] = card_count.get(card.value, 0) + 1
            if any([card for card in cards if card.value == SpecialCard.PHOENIX.value]):
                del card_count[SpecialCard.PHOENIX.value]
                to_add = next((key for key, val in sorted(card_count.items(), key=lambda item: item[0], reverse=True) if val == 2), -1)
                if to_add != -1:
                    card_count[to_add] += 1
            if sorted(card_count.values()) == [2, 3]:
                return cls(CombinationType.FULL_HOUSE, next(key for key, val in card_count.items() if val == 3))
        return None

    def __init__(self, combination_type: CombinationType, value: int, length: int = 1):
        self.combination_type = combination_type
        self.value = value
        self.length = length
