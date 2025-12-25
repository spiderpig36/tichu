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


class Combination:
    def __init__(self, combination_type: CombinationType, value: int, length: int = 1):
        self.combination_type = combination_type
        self.value = value
        self.length = length

    @classmethod
    def from_cards(cls, cards: list[Card]) -> Combination | None:
        if len(cards) <= 3 and all(
            card.value == cards[0].value or card.value == SpecialCard.PHOENIX.value
            for card in cards
        ):
            match len(cards):
                case 1:
                    return cls(CombinationType.SINGLE, cards[0].value)
                case 2:
                    return cls(CombinationType.PAIR, cards[0].value)
                case 3:
                    return cls(CombinationType.TRIPLE, cards[0].value)
        if len(cards) == 4 and all(card.value == cards[0].value for card in cards):
            return cls(CombinationType.BOMB, cards[0].value)
        has_phoenix = SpecialCard.PHOENIX.value in ([card.value for card in cards])
        cards.sort(key=lambda c: c.value)
        card_count = Combination.get_card_count(cards)
        straight_values = sorted(card_count.keys())
        if len(cards) >= 4 and len(cards) % 2 == 0:
            if (
                all(val == 2 for val in card_count.values())
                or (
                    len([val for val in card_count.values() if val == 2])
                    == len(card_count) - 1
                    and len([val for val in card_count.values() if val == 1]) == 1
                    and has_phoenix
                )
            ) and straight_values[-1] - straight_values[0] == len(card_count) - 1:
                return cls(
                    CombinationType.STAIR, max(card_count.keys()), len(cards) // 2
                )
        if len(straight_values) >= 4 and all(val == 1 for val in card_count.values()):
            if (
                straight_values[-1] - straight_values[0] == len(straight_values) - 1
                and len(straight_values) >= 5
            ):
                if all(
                    cards[i].color == cards[i + 1].color for i in range(len(cards) - 1)
                ):
                    return cls(
                        CombinationType.STRAIGHT_BOMB, cards[-1].value, len(cards)
                    )
                return cls(CombinationType.STRAIGHT, cards[-1].value, len(cards))
            if has_phoenix:
                if (
                    len(straight_values) - 1
                    <= straight_values[-1] - straight_values[0]
                    <= len(straight_values)
                ):
                    return cls(
                        CombinationType.STRAIGHT,
                        min(14, cards[0].value + len(cards) - 1),
                        len(cards),
                    )
        if len(cards) == 5:
            if sorted(card_count.values()) == [2, 3] or (
                has_phoenix
                and (
                    sorted(card_count.values()) == [1, 3]
                    or sorted(card_count.values()) == [2, 2]
                )
            ):
                return cls(
                    CombinationType.FULL_HOUSE,
                    next(
                        (key for key, val in card_count.items() if val == 3),
                        sorted(card_count.keys())[-1],
                    ),
                )
        return None

    def can_be_played_on(self, other: Combination) -> bool:
        return (
            other.combination_type == self.combination_type
            and other.length == self.length
            and self.value > other.value
        ) or self.combination_type.get_bomb_strength(
            self.length
        ) > other.combination_type.get_bomb_strength(
            other.length
        )

    @staticmethod
    def possible_wish_straight(
        length: int, wish_value: int, card_count: dict[int, int], has_phoenix: bool
    ) -> Combination | None:
        straight_values = sorted(card_count.keys())
        for i in range(length - 1, -1, -1):
            window_start = max(0, wish_value - (length - 1) + i)
            window_end = min(wish_value + i, 14)
            window = [
                val for val in straight_values if window_start <= val <= window_end
            ]
            if len(window) == length or len(window) == length - 1 and has_phoenix:
                return Combination(
                    CombinationType.STRAIGHT,
                    (window_end if window_end in window else window_end + 1),
                    length,
                )
        return None

    @staticmethod
    def get_card_count(cards: list[Card]) -> dict[int, int]:
        card_count: dict[int, int] = {}
        for card in cards:
            if card.color != Color.SPECIAL or card.value == SpecialCard.MAH_JONG.value:
                card_count[card.value] = card_count.get(card.value, 0) + 1
        return card_count

    @staticmethod
    def can_fulfill_wish(
        combination: Combination, wish_value: int, cards: list[Card]
    ) -> bool:
        card_count = Combination.get_card_count(cards)
        wish_card_count = card_count.get(wish_value, 0)
        has_phoenix = SpecialCard.PHOENIX.value in [card.value for card in cards]
        next_combination = None
        if wish_card_count == 0:
            return False
        for color in Color:
            if color == Color.SPECIAL:
                continue
            cards_in_color = [card for card in cards if card.color == color]
            color_cards_count = Combination.get_card_count(cards_in_color)
            if wish_value in color_cards_count and len(color_cards_count) >= 5:
                next_combination = Combination.possible_wish_straight(
                    5, wish_value, color_cards_count, False
                )
                if next_combination is not None:
                    next_combination.combination_type = CombinationType.STRAIGHT_BOMB
                    break
        if wish_card_count == 4:
            next_combination = Combination(CombinationType.BOMB, wish_value)
        if next_combination is None:
            match combination.combination_type:
                case CombinationType.SINGLE:
                    next_combination = Combination(CombinationType.SINGLE, wish_value)
                case CombinationType.PAIR:
                    if wish_card_count >= 2 or (wish_card_count == 1 and has_phoenix):
                        next_combination = Combination(CombinationType.PAIR, wish_value)
                case CombinationType.TRIPLE:
                    if wish_card_count >= 3 or (wish_card_count == 2 and has_phoenix):
                        next_combination = Combination(
                            CombinationType.TRIPLE, wish_value
                        )
                case CombinationType.STRAIGHT:
                    next_combination = Combination.possible_wish_straight(
                        combination.length, wish_value, card_count, has_phoenix
                    )
                case CombinationType.FULL_HOUSE:
                    if (2 - int(has_phoenix)) <= wish_card_count <= 3 and (
                        min(3, 5 - int(has_phoenix) - wish_card_count)
                    ) in card_count.values():
                        next_combination = Combination(
                            CombinationType.FULL_HOUSE,
                            next(
                                (key for key, val in card_count.items() if val == 3),
                                sorted(card_count.keys())[-1],
                            ),
                        )
                case CombinationType.STAIR:
                    straight_items = sorted(card_count.items(), key=lambda i: i[0])
                    for i in range(combination.length, 0, -1):
                        window_start = max(0, wish_value - (combination.length - 1) + i)
                        window_end = min(wish_value + i, 14)
                        straight_counts = [
                            item[1]
                            for item in straight_items
                            if window_start <= item[0] <= window_end
                        ]

                        if (
                            len([count for count in straight_counts if count == 2])
                            == combination.length - 1
                            or len([count for count in straight_counts if count == 2])
                            == combination.length - 2
                            and has_phoenix
                        ):
                            next_combination = Combination(
                                CombinationType.STAIR,
                                window_end,
                                combination.length,
                            )
                            break
        return next_combination is not None and next_combination.can_be_played_on(
            combination
        )
