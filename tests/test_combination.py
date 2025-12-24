import pytest
from tichu.card import Card, Color, SpecialCard
from tichu.combination import Combination, CombinationType


@pytest.mark.parametrize(
    "cards, expected_type, expected_value, expected_length",
    [
        ([Card(Color.RED, 10)], CombinationType.SINGLE, 10, 1),
        ([Card(Color.RED, 5), Card(Color.GREEN, 5)], CombinationType.PAIR, 5, 1),
        (
            [Card(Color.RED, 8), Card(Color.SPECIAL, SpecialCard.PHOENIX.value)],
            CombinationType.PAIR,
            8,
            1,
        ),
        (
            [Card(Color.RED, 7), Card(Color.GREEN, 7), Card(Color.YELLOW, 7)],
            CombinationType.TRIPLE,
            7,
            1,
        ),
        (
            [
                Card(Color.RED, 12),
                Card(Color.GREEN, 12),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
            ],
            CombinationType.TRIPLE,
            12,
            1,
        ),
        (
            [
                Card(Color.RED, 6),
                Card(Color.RED, 3),
                Card(Color.GREEN, 4),
                Card(Color.YELLOW, 5),
                Card(Color.GREEN, 7),
            ],
            CombinationType.STRAIGHT,
            7,
            5,
        ),
        (
            [
                Card(Color.SPECIAL, SpecialCard.MAH_JONG.value),
                Card(Color.RED, 2),
                Card(Color.GREEN, 3),
                Card(Color.YELLOW, 4),
                Card(Color.GREEN, 5),
            ],
            CombinationType.STRAIGHT,
            5,
            5,
        ),
        (
            [
                Card(Color.RED, 6),
                Card(Color.RED, 2),
                Card(Color.RED, 3),
                Card(Color.GREEN, 4),
                Card(Color.YELLOW, 5),
                Card(Color.GREEN, 7),
            ],
            CombinationType.STRAIGHT,
            7,
            6,
        ),
        (
            [
                Card(Color.RED, 9),
                Card(Color.GREEN, 10),
                Card(Color.YELLOW, 11),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
                Card(Color.BLUE, 13),
            ],
            CombinationType.STRAIGHT,
            13,
            5,
        ),
        (
            [
                Card(Color.RED, 9),
                Card(Color.GREEN, 10),
                Card(Color.YELLOW, 11),
                Card(Color.BLUE, 12),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
            ],
            CombinationType.STRAIGHT,
            13,
            5,
        ),
        (
            [
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
                Card(Color.GREEN, 11),
                Card(Color.YELLOW, 12),
                Card(Color.BLUE, 13),
                Card(Color.RED, 14),
            ],
            CombinationType.STRAIGHT,
            14,
            5,
        ),
        (
            [
                Card(Color.RED, 2),
                Card(Color.BLUE, 2),
                Card(Color.GREEN, 4),
                Card(Color.YELLOW, 4),
                Card(Color.GREEN, 3),
                Card(Color.RED, 3),
            ],
            CombinationType.STAIR,
            4,
            3,
        ),
        (
            [
                Card(Color.GREEN, 4),
                Card(Color.YELLOW, 4),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
                Card(Color.RED, 3),
            ],
            CombinationType.STAIR,
            4,
            2,
        ),
        (
            [
                Card(Color.RED, 2),
                Card(Color.BLUE, 2),
                Card(Color.GREEN, 4),
                Card(Color.YELLOW, 4),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
                Card(Color.RED, 3),
            ],
            CombinationType.STAIR,
            4,
            3,
        ),
        (
            [
                Card(Color.RED, 9),
                Card(Color.GREEN, 9),
                Card(Color.YELLOW, 9),
                Card(Color.RED, 12),
                Card(Color.GREEN, 12),
            ],
            CombinationType.FULL_HOUSE,
            9,
            1,
        ),
        (
            [
                Card(Color.RED, 14),
                Card(Color.GREEN, 14),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
                Card(Color.RED, 2),
                Card(Color.GREEN, 2),
            ],
            CombinationType.FULL_HOUSE,
            14,
            1,
        ),
        (
            [
                Card(Color.RED, 14),
                Card(Color.GREEN, 14),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
                Card(Color.RED, 14),
                Card(Color.GREEN, 2),
            ],
            CombinationType.FULL_HOUSE,
            14,
            1,
        ),
        (
            [
                Card(Color.RED, 11),
                Card(Color.GREEN, 11),
                Card(Color.YELLOW, 11),
                Card(Color.BLUE, 11),
            ],
            CombinationType.BOMB,
            11,
            1,
        ),
        (
            [
                Card(Color.RED, 8),
                Card(Color.RED, 9),
                Card(Color.RED, 10),
                Card(Color.RED, 11),
                Card(Color.RED, 12),
            ],
            CombinationType.STRAIGHT_BOMB,
            12,
            5,
        ),
        (
            [
                Card(Color.RED, 3),
                Card(Color.RED, 4),
                Card(Color.GREEN, 5),
                Card(Color.RED, 6),
                Card(Color.RED, 7),
            ],
            CombinationType.STRAIGHT,
            7,
            5,
        ),
        (
            [
                Card(Color.RED, 10),
                Card(Color.RED, 11),
                Card(Color.RED, 12),
                Card(Color.RED, 13),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
            ],
            CombinationType.STRAIGHT,
            14,
            5,
        ),
    ],
)
def test_valid_combinations(cards, expected_type, expected_value, expected_length):
    combination = Combination.from_cards(cards)
    assert combination is not None
    assert combination.combination_type == expected_type
    assert combination.value == expected_value
    assert combination.length == expected_length


