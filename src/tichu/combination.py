from collections import defaultdict
from enum import Enum
from functools import reduce
from itertools import combinations

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

    def __hash__(self):
        return hash((self.combination_type, self.value, self.length))

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
        straight_values = sorted(card_count.keys())
        wish_card_count = card_count.get(wish_value, 0)
        has_phoenix = SpecialCard.PHOENIX.value in [card.value for card in cards]
        next_combination = None
        if wish_card_count == 0:
            return False
        if combination is None:
            return True

        length = (
            combination.length
            if combination.combination_type == CombinationType.STRAIGHT_BOMB
            else 5
        )
        for i in range(length - 1, -1, -1):
            window_start = max(0, wish_value - (length - 1) + i)
            window_end = min(wish_value + i, 14)
            window = [
                val for val in straight_values if window_start <= val <= window_end
            ]
            if len(window) == length:
                possible_cards = [
                    card for card in cards if window_start <= card.value <= window_end
                ]
                card_buckets: dict[int, set[Color]] = defaultdict(set)
                for card in possible_cards:
                    card_buckets[card.value].add(card.color)
                colors = reduce(
                    lambda x, y: x.intersection(y),
                    list(card_buckets.values()),
                    set(Color),
                )
                if len(colors) > 0:
                    next_combination = Combination(
                        CombinationType.STRAIGHT_BOMB,
                        window_end,
                        length,
                    )

        if next_combination is None and wish_card_count == BOMB_SIZE:
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
                case CombinationType.STRAIGHT:
                    length = combination.length
                    for i in range(length - 1, -1, -1):
                        window_start = max(0, wish_value - (length - 1) + i)
                        window_end = min(wish_value + i, 14)
                        window = [
                            val
                            for val in straight_values
                            if window_start <= val <= window_end
                        ]
                        if len(window) == length or (
                            len(window) == length - 1 and has_phoenix
                        ):
                            next_combination = Combination(
                                CombinationType.STRAIGHT,
                                window_end,
                                length,
                            )
                            break
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
        combination: "Combination | None",
        cards: list[Card],
    ) -> list[set[Card]]:
        min_value = round(combination.value + 1) if combination else 0
        card_count = Combination.get_card_count(cards)
        card_buckets: dict[int, set[Card]] = defaultdict(set)
        for card in cards:
            if card.color != Color.SPECIAL or card.value == SpecialCard.MAH_JONG.value:
                card_buckets[card.value].add(card)
        has_phoenix = SpecialCard.PHOENIX.value in [card.value for card in cards]
        phoenix_card = Card(Color.SPECIAL, SpecialCard.PHOENIX.value)
        has_dragon = SpecialCard.DRAGON.value in [card.value for card in cards]
        has_dog = SpecialCard.DOG.value in [card.value for card in cards]
        possible_combinations: list[set[Card]] = []

        if (
            combination is None
            or combination.combination_type == CombinationType.SINGLE
        ):
            for value in card_buckets.keys():
                if value >= min_value:
                    possible_combinations.extend(
                        [{card} for card in card_buckets[value]]
                    )
            if has_phoenix and min_value < SpecialCard.DRAGON.value:
                possible_combinations.append(
                    {Card(Color.SPECIAL, SpecialCard.PHOENIX.value)}
                )
            if has_dragon:
                possible_combinations.append(
                    {Card(Color.SPECIAL, SpecialCard.DRAGON.value)}
                )
            if has_dog and min_value == 0:
                possible_combinations.append(
                    {Card(Color.SPECIAL, SpecialCard.DOG.value)}
                )

        if combination is None or combination.combination_type == CombinationType.PAIR:
            for value in card_buckets.keys():
                if value >= min_value:
                    if len(card_buckets[value]) >= 2:
                        possible_combinations.extend(
                            [
                                set(combo)
                                for combo in combinations(card_buckets[value], 2)
                            ]
                        )
                    elif len(card_buckets[value]) == 1 and has_phoenix:
                        possible_combinations.extend(
                            [
                                set(combo) | {phoenix_card}
                                for combo in combinations(card_buckets[value], 1)
                            ]
                        )
        if (
            combination is None
            or combination.combination_type == CombinationType.TRIPLE
        ):
            for value in card_buckets.keys():
                if value >= min_value:
                    if len(card_buckets[value]) >= 3:
                        possible_combinations.extend(
                            [
                                set(combo)
                                for combo in combinations(card_buckets[value], 3)
                            ]
                        )
                    elif len(card_buckets[value]) == 2 and has_phoenix:
                        possible_combinations.extend(
                            [
                                set(combo) | {phoenix_card}
                                for combo in combinations(card_buckets[value], 2)
                            ]
                        )
        if (
            combination is None
            or combination.combination_type is not CombinationType.STRAIGHT_BOMB
        ):
            for value in card_buckets.keys():
                if value >= min_value:
                    if len(card_buckets[value]) >= 4:
                        possible_combinations.extend(
                            [
                                set(combo)
                                for combo in combinations(card_buckets[value], 4)
                            ]
                        )
        if (
            combination is None
            or combination.combination_type == CombinationType.STRAIGHT
        ):
            straight_values = sorted(card_buckets.keys())
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

                        straight_plays: list[set[Card]] = []
                        for val in range(window_start, window_end + 1):
                            new_plays = []
                            for card in card_buckets[val]:
                                new_plays.extend(
                                    [
                                        play | {card}
                                        for play in (
                                            straight_plays
                                            if len(straight_plays) > 0
                                            else [set()]
                                        )
                                    ]
                                )
                            if len(card_buckets[val]) == 0:
                                new_plays.extend(
                                    [
                                        play | {phoenix_card}
                                        for play in (
                                            straight_plays
                                            if len(straight_plays) > 0
                                            else [set()]
                                        )
                                    ]
                                )
                            if has_phoenix and len(window) == length:
                                new_plays.extend(
                                    [
                                        play | {phoenix_card}
                                        for play in (
                                            straight_plays
                                            if len(straight_plays) > 0
                                            else [set()]
                                        )
                                        if phoenix_card not in play
                                    ]
                                )
                            straight_plays = new_plays
                        possible_combinations.extend(straight_plays)
        if (
            combination is None
            or combination.combination_type == CombinationType.FULL_HOUSE
        ):
            triple_combos = {
                val: [set(combo) for combo in combinations(bucket, 3)]
                for val, bucket in card_buckets.items()
                if len(bucket) >= 3
            }
            pair_combos = {
                val: [set(combo) for combo in combinations(bucket, 2)]
                for val, bucket in card_buckets.items()
                if len(bucket) >= 2
            }
            single_combos = {
                val: [{card} for card in bucket]
                for val, bucket in card_buckets.items()
                if len(bucket) >= 1
            }

            for triple_val, triple_combo in triple_combos.items():
                for pair_val, pair_combo in pair_combos.items():
                    if triple_val != pair_val:
                        possible_combinations.extend(
                            [
                                triple | pair
                                for triple in triple_combo
                                for pair in pair_combo
                            ]
                        )
                if has_phoenix:
                    for single_val, single_combo in single_combos.items():
                        if triple_val != single_val:
                            possible_combinations.extend(
                                [
                                    triple | single | {phoenix_card}
                                    for triple in triple_combo
                                    for single in single_combo
                                ]
                            )
            if has_phoenix:
                for pair_val, pair_combo in pair_combos.items():
                    for pair_val_2, pair_combo_2 in pair_combos.items():
                        if pair_val > pair_val_2:
                            possible_combinations.extend(
                                [
                                    pair | pair_2 | {phoenix_card}
                                    for pair in pair_combo
                                    for pair_2 in pair_combo_2
                                ]
                            )

        return possible_combinations
