from enum import Enum

from tichu.card import Card, Color, SpecialCard


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


PAIR_SIZE = 2
TRIPLE_SIZE = 3
BOMB_SIZE = 4
STRAIGHT_MIN_SIZE = 5
STAIR_SIZE = 2
FULL_HOUSE_LENGTH_KEY = 3
FULL_HOUSE_LENGTH_1 = 3
FULL_HOUSE_LENGTH_2 = 2


class Combination:
    def __init__(
        self, combination_type: CombinationType, value: int | float, length: int = 1
    ):
        self.combination_type = combination_type
        self.value = value
        self.length = length

    def __eq__(self, value):
        return (
            self.combination_type == value.combination_type
            and self.value == value.value
            and self.length == value.length
        )

    @classmethod
    def from_cards(cls, cards: list[Card]) -> "Combination | None":
        if len(cards) <= TRIPLE_SIZE and all(
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
        if len(cards) == BOMB_SIZE and all(
            card.value == cards[0].value for card in cards
        ):
            return cls(CombinationType.BOMB, cards[0].value)
        has_phoenix = SpecialCard.PHOENIX.value in ([card.value for card in cards])
        cards.sort(key=lambda c: c.value)
        card_count = Combination.get_card_count(cards)
        straight_values = sorted(card_count.keys())
        if (
            len(cards) >= STAIR_SIZE * 2
            and len(cards) % 2 == 0
            and (
                all(val == STAIR_SIZE for val in card_count.values())
                or (
                    len([val for val in card_count.values() if val == STAIR_SIZE])
                    == len(card_count) - 1
                    and len(
                        [val for val in card_count.values() if val == STAIR_SIZE - 1]
                    )
                    == 1
                    and has_phoenix
                )
            )
            and straight_values[-1] - straight_values[0] == len(card_count) - 1
        ):
            return cls(CombinationType.STAIR, max(card_count.keys()), len(cards) // 2)
        if len(straight_values) >= STRAIGHT_MIN_SIZE - 1 and all(
            val == 1 for val in card_count.values()
        ):
            if (
                straight_values[-1] - straight_values[0] == len(straight_values) - 1
                and len(straight_values) >= STRAIGHT_MIN_SIZE
            ):
                if all(
                    cards[i].color == cards[i + 1].color for i in range(len(cards) - 1)
                ):
                    return cls(
                        CombinationType.STRAIGHT_BOMB, cards[-1].value, len(cards)
                    )
                return cls(CombinationType.STRAIGHT, cards[-1].value, len(cards))
            if has_phoenix and (
                len(straight_values) - 1
                <= straight_values[-1] - straight_values[0]
                <= len(straight_values)
            ):
                return cls(
                    CombinationType.STRAIGHT,
                    min(14, cards[0].value + len(cards) - 1),
                    len(cards),
                )
        if len(cards) == FULL_HOUSE_LENGTH_1 + FULL_HOUSE_LENGTH_2 and (
            sorted(card_count.values()) == [2, 3]
            or (
                has_phoenix
                and (
                    sorted(card_count.values()) == [1, 3]
                    or sorted(card_count.values()) == [2, 2]
                )
            )
        ):
            return cls(
                CombinationType.FULL_HOUSE,
                next(
                    (
                        key
                        for key, val in card_count.items()
                        if val == FULL_HOUSE_LENGTH_1
                    ),
                    sorted(card_count.keys())[-1],
                ),
            )
        return None

    def can_be_played_on(self, other: "Combination") -> bool:
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
        length: int, wish_value: int, card_count: dict[int, int], *, has_phoenix: bool
    ) -> "Combination | None":
        straight_values = sorted(card_count.keys())
        for i in range(length - 1, -1, -1):
            window_start = max(0, wish_value - (length - 1) + i)
            window_end = min(wish_value + i, 14)
            window = [
                val for val in straight_values if window_start <= val <= window_end
            ]
            if len(window) == length or (len(window) == length - 1 and has_phoenix):
                return Combination(
                    CombinationType.STRAIGHT,
                    window_end,
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
        combination: "Combination | None", wish_value: int, cards: list[Card]
    ) -> bool:
        card_count = Combination.get_card_count(cards)
        wish_card_count = card_count.get(wish_value, 0)
        has_phoenix = SpecialCard.PHOENIX.value in [card.value for card in cards]
        next_combination = None
        if wish_card_count == 0:
            return False
        if combination is None:
            return True
        for color in Color:
            if color == Color.SPECIAL:
                continue
            cards_in_color = [card for card in cards if card.color == color]
            color_cards_count = Combination.get_card_count(cards_in_color)
            if (
                wish_value in color_cards_count
                and len(color_cards_count) >= STRAIGHT_MIN_SIZE
            ):
                next_combination = Combination.possible_wish_straight(
                    5, wish_value, color_cards_count, has_phoenix=False
                )
                if next_combination is not None:
                    next_combination.combination_type = CombinationType.STRAIGHT_BOMB
                    break
        if wish_card_count == BOMB_SIZE:
            next_combination = Combination(CombinationType.BOMB, wish_value)
        if next_combination is None:
            match combination.combination_type:
                case CombinationType.SINGLE:
                    next_combination = Combination(CombinationType.SINGLE, wish_value)
                case CombinationType.PAIR:
                    if wish_card_count >= PAIR_SIZE or (
                        wish_card_count == PAIR_SIZE - 1 and has_phoenix
                    ):
                        next_combination = Combination(CombinationType.PAIR, wish_value)
                case CombinationType.TRIPLE:
                    if wish_card_count >= TRIPLE_SIZE or (
                        wish_card_count == TRIPLE_SIZE - 1 and has_phoenix
                    ):
                        next_combination = Combination(
                            CombinationType.TRIPLE, wish_value
                        )
                case CombinationType.STRAIGHT:
                    next_combination = Combination.possible_wish_straight(
                        combination.length,
                        wish_value,
                        card_count,
                        has_phoenix=has_phoenix,
                    )
                case CombinationType.FULL_HOUSE:
                    if (
                        FULL_HOUSE_LENGTH_2 - int(has_phoenix)
                    ) <= wish_card_count <= FULL_HOUSE_LENGTH_1 and (
                        min(
                            FULL_HOUSE_LENGTH_1,
                            (FULL_HOUSE_LENGTH_1 + FULL_HOUSE_LENGTH_2)
                            - int(has_phoenix)
                            - wish_card_count,
                        )
                    ) in card_count.values():
                        next_combination = Combination(
                            CombinationType.FULL_HOUSE,
                            next(
                                (
                                    key
                                    for key, val in card_count.items()
                                    if val == FULL_HOUSE_LENGTH_KEY
                                ),
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

                        if len(
                            [count for count in straight_counts if count == STAIR_SIZE]
                        ) == combination.length - 1 or (
                            len(
                                [
                                    count
                                    for count in straight_counts
                                    if count == STAIR_SIZE
                                ]
                            )
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

    @staticmethod
    def possible_plays(
        combination: Combination | None,
        cards: list[Card],
    ) -> list[Combination]:
        min_value = round(combination.value) if combination else 0
        card_count = Combination.get_card_count(cards)
        has_phoenix = SpecialCard.PHOENIX.value in [card.value for card in cards]
        has_dragon = SpecialCard.DRAGON.value in [card.value for card in cards]
        has_dog = SpecialCard.DOG.value in [card.value for card in cards]
        possible_combinations: list[Combination] = []

        if (
            combination is None
            or combination.combination_type == CombinationType.SINGLE
        ):
            possible_combinations.extend(
                [
                    Combination(CombinationType.SINGLE, value)
                    for value in card_count.keys()
                    if value > min_value
                ]
            )
            if has_phoenix and min_value < SpecialCard.DRAGON.value:
                possible_combinations.append(
                    Combination(
                        CombinationType.SINGLE,
                        (0 if combination is None else combination.value) + 0.5,
                    )
                )
            if has_dragon:
                possible_combinations.append(
                    Combination(CombinationType.SINGLE, SpecialCard.DRAGON.value)
                )
            if has_dog and min_value == 0:
                possible_combinations.append(
                    Combination(CombinationType.SINGLE, SpecialCard.DOG.value)
                )

        if combination is None or combination.combination_type == CombinationType.PAIR:
            possible_combinations.extend(
                [
                    Combination(CombinationType.PAIR, value)
                    for value, count in card_count.items()
                    if (count >= 2 or (count >= 1 and has_phoenix))
                    and value > min_value
                ]
            )
        if (
            combination is None
            or combination.combination_type == CombinationType.TRIPLE
        ):
            possible_combinations.extend(
                [
                    Combination(CombinationType.TRIPLE, value)
                    for value, count in card_count.items()
                    if (count >= 3 or (count >= 2 and has_phoenix))
                    and value > min_value
                ]
            )
        if (
            combination is not None
            and combination.combination_type is not CombinationType.STRAIGHT_BOMB
        ):
            possible_combinations.extend(
                [
                    Combination(CombinationType.BOMB, value)
                    for value, count in card_count.items()
                    if count == 4
                    and (
                        combination.combination_type != CombinationType.BOMB
                        or value > min_value
                    )
                ]
            )
        if (
            combination is None
            or combination.combination_type == CombinationType.STRAIGHT
        ):
            straight_values = sorted(card_count.keys())
            for length in range(
                combination.length if combination else STRAIGHT_MIN_SIZE,
                combination.length + 1 if combination else 14,
            ):
                for i in range(14, max(min_value, length) - 1, -1):
                    window_start = i - (length - 1)
                    window_end = i
                    window = [
                        val
                        for val in straight_values
                        if window_start <= val <= window_end
                    ]
                    if len(window) == length or (
                        len(window) == length - 1 and has_phoenix
                    ):
                        possible_combinations.append(
                            Combination(
                                CombinationType.STRAIGHT,
                                window_end,
                                length,
                            )
                        )

        return possible_combinations