@pytest.mark.parametrize(
    "cards",
    [
        [Card(Color.RED, 8), Card(Color.GREEN, 9)],
        [Card(Color.RED, 10), Card(Color.GREEN, 10), Card(Color.YELLOW, 11)],
        [
            Card(Color.RED, 2),
            Card(Color.GREEN, 4),
            Card(Color.YELLOW, 5),
            Card(Color.BLUE, 6),
            Card(Color.RED, 7),
        ],
        [
            Card(Color.SPECIAL, SpecialCard.DOG.value),
            Card(Color.GREEN, 2),
            Card(Color.YELLOW, 3),
            Card(Color.BLUE, 4),
            Card(Color.RED, 5),
        ],
        [
            Card(Color.GREEN, 4),
            Card(Color.YELLOW, 5),
            Card(Color.BLUE, 6),
            Card(Color.RED, 7),
        ],
        [
            Card(Color.GREEN, 4),
            Card(Color.YELLOW, 5),
            Card(Color.YELLOW, 5),
            Card(Color.BLUE, 5),
            Card(Color.RED, 8),
        ],
        [
            Card(Color.GREEN, 4),
            Card(Color.YELLOW, 5),
            Card(Color.YELLOW, 5),
            Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
            Card(Color.RED, 8),
        ],
        [
            Card(Color.GREEN, 4),
            Card(Color.GREEN, 4),
            Card(Color.GREEN, 5),
            Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
            Card(Color.RED, 6),
        ],
        [
            Card(Color.RED, 13),
            Card(Color.GREEN, 13),
            Card(Color.YELLOW, 13),
            Card(Color.BLUE, 12),
        ],
        [
            Card(Color.RED, 14),
            Card(Color.GREEN, 14),
            Card(Color.YELLOW, 14),
            Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
        ],
        [
            Card(Color.RED, 2),
            Card(Color.BLUE, 2),
            Card(Color.GREEN, 4),
            Card(Color.YELLOW, 4),
            Card(Color.GREEN, 5),
            Card(Color.RED, 3),
        ],
        [Card(Color.SPECIAL, SpecialCard.DOG.value), Card(Color.GREEN, 2)],
        [Card(Color.SPECIAL, SpecialCard.DRAGON.value), Card(Color.GREEN, 14)],
    ],
)
def test_invalid_combinations(cards):
    combination = Combination.from_cards(cards)
    assert combination is None


