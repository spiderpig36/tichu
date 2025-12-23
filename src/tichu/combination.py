from enum import Enum
from .card import Card, Color, SpecialCard

class CombinationType(Enum):
    SINGLE = 0
    PAIR = 1
    TRIPLE = 2
    STAIR = 3
    FULL_HOUSE = 4
    STRAIGHT = 5
    BOMB = 6
    STRAIGHT_BOMB = 7

    def get_bomb_strength(self, length: int) -> int:
        match self:
            case CombinationType.BOMB:
                return 1
            case CombinationType.STRAIGHT_BOMB:
                return 2 + length
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
        card_count: dict[int, int] = {}
        for card in cards:
            if card.color != Color.SPECIAL:
                card_count[card.value] = card_count.get(card.value, 0) + 1
        if len(cards) >= 4 and len(cards) % 2 == 0:
            straight_values = sorted(card_count.keys())
            if (all(val == 2 for val in card_count.values()) or (len([val for val in card_count.values() if val == 2]) == len(card_count) - 1 and len([val for val in card_count.values() if val == 1]) == 1 and any([card for card in cards if card.value == SpecialCard.PHOENIX.value]))) and straight_values[-1] - straight_values[0] == len(card_count) - 1:
                return cls(CombinationType.STAIR, max(card_count.keys()), len(cards) // 2)
        if len(cards) == 5:
            if sorted(card_count.values()) == [2, 3] or (any([card for card in cards if card.value == SpecialCard.PHOENIX.value]) and (sorted(card_count.values()) == [1, 3] or sorted(card_count.values()) == [2, 2])):
                return cls(CombinationType.FULL_HOUSE, next((key for key, val in card_count.items() if val == 3), sorted(card_count.keys())[-1]))
        return None

    def can_be_played_on(self, other: Combination) -> bool:
        return (other.combination_type == self.combination_type and other.length == self.length and self.value > other.value) or self.combination_type.get_bomb_strength(other.length) > other.combination_type.get_bomb_strength(self.length)
    
    @staticmethod
    def can_fulfill_wish(combination: Combination, wish_value: int, cards: list[Card]) -> bool:
        card_count: dict[int, int] = {}
        for card in cards:
            card_count[card.value] = card_count.get(card.value, 0) + 1
        next_combination = None
        match combination.combination_type:
            case CombinationType.SINGLE:
                if wish_value in card_count:
                    next_combination = Combination.from_cards([card for card in cards if card.value == wish_value])
            case CombinationType.PAIR:
                if card_count.get(wish_value, 0) >= 2 or (card_count.get(wish_value, 0) == 1 and card_count.get(SpecialCard.PHOENIX.value, 0) >= 1):
                    next_combination = Combination.from_cards([card for card in cards if card.value == wish_value])
            case CombinationType.TRIPLE:
                if card_count.get(wish_value, 0) >= 3 or (card_count.get(wish_value, 0) == 2 and card_count.get(SpecialCard.PHOENIX.value, 0) >= 1):
                    next_combination = Combination.from_cards([card for card in cards if card.value == wish_value])
            case CombinationType.BOMB:
                if card_count.get(wish_value, 0) == 4:
                    next_combination = Combination.from_cards([card for card in cards if card.value == wish_value])
            case CombinationType.STRAIGHT:
                pass
            case CombinationType.FULL_HOUSE:
                pass
            case CombinationType.STAIR:
                pass
            case CombinationType.STRAIGHT_BOMB:
                pass
        return next_combination is not None and next_combination.can_be_played_on(combination)

    def __init__(self, combination_type: CombinationType, value: int, length: int = 1):
        self.combination_type = combination_type
        self.value = value
        self.length = length