@pytest.mark.parametrize(
    "played_type, played_value, played_length, current_type, current_value, current_length, expected",
    [
        # Single card beats single card (higher value)
        (CombinationType.SINGLE, 10, 1, CombinationType.SINGLE, 8, 1, True),
        (CombinationType.SINGLE, 5, 1, CombinationType.SINGLE, 10, 1, False),
        (CombinationType.SINGLE, 14, 1, CombinationType.SINGLE, 13, 1, True),
        # Pair beats pair (higher value)
        (CombinationType.PAIR, 12, 1, CombinationType.PAIR, 10, 1, True),
        (CombinationType.PAIR, 8, 1, CombinationType.PAIR, 9, 1, False),
        (CombinationType.PAIR, 14, 1, CombinationType.PAIR, 2, 1, True),
        # Triple beats triple (higher value)
        (CombinationType.TRIPLE, 7, 1, CombinationType.TRIPLE, 5, 1, True),
        (CombinationType.TRIPLE, 3, 1, CombinationType.TRIPLE, 7, 1, False),
        (CombinationType.TRIPLE, 13, 1, CombinationType.TRIPLE, 12, 1, True),
        # Straight beats straight (higher value, same length)
        (CombinationType.STRAIGHT, 10, 5, CombinationType.STRAIGHT, 8, 5, True),
        (CombinationType.STRAIGHT, 6, 5, CombinationType.STRAIGHT, 10, 5, False),
        (CombinationType.STRAIGHT, 9, 6, CombinationType.STRAIGHT, 7, 6, True),
        # Different lengths cannot be played on each other
        (CombinationType.STRAIGHT, 10, 5, CombinationType.STRAIGHT, 8, 6, False),
        (CombinationType.STRAIGHT, 12, 6, CombinationType.STRAIGHT, 10, 5, False),
        # Full house beats full house (higher value)
        (CombinationType.FULL_HOUSE, 10, 1, CombinationType.FULL_HOUSE, 8, 1, True),
        (CombinationType.FULL_HOUSE, 6, 1, CombinationType.FULL_HOUSE, 9, 1, False),
        # Stair beats stair (higher value, same length)
        (CombinationType.STAIR, 8, 3, CombinationType.STAIR, 6, 3, True),
        (CombinationType.STAIR, 5, 2, CombinationType.STAIR, 7, 2, False),
        (CombinationType.STAIR, 10, 4, CombinationType.STAIR, 8, 4, True),
        # Different combination types cannot beat each other (non-bombs)
        (CombinationType.PAIR, 14, 1, CombinationType.SINGLE, 2, 1, False),
        (CombinationType.TRIPLE, 14, 1, CombinationType.PAIR, 2, 1, False),
        (CombinationType.STRAIGHT, 14, 5, CombinationType.PAIR, 2, 1, False),
        (CombinationType.FULL_HOUSE, 14, 1, CombinationType.TRIPLE, 2, 1, False),
    ],
)
def test_can_be_played_on_same_types(
    played_type,
    played_value,
    played_length,
    current_type,
    current_value,
    current_length,
    expected,
):
    """Test that combinations of same type can be played if value is higher."""
    played_combo = Combination(played_type, played_value, played_length)
    current_combo = Combination(current_type, current_value, current_length)
    assert played_combo.can_be_played_on(current_combo) == expected


@pytest.mark.parametrize(
    "played_type, played_value, played_length, current_type, current_value, current_length, expected",
    [
        # Bomb beats any non-bomb
        (CombinationType.BOMB, 10, 1, CombinationType.SINGLE, 14, 1, True),
        (CombinationType.BOMB, 2, 1, CombinationType.PAIR, 14, 1, True),
        (CombinationType.BOMB, 5, 1, CombinationType.TRIPLE, 14, 1, True),
        (CombinationType.BOMB, 3, 1, CombinationType.STRAIGHT, 14, 5, True),
        (CombinationType.BOMB, 7, 1, CombinationType.FULL_HOUSE, 14, 1, True),
        (CombinationType.BOMB, 6, 1, CombinationType.STAIR, 14, 3, True),
        # Straight bomb beats any non-straight-bomb
        (CombinationType.STRAIGHT_BOMB, 10, 5, CombinationType.SINGLE, 14, 1, True),
        (CombinationType.STRAIGHT_BOMB, 8, 5, CombinationType.BOMB, 14, 1, True),
        (CombinationType.STRAIGHT_BOMB, 12, 6, CombinationType.BOMB, 2, 1, True),
        # Lower value bomb cannot beat higher value bomb
        (CombinationType.BOMB, 2, 1, CombinationType.BOMB, 14, 1, False),
        # Higher value bomb beats lower value bomb
        (CombinationType.BOMB, 14, 1, CombinationType.BOMB, 2, 1, True),
        # Straight bomb beats regular bomb
        (CombinationType.STRAIGHT_BOMB, 7, 5, CombinationType.BOMB, 14, 1, True),
        # Straight bomb with higher length beats straight bomb with lower length
        (
            CombinationType.STRAIGHT_BOMB,
            10,
            6,
            CombinationType.STRAIGHT_BOMB,
            10,
            5,
            True,
        ),
        # Straight bomb with same value but lower length cannot beat
        (
            CombinationType.STRAIGHT_BOMB,
            10,
            5,
            CombinationType.STRAIGHT_BOMB,
            10,
            6,
            False,
        ),
        # Straight bomb with higher value beats straight bomb with lower value (same length)
        (
            CombinationType.STRAIGHT_BOMB,
            12,
            5,
            CombinationType.STRAIGHT_BOMB,
            10,
            5,
            True,
        ),
    ],
)
def test_can_be_played_on_bombs(
    played_type,
    played_value,
    played_length,
    current_type,
    current_value,
    current_length,
    expected,
):
    """Test that bombs can beat non-bombs and other bombs according to rules."""
    played_combo = Combination(played_type, played_value, played_length)
    current_combo = Combination(current_type, current_value, current_length)
    assert played_combo.can_be_played_on(current_combo) == expected


@pytest.mark.parametrize(
    "played_type, played_value, played_length, current_type, current_value, current_length, expected",
    [
        # Non-bomb cannot beat bomb
        (CombinationType.SINGLE, 14, 1, CombinationType.BOMB, 2, 1, False),
        (CombinationType.PAIR, 14, 1, CombinationType.BOMB, 3, 1, False),
        (CombinationType.TRIPLE, 14, 1, CombinationType.BOMB, 4, 1, False),
        (CombinationType.STRAIGHT, 14, 5, CombinationType.BOMB, 2, 1, False),
        (CombinationType.FULL_HOUSE, 14, 1, CombinationType.BOMB, 5, 1, False),
        (CombinationType.STAIR, 14, 4, CombinationType.BOMB, 6, 1, False),
        # Non-bomb cannot beat straight bomb
        (CombinationType.SINGLE, 14, 1, CombinationType.STRAIGHT_BOMB, 2, 5, False),
        (CombinationType.BOMB, 14, 1, CombinationType.STRAIGHT_BOMB, 2, 5, False),
        # Bomb cannot beat straight bomb (lower strength)
        (CombinationType.BOMB, 14, 1, CombinationType.STRAIGHT_BOMB, 5, 5, False),
    ],
)
def test_can_be_played_on_non_bomb_vs_bomb(
    played_type,
    played_value,
    played_length,
    current_type,
    current_value,
    current_length,
    expected,
):
    """Test that non-bombs cannot beat bombs."""
    played_combo = Combination(played_type, played_value, played_length)
    current_combo = Combination(current_type, current_value, current_length)
    assert played_combo.can_be_played_on(current_combo) == expected


@pytest.mark.parametrize(
    "current_type,current_value,current_length,wish_value,player_cards,expected",
    [
        # SINGLE: higher single available -> True
        (CombinationType.SINGLE, 5, 1, 7, [Card(Color.RED, 7)], True),
        # SINGLE: single lower than current -> False
        (CombinationType.SINGLE, 9, 1, 8, [Card(Color.GREEN, 8)], False),
        # PAIR: direct pair available -> True
        (
            CombinationType.PAIR,
            10,
            1,
            12,
            [Card(Color.RED, 12), Card(Color.BLUE, 12)],
            True,
        ),
        # PAIR: single + phoenix -> True
        (
            CombinationType.PAIR,
            10,
            1,
            11,
            [Card(Color.RED, 11), Card(Color.SPECIAL, SpecialCard.PHOENIX.value)],
            True,
        ),
        # PAIR: cannot beat current pair value -> False
        (
            CombinationType.PAIR,
            12,
            1,
            11,
            [Card(Color.RED, 11), Card(Color.BLUE, 11)],
            False,
        ),
        # TRIPLE: direct triple available -> True
        (
            CombinationType.TRIPLE,
            6,
            1,
            8,
            [Card(Color.RED, 8), Card(Color.BLUE, 8), Card(Color.GREEN, 8)],
            True,
        ),
        # TRIPLE: two + phoenix -> True
        (
            CombinationType.TRIPLE,
            10,
            1,
            11,
            [
                Card(Color.RED, 11),
                Card(Color.BLUE, 11),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
            ],
            True,
        ),
        # BOMB: four-of-a-kind available -> True
        (
            CombinationType.BOMB,
            5,
            1,
            9,
            [
                Card(Color.RED, 9),
                Card(Color.BLUE, 9),
                Card(Color.GREEN, 9),
                Card(Color.YELLOW, 9),
            ],
            True,
        ),
        # BOMB: needs to be played
        (
            CombinationType.SINGLE,
            5,
            1,
            9,
            [
                Card(Color.RED, 9),
                Card(Color.BLUE, 9),
                Card(Color.GREEN, 9),
                Card(Color.YELLOW, 9),
            ],
            True,
        ),
        # BOMB: can not be played if too small
        (
            CombinationType.BOMB,
            10,
            1,
            9,
            [
                Card(Color.RED, 9),
                Card(Color.BLUE, 9),
                Card(Color.GREEN, 9),
                Card(Color.YELLOW, 9),
            ],
            False,
        ),
        # BOMB: insufficient cards -> False
        (
            CombinationType.BOMB,
            5,
            1,
            9,
            [Card(Color.RED, 9), Card(Color.BLUE, 9), Card(Color.GREEN, 9)],
            False,
        ),
        # FULL_HOUSE: 3 + 2 available -> Too Small -> False
        (
            CombinationType.FULL_HOUSE,
            10,
            1,
            9,
            [
                Card(Color.RED, 9),
                Card(Color.BLUE, 9),
                Card(Color.GREEN, 9),
                Card(Color.RED, 2),
                Card(Color.BLUE, 2),
            ],
            False,
        ),
        (
            CombinationType.FULL_HOUSE,
            10,
            1,
            9,
            [
                Card(Color.RED, 11),
                Card(Color.BLUE, 11),
                Card(Color.GREEN, 11),
                Card(Color.RED, 9),
                Card(Color.BLUE, 9),
            ],
            True,
        ),
        # FULL_HOUSE: with phoenix complement -> True
        (
            CombinationType.FULL_HOUSE,
            10,
            1,
            14,
            [
                Card(Color.RED, 14),
                Card(Color.BLUE, 14),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
                Card(Color.RED, 3),
                Card(Color.BLUE, 3),
            ],
            True,
        ),
        # FULL_HOUSE: missing complement -> False
        (
            CombinationType.FULL_HOUSE,
            10,
            1,
            9,
            [
                Card(Color.RED, 9),
                Card(Color.BLUE, 9),
                Card(Color.GREEN, 9),
                Card(Color.RED, 4),
                Card(Color.BLUE, 5),
            ],
            False,
        ),
        (
            CombinationType.FULL_HOUSE,
            8,
            1,
            4,
            [
                Card(Color.RED, 9),
                Card(Color.BLUE, 9),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
                Card(Color.RED, 4),
            ],
            False,
        ),
        (
            CombinationType.STRAIGHT,
            8,
            5,
            7,
            [
                Card(Color.RED, 3),
                Card(Color.RED, 4),
                Card(Color.BLUE, 5),
                Card(Color.RED, 6),
                Card(Color.GREEN, 7),
                Card(Color.RED, 8),
                Card(Color.YELLOW, 9),
                Card(Color.BLUE, 10),
                Card(Color.GREEN, 11),
                Card(Color.YELLOW, 12),
                Card(Color.RED, 13),
            ],
            True,
        ),
        (
            CombinationType.STRAIGHT,
            8,
            5,
            9,
            [
                Card(Color.RED, 5),
                Card(Color.RED, 6),
                Card(Color.RED, 7),
                Card(Color.RED, 9),
                Card(Color.BLUE, 10),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
                Card(Color.YELLOW, 12),
                Card(Color.RED, 13),
            ],
            True,
        ),
        (
            CombinationType.STRAIGHT,
            13,
            5,
            10,
            [
                Card(Color.RED, 5),
                Card(Color.RED, 6),
                Card(Color.RED, 7),
                Card(Color.RED, 9),
                Card(Color.BLUE, 10),
                Card(Color.BLUE, 11),
                Card(Color.YELLOW, 12),
                Card(Color.RED, 13),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
            ],
            True,
        ),
        (
            CombinationType.STRAIGHT,
            8,
            7,
            9,
            [
                Card(Color.RED, 5),
                Card(Color.RED, 6),
                Card(Color.RED, 7),
                Card(Color.RED, 9),
                Card(Color.BLUE, 10),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
                Card(Color.YELLOW, 12),
                Card(Color.RED, 13),
            ],
            False,
        ),
        (
            CombinationType.STRAIGHT,
            8,
            5,
            9,
            [
                Card(Color.RED, 5),
                Card(Color.RED, 7),
                Card(Color.RED, 9),
                Card(Color.BLUE, 10),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
                Card(Color.RED, 13),
            ],
            False,
        ),
        (
            CombinationType.STRAIGHT,
            6,
            5,
            7,
            [
                Card(Color.RED, 3),
                Card(Color.GREEN, 4),
                Card(Color.RED, 5),
                Card(Color.BLUE, 6),
                Card(Color.RED, 7),
            ],
            True,
        ),
        (
            CombinationType.STRAIGHT,
            8,
            5,
            7,
            [
                Card(Color.RED, 3),
                Card(Color.GREEN, 4),
                Card(Color.RED, 5),
                Card(Color.BLUE, 6),
                Card(Color.RED, 7),
            ],
            False,
        ),
        (
            CombinationType.STRAIGHT,
            6,
            5,
            7,
            [
                Card(Color.RED, 2),
                Card(Color.GREEN, 4),
                Card(Color.RED, 5),
                Card(Color.BLUE, 6),
                Card(Color.RED, 7),
            ],
            False,
        ),
        (
            CombinationType.STAIR,
            6,
            3,
            7,
            [
                Card(Color.RED, 7),
                Card(Color.BLUE, 7),
                Card(Color.GREEN, 8),
                Card(Color.YELLOW, 8),
                Card(Color.RED, 9),
                Card(Color.BLUE, 9),
            ],
            True,
        ),
        (
            CombinationType.STAIR,
            6,
            3,
            7,
            [
                Card(Color.RED, 7),
                Card(Color.BLUE, 7),
                Card(Color.GREEN, 8),
                Card(Color.YELLOW, 9),
                Card(Color.RED, 9),
                Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
            ],
            True,
        ),
        (
            CombinationType.STAIR,
            6,
            3,
            7,
            [
                Card(Color.RED, 7),
                Card(Color.BLUE, 7),
                Card(Color.GREEN, 8),
                Card(Color.YELLOW, 8),
                Card(Color.RED, 8),
                Card(Color.BLUE, 9),
            ],
            False,
        ),
        (
            CombinationType.STAIR,
            10,
            3,
            7,
            [
                Card(Color.RED, 7),
                Card(Color.BLUE, 7),
                Card(Color.GREEN, 8),
                Card(Color.YELLOW, 8),
                Card(Color.RED, 9),
                Card(Color.BLUE, 9),
            ],
            False,
        ),
        (
            CombinationType.FULL_HOUSE,
            14,
            1,
            7,
            [
                Card(Color.RED, 3),
                Card(Color.RED, 4),
                Card(Color.RED, 5),
                Card(Color.RED, 6),
                Card(Color.RED, 7),
            ],
            True,
        ),
    ],
)
def test_can_fulfill_wish(
    current_type,
    current_value,
    current_length,
    wish_value,
    player_cards,
    expected,
):
    current_combo = Combination(current_type, current_value, current_length)
    assert (
        Combination.can_fulfill_wish(current_combo, wish_value, player_cards)
        is expected
    )
