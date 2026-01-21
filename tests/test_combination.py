import pytest

from tichu.card import Card, Color, SpecialCard
from tichu.combination import Combination, CombinationType


@pytest.mark.parametrize(
    ("cards", "expected_type", "expected_value", "expected_length"),
    [
        ([Card(Color.JADE, 10)], CombinationType.SINGLE, 10, 1),
        ([Card(Color.JADE, 5), Card(Color.SWORDS, 5)], CombinationType.PAIR, 5, 1),
        (
            [Card(Color.JADE, 8), SpecialCard.PHOENIX.value],
            CombinationType.PAIR,
            8,
            1,
        ),
        (
            [Card(Color.JADE, 7), Card(Color.SWORDS, 7), Card(Color.STAR, 7)],
            CombinationType.TRIPLE,
            7,
            1,
        ),
        (
            [
                Card(Color.JADE, 12),
                Card(Color.SWORDS, 12),
                SpecialCard.PHOENIX.value,
            ],
            CombinationType.TRIPLE,
            12,
            1,
        ),
        (
            [
                Card(Color.JADE, 6),
                Card(Color.JADE, 3),
                Card(Color.SWORDS, 4),
                Card(Color.STAR, 5),
                Card(Color.SWORDS, 7),
            ],
            CombinationType.STRAIGHT,
            7,
            5,
        ),
        (
            [
                SpecialCard.MAH_JONG.value,
                Card(Color.JADE, 2),
                Card(Color.SWORDS, 3),
                Card(Color.STAR, 4),
                Card(Color.SWORDS, 5),
            ],
            CombinationType.STRAIGHT,
            5,
            5,
        ),
        (
            [
                Card(Color.JADE, 6),
                Card(Color.JADE, 2),
                Card(Color.JADE, 3),
                Card(Color.SWORDS, 4),
                Card(Color.STAR, 5),
                Card(Color.SWORDS, 7),
            ],
            CombinationType.STRAIGHT,
            7,
            6,
        ),
        (
            [
                Card(Color.JADE, 9),
                Card(Color.SWORDS, 10),
                Card(Color.STAR, 11),
                SpecialCard.PHOENIX.value,
                Card(Color.PAGODE, 13),
            ],
            CombinationType.STRAIGHT,
            13,
            5,
        ),
        (
            [
                Card(Color.JADE, 9),
                Card(Color.SWORDS, 10),
                Card(Color.STAR, 11),
                Card(Color.PAGODE, 12),
                SpecialCard.PHOENIX.value,
            ],
            CombinationType.STRAIGHT,
            13,
            5,
        ),
        (
            [
                SpecialCard.PHOENIX.value,
                Card(Color.SWORDS, 11),
                Card(Color.STAR, 12),
                Card(Color.PAGODE, 13),
                Card(Color.JADE, 14),
            ],
            CombinationType.STRAIGHT,
            14,
            5,
        ),
        (
            [
                Card(Color.JADE, 2),
                Card(Color.PAGODE, 2),
                Card(Color.SWORDS, 3),
                Card(Color.JADE, 3),
            ],
            CombinationType.STAIR,
            3,
            2,
        ),
        (
            [
                Card(Color.JADE, 2),
                Card(Color.PAGODE, 2),
                Card(Color.SWORDS, 4),
                Card(Color.STAR, 4),
                Card(Color.SWORDS, 3),
                Card(Color.JADE, 3),
            ],
            CombinationType.STAIR,
            4,
            3,
        ),
        (
            [
                Card(Color.SWORDS, 4),
                Card(Color.STAR, 4),
                SpecialCard.PHOENIX.value,
                Card(Color.JADE, 3),
            ],
            CombinationType.STAIR,
            4,
            2,
        ),
        (
            [
                Card(Color.JADE, 2),
                Card(Color.PAGODE, 2),
                Card(Color.SWORDS, 4),
                Card(Color.STAR, 4),
                SpecialCard.PHOENIX.value,
                Card(Color.JADE, 3),
            ],
            CombinationType.STAIR,
            4,
            3,
        ),
        (
            [
                Card(Color.JADE, 9),
                Card(Color.SWORDS, 9),
                Card(Color.STAR, 9),
                Card(Color.JADE, 12),
                Card(Color.SWORDS, 12),
            ],
            CombinationType.FULL_HOUSE,
            9,
            1,
        ),
        (
            [
                Card(Color.JADE, 14),
                Card(Color.SWORDS, 14),
                SpecialCard.PHOENIX.value,
                Card(Color.JADE, 2),
                Card(Color.SWORDS, 2),
            ],
            CombinationType.FULL_HOUSE,
            14,
            1,
        ),
        (
            [
                Card(Color.JADE, 14),
                Card(Color.SWORDS, 14),
                SpecialCard.PHOENIX.value,
                Card(Color.JADE, 14),
                Card(Color.SWORDS, 2),
            ],
            CombinationType.FULL_HOUSE,
            14,
            1,
        ),
        (
            [
                Card(Color.JADE, 11),
                Card(Color.SWORDS, 11),
                Card(Color.STAR, 11),
                Card(Color.PAGODE, 11),
            ],
            CombinationType.BOMB,
            11,
            1,
        ),
        (
            [
                Card(Color.JADE, 8),
                Card(Color.JADE, 9),
                Card(Color.JADE, 10),
                Card(Color.JADE, 11),
                Card(Color.JADE, 12),
            ],
            CombinationType.STRAIGHT_BOMB,
            12,
            5,
        ),
        (
            [
                Card(Color.JADE, 3),
                Card(Color.JADE, 4),
                Card(Color.SWORDS, 5),
                Card(Color.JADE, 6),
                Card(Color.JADE, 7),
            ],
            CombinationType.STRAIGHT,
            7,
            5,
        ),
        (
            [
                Card(Color.JADE, 10),
                Card(Color.JADE, 11),
                Card(Color.JADE, 12),
                Card(Color.JADE, 13),
                SpecialCard.PHOENIX.value,
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
        [Card(Color.JADE, 8), Card(Color.SWORDS, 9)],
        [Card(Color.JADE, 10), Card(Color.SWORDS, 10), Card(Color.STAR, 11)],
        [
            Card(Color.JADE, 2),
            Card(Color.SWORDS, 4),
            Card(Color.STAR, 5),
            Card(Color.PAGODE, 6),
            Card(Color.JADE, 7),
        ],
        [
            SpecialCard.DOG.value,
            Card(Color.SWORDS, 2),
            Card(Color.STAR, 3),
            Card(Color.PAGODE, 4),
            Card(Color.JADE, 5),
        ],
        [
            Card(Color.SWORDS, 2),
            Card(Color.SWORDS, 4),
            Card(Color.STAR, 5),
            Card(Color.PAGODE, 6),
            Card(Color.JADE, 7),
            Card(Color.JADE, 8),
        ],
        [
            Card(Color.SWORDS, 4),
            Card(Color.SWORDS, 4),
            Card(Color.STAR, 5),
            Card(Color.PAGODE, 6),
            Card(Color.JADE, 7),
            Card(Color.JADE, 8),
        ],
        [
            Card(Color.SWORDS, 4),
            Card(Color.STAR, 5),
            Card(Color.PAGODE, 6),
            Card(Color.JADE, 7),
        ],
        [
            Card(Color.SWORDS, 4),
            Card(Color.STAR, 5),
            Card(Color.STAR, 5),
            Card(Color.PAGODE, 5),
            Card(Color.JADE, 8),
        ],
        [
            Card(Color.SWORDS, 4),
            Card(Color.STAR, 5),
            Card(Color.STAR, 5),
            SpecialCard.PHOENIX.value,
            Card(Color.JADE, 8),
        ],
        [
            Card(Color.STAR, 11),
            Card(Color.STAR, 12),
            Card(Color.JADE, 13),
            Card(Color.SWORDS, 14),
            SpecialCard.DRAGON.value,
        ],
        [
            Card(Color.SWORDS, 4),
            Card(Color.SWORDS, 4),
            Card(Color.SWORDS, 5),
            SpecialCard.PHOENIX.value,
            Card(Color.JADE, 6),
        ],
        [
            Card(Color.JADE, 13),
            Card(Color.SWORDS, 13),
            Card(Color.STAR, 13),
            Card(Color.PAGODE, 12),
        ],
        [
            Card(Color.JADE, 14),
            Card(Color.SWORDS, 14),
            Card(Color.STAR, 14),
            SpecialCard.PHOENIX.value,
        ],
        [
            Card(Color.JADE, 2),
            Card(Color.PAGODE, 2),
            Card(Color.SWORDS, 4),
            Card(Color.STAR, 4),
            Card(Color.SWORDS, 5),
            Card(Color.JADE, 3),
        ],
        [SpecialCard.DOG.value, Card(Color.SWORDS, 2)],
        [SpecialCard.DRAGON.value, Card(Color.SWORDS, 14)],
    ],
)
def test_invalid_combinations(cards):
    combination = Combination.from_cards(cards)
    assert combination is None


@pytest.mark.parametrize(
    (
        "played_type",
        "played_value",
        "played_length",
        "current_type",
        "current_value",
        "current_length",
        "expected",
    ),
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
    (
        "played_type",
        "played_value",
        "played_length",
        "current_type",
        "current_value",
        "current_length",
        "expected",
    ),
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
    (
        "played_type",
        "played_value",
        "played_length",
        "current_type",
        "current_value",
        "current_length",
        "expected",
    ),
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
    (
        "current_type",
        "current_value",
        "current_length",
        "wish_value",
        "player_cards",
        "expected",
    ),
    [
        (CombinationType.SINGLE, 5, 1, 7, [Card(Color.JADE, 7)], True),
        (CombinationType.SINGLE, 9, 1, 8, [Card(Color.SWORDS, 8)], False),
        (
            CombinationType.PAIR,
            10,
            1,
            12,
            [Card(Color.JADE, 12), Card(Color.PAGODE, 12)],
            True,
        ),
        (
            CombinationType.PAIR,
            10,
            1,
            11,
            [Card(Color.JADE, 11), SpecialCard.PHOENIX.value],
            True,
        ),
        (
            CombinationType.PAIR,
            12,
            1,
            11,
            [Card(Color.JADE, 11), Card(Color.PAGODE, 11)],
            False,
        ),
        (
            CombinationType.TRIPLE,
            6,
            1,
            8,
            [Card(Color.JADE, 8), Card(Color.PAGODE, 8), Card(Color.SWORDS, 8)],
            True,
        ),
        (
            CombinationType.TRIPLE,
            10,
            1,
            11,
            [
                Card(Color.JADE, 11),
                Card(Color.PAGODE, 11),
                SpecialCard.PHOENIX.value,
            ],
            True,
        ),
        (
            CombinationType.BOMB,
            5,
            1,
            9,
            [
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 9),
                Card(Color.SWORDS, 9),
                Card(Color.STAR, 9),
            ],
            True,
        ),
        (
            CombinationType.SINGLE,
            5,
            1,
            9,
            [
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 9),
                Card(Color.SWORDS, 9),
                Card(Color.STAR, 9),
            ],
            True,
        ),
        (
            CombinationType.BOMB,
            10,
            1,
            9,
            [
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 9),
                Card(Color.SWORDS, 9),
                Card(Color.STAR, 9),
            ],
            False,
        ),
        (
            CombinationType.BOMB,
            5,
            1,
            9,
            [Card(Color.JADE, 9), Card(Color.PAGODE, 9), Card(Color.SWORDS, 9)],
            False,
        ),
        (
            CombinationType.FULL_HOUSE,
            10,
            1,
            9,
            [
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 9),
                Card(Color.SWORDS, 9),
                Card(Color.JADE, 2),
                Card(Color.PAGODE, 2),
            ],
            False,
        ),
        (
            CombinationType.FULL_HOUSE,
            10,
            1,
            9,
            [
                Card(Color.JADE, 11),
                Card(Color.PAGODE, 11),
                Card(Color.SWORDS, 11),
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 9),
            ],
            True,
        ),
        (
            CombinationType.FULL_HOUSE,
            10,
            1,
            14,
            [
                Card(Color.JADE, 14),
                Card(Color.PAGODE, 14),
                SpecialCard.PHOENIX.value,
                Card(Color.JADE, 3),
                Card(Color.PAGODE, 3),
            ],
            True,
        ),
        (
            CombinationType.FULL_HOUSE,
            10,
            1,
            9,
            [
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 9),
                Card(Color.SWORDS, 9),
                Card(Color.JADE, 4),
                Card(Color.PAGODE, 5),
            ],
            False,
        ),
        (
            CombinationType.FULL_HOUSE,
            8,
            1,
            4,
            [
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 9),
                SpecialCard.PHOENIX.value,
                Card(Color.JADE, 4),
            ],
            False,
        ),
        (
            CombinationType.STRAIGHT,
            8,
            5,
            7,
            [
                Card(Color.JADE, 3),
                Card(Color.JADE, 4),
                Card(Color.PAGODE, 5),
                Card(Color.JADE, 6),
                Card(Color.SWORDS, 7),
                Card(Color.JADE, 8),
                Card(Color.STAR, 9),
                Card(Color.PAGODE, 10),
                Card(Color.SWORDS, 11),
                Card(Color.STAR, 12),
                Card(Color.JADE, 13),
            ],
            True,
        ),
        (
            CombinationType.STRAIGHT,
            8,
            5,
            9,
            [
                Card(Color.JADE, 5),
                Card(Color.JADE, 6),
                Card(Color.JADE, 7),
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 10),
                SpecialCard.PHOENIX.value,
                Card(Color.STAR, 12),
                Card(Color.JADE, 13),
            ],
            True,
        ),
        (
            CombinationType.STRAIGHT,
            13,
            5,
            10,
            [
                Card(Color.JADE, 5),
                Card(Color.JADE, 6),
                Card(Color.JADE, 7),
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 10),
                Card(Color.PAGODE, 11),
                Card(Color.STAR, 12),
                Card(Color.JADE, 13),
                SpecialCard.PHOENIX.value,
            ],
            True,
        ),
        (
            CombinationType.STRAIGHT,
            8,
            7,
            9,
            [
                Card(Color.JADE, 5),
                Card(Color.JADE, 6),
                Card(Color.JADE, 7),
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 10),
                SpecialCard.PHOENIX.value,
                Card(Color.STAR, 12),
                Card(Color.JADE, 13),
            ],
            False,
        ),
        (
            CombinationType.STRAIGHT,
            8,
            5,
            9,
            [
                Card(Color.JADE, 5),
                Card(Color.JADE, 7),
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 10),
                SpecialCard.PHOENIX.value,
                Card(Color.JADE, 13),
            ],
            False,
        ),
        (
            CombinationType.STRAIGHT,
            6,
            5,
            7,
            [
                Card(Color.JADE, 3),
                Card(Color.SWORDS, 4),
                Card(Color.JADE, 5),
                Card(Color.PAGODE, 6),
                Card(Color.JADE, 7),
            ],
            True,
        ),
        (
            CombinationType.STRAIGHT,
            8,
            5,
            7,
            [
                Card(Color.JADE, 3),
                Card(Color.SWORDS, 4),
                Card(Color.JADE, 5),
                Card(Color.PAGODE, 6),
                Card(Color.JADE, 7),
            ],
            False,
        ),
        (
            CombinationType.STRAIGHT,
            6,
            5,
            7,
            [
                Card(Color.JADE, 2),
                Card(Color.SWORDS, 4),
                Card(Color.JADE, 5),
                Card(Color.PAGODE, 6),
                Card(Color.JADE, 7),
            ],
            False,
        ),
        (
            CombinationType.STAIR,
            6,
            3,
            7,
            [
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.SWORDS, 8),
                Card(Color.STAR, 8),
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 9),
            ],
            True,
        ),
        (
            CombinationType.STAIR,
            6,
            3,
            7,
            [
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.SWORDS, 8),
                Card(Color.STAR, 9),
                Card(Color.JADE, 9),
                SpecialCard.PHOENIX.value,
            ],
            True,
        ),
        (
            CombinationType.STAIR,
            6,
            3,
            7,
            [
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.SWORDS, 8),
                Card(Color.STAR, 8),
                Card(Color.JADE, 8),
                Card(Color.PAGODE, 9),
            ],
            False,
        ),
        (
            CombinationType.STAIR,
            10,
            3,
            7,
            [
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.SWORDS, 8),
                Card(Color.STAR, 8),
                Card(Color.JADE, 9),
                Card(Color.PAGODE, 9),
            ],
            False,
        ),
        (
            CombinationType.FULL_HOUSE,
            14,
            1,
            7,
            [
                Card(Color.JADE, 3),
                Card(Color.JADE, 4),
                Card(Color.JADE, 5),
                Card(Color.JADE, 6),
                Card(Color.JADE, 7),
            ],
            True,
        ),
        (
            CombinationType.FULL_HOUSE,
            14,
            1,
            7,
            [
                Card(Color.JADE, 3),
                Card(Color.JADE, 4),
                Card(Color.JADE, 5),
                Card(Color.JADE, 6),
                Card(Color.SWORDS, 7),
            ],
            False,
        ),
        (
            CombinationType.STRAIGHT_BOMB,
            8,
            6,
            7,
            [
                Card(Color.JADE, 3),
                Card(Color.JADE, 4),
                Card(Color.JADE, 5),
                Card(Color.JADE, 6),
                Card(Color.JADE, 7),
            ],
            False,
        ),
        (
            CombinationType.STRAIGHT_BOMB,
            8,
            6,
            7,
            [
                Card(Color.SWORDS, 3),
                Card(Color.JADE, 4),
                Card(Color.JADE, 5),
                Card(Color.JADE, 6),
                Card(Color.JADE, 7),
                Card(Color.JADE, 8),
                Card(Color.JADE, 9),
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


@pytest.mark.parametrize(
    (
        "combination",
        "cards",
        "expected",
    ),
    [
        (
            None,
            [Card(Color.JADE, 7)],
            [{Card(Color.JADE, 7)}],
        ),
        (
            None,
            [Card(Color.JADE, 7), Card(Color.PAGODE, 7)],
            [
                {Card(Color.PAGODE, 7)},
                {Card(Color.JADE, 7)},
                {Card(Color.PAGODE, 7), Card(Color.JADE, 7)},
            ],
        ),
        (
            Combination(CombinationType.PAIR, 6, 1),
            [Card(Color.JADE, 7), Card(Color.PAGODE, 7)],
            [
                {Card(Color.PAGODE, 7), Card(Color.JADE, 7)},
            ],
        ),
        (
            Combination(CombinationType.PAIR, 6, 1),
            [Card(Color.JADE, 7), SpecialCard.PHOENIX.value],
            [
                {Card(Color.JADE, 7), SpecialCard.PHOENIX.value},
            ],
        ),
        (
            Combination(CombinationType.PAIR, 8, 1),
            [Card(Color.JADE, 7), SpecialCard.PHOENIX.value],
            [],
        ),
        (
            None,
            [Card(Color.JADE, 7), Card(Color.PAGODE, 7), Card(Color.SWORDS, 7)],
            [
                {Card(Color.PAGODE, 7)},
                {Card(Color.JADE, 7)},
                {Card(Color.SWORDS, 7)},
                {Card(Color.PAGODE, 7), Card(Color.JADE, 7)},
                {Card(Color.PAGODE, 7), Card(Color.SWORDS, 7)},
                {Card(Color.JADE, 7), Card(Color.SWORDS, 7)},
                {
                    Card(Color.PAGODE, 7),
                    Card(Color.JADE, 7),
                    Card(Color.SWORDS, 7),
                },
            ],
        ),
        (
            None,
            [
                Card(Color.STAR, 7),
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.SWORDS, 7),
            ],
            [
                {Card(Color.PAGODE, 7)},
                {Card(Color.JADE, 7)},
                {Card(Color.SWORDS, 7)},
                {Card(Color.STAR, 7)},
                {Card(Color.PAGODE, 7), Card(Color.JADE, 7)},
                {Card(Color.PAGODE, 7), Card(Color.SWORDS, 7)},
                {Card(Color.JADE, 7), Card(Color.SWORDS, 7)},
                {Card(Color.STAR, 7), Card(Color.JADE, 7)},
                {Card(Color.STAR, 7), Card(Color.PAGODE, 7)},
                {Card(Color.STAR, 7), Card(Color.SWORDS, 7)},
                {Card(Color.STAR, 7), Card(Color.JADE, 7), Card(Color.PAGODE, 7)},
                {Card(Color.STAR, 7), Card(Color.JADE, 7), Card(Color.SWORDS, 7)},
                {Card(Color.STAR, 7), Card(Color.PAGODE, 7), Card(Color.SWORDS, 7)},
                {
                    Card(Color.PAGODE, 7),
                    Card(Color.JADE, 7),
                    Card(Color.SWORDS, 7),
                },
                {
                    Card(Color.STAR, 7),
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.SWORDS, 7),
                },
            ],
        ),
        (
            None,
            [
                Card(Color.STAR, 2),
                Card(Color.JADE, 3),
                Card(Color.PAGODE, 4),
                Card(Color.SWORDS, 5),
                Card(Color.JADE, 6),
            ],
            [
                {Card(Color.STAR, 2)},
                {Card(Color.JADE, 3)},
                {Card(Color.PAGODE, 4)},
                {Card(Color.SWORDS, 5)},
                {Card(Color.JADE, 6)},
                {
                    Card(Color.STAR, 2),
                    Card(Color.JADE, 3),
                    Card(Color.PAGODE, 4),
                    Card(Color.SWORDS, 5),
                    Card(Color.JADE, 6),
                },
            ],
        ),
        (
            None,
            [
                Card(Color.STAR, 2),
                Card(Color.JADE, 3),
                Card(Color.PAGODE, 4),
                Card(Color.SWORDS, 5),
                Card(Color.JADE, 6),
                Card(Color.PAGODE, 7),
            ],
            [
                {Card(Color.STAR, 2)},
                {Card(Color.JADE, 3)},
                {Card(Color.PAGODE, 4)},
                {Card(Color.SWORDS, 5)},
                {Card(Color.JADE, 6)},
                {Card(Color.PAGODE, 7)},
                {
                    Card(Color.STAR, 2),
                    Card(Color.JADE, 3),
                    Card(Color.PAGODE, 4),
                    Card(Color.SWORDS, 5),
                    Card(Color.JADE, 6),
                },
                {
                    Card(Color.JADE, 3),
                    Card(Color.PAGODE, 4),
                    Card(Color.SWORDS, 5),
                    Card(Color.JADE, 6),
                    Card(Color.PAGODE, 7),
                },
                {
                    Card(Color.STAR, 2),
                    Card(Color.JADE, 3),
                    Card(Color.PAGODE, 4),
                    Card(Color.SWORDS, 5),
                    Card(Color.JADE, 6),
                    Card(Color.PAGODE, 7),
                },
            ],
        ),
        (
            Combination(CombinationType.STRAIGHT, 6, 5),
            [
                Card(Color.JADE, 3),
                Card(Color.PAGODE, 4),
                Card(Color.SWORDS, 5),
                Card(Color.JADE, 6),
                Card(Color.PAGODE, 7),
            ],
            [
                {
                    Card(Color.JADE, 3),
                    Card(Color.PAGODE, 4),
                    Card(Color.SWORDS, 5),
                    Card(Color.JADE, 6),
                    Card(Color.PAGODE, 7),
                },
            ],
        ),
        (
            Combination(CombinationType.STRAIGHT, 6, 5),
            [
                Card(Color.JADE, 3),
                Card(Color.PAGODE, 4),
                Card(Color.JADE, 6),
                Card(Color.PAGODE, 7),
            ],
            [],
        ),
        (
            Combination(CombinationType.FULL_HOUSE, 14),
            [
                Card(Color.JADE, 2),
                Card(Color.JADE, 3),
                Card(Color.JADE, 4),
                Card(Color.JADE, 5),
                Card(Color.JADE, 6),
            ],
            [
                {
                    Card(Color.JADE, 2),
                    Card(Color.JADE, 3),
                    Card(Color.JADE, 4),
                    Card(Color.JADE, 5),
                    Card(Color.JADE, 6),
                }
            ],
        ),
        (
            Combination(CombinationType.FULL_HOUSE, 14),
            [
                Card(Color.SWORDS, 2),
                Card(Color.JADE, 3),
                Card(Color.JADE, 4),
                Card(Color.JADE, 5),
                Card(Color.JADE, 6),
            ],
            [],
        ),
        (
            Combination(CombinationType.STRAIGHT, 6, 5),
            [
                Card(Color.JADE, 3),
                Card(Color.PAGODE, 4),
                SpecialCard.PHOENIX.value,
                Card(Color.JADE, 6),
                Card(Color.PAGODE, 7),
            ],
            [
                {
                    Card(Color.JADE, 3),
                    Card(Color.PAGODE, 4),
                    SpecialCard.PHOENIX.value,
                    Card(Color.JADE, 6),
                    Card(Color.PAGODE, 7),
                },
            ],
        ),
        (
            Combination(CombinationType.STRAIGHT, 6, 5),
            [
                Card(Color.JADE, 3),
                Card(Color.PAGODE, 4),
                Card(Color.SWORDS, 5),
                Card(Color.JADE, 6),
                Card(Color.PAGODE, 7),
                SpecialCard.PHOENIX.value,
            ],
            [
                {
                    Card(Color.JADE, 3),
                    Card(Color.PAGODE, 4),
                    Card(Color.SWORDS, 5),
                    Card(Color.JADE, 6),
                    Card(Color.PAGODE, 7),
                },
                {
                    SpecialCard.PHOENIX.value,
                    Card(Color.PAGODE, 4),
                    Card(Color.SWORDS, 5),
                    Card(Color.JADE, 6),
                    Card(Color.PAGODE, 7),
                },
                {
                    Card(Color.JADE, 3),
                    SpecialCard.PHOENIX.value,
                    Card(Color.SWORDS, 5),
                    Card(Color.JADE, 6),
                    Card(Color.PAGODE, 7),
                },
                {
                    Card(Color.JADE, 3),
                    Card(Color.PAGODE, 4),
                    SpecialCard.PHOENIX.value,
                    Card(Color.JADE, 6),
                    Card(Color.PAGODE, 7),
                },
                {
                    Card(Color.JADE, 3),
                    Card(Color.PAGODE, 4),
                    Card(Color.SWORDS, 5),
                    SpecialCard.PHOENIX.value,
                    Card(Color.PAGODE, 7),
                },
                {
                    Card(Color.JADE, 3),
                    Card(Color.PAGODE, 4),
                    Card(Color.SWORDS, 5),
                    Card(Color.JADE, 6),
                    SpecialCard.PHOENIX.value,
                },
                {
                    Card(Color.PAGODE, 4),
                    Card(Color.SWORDS, 5),
                    Card(Color.JADE, 6),
                    Card(Color.PAGODE, 7),
                    SpecialCard.PHOENIX.value,
                },
            ],
        ),
        (
            Combination(CombinationType.STRAIGHT, 9, 5),
            [
                Card(Color.JADE, 3),
                Card(Color.PAGODE, 4),
                Card(Color.SWORDS, 5),
                Card(Color.JADE, 6),
                Card(Color.PAGODE, 7),
                SpecialCard.PHOENIX.value,
            ],
            [],
        ),
        (
            Combination(CombinationType.FULL_HOUSE, 6),
            [
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.SWORDS, 7),
                Card(Color.JADE, 8),
                Card(Color.SWORDS, 8),
            ],
            [
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.JADE, 8),
                    Card(Color.SWORDS, 8),
                }
            ],
        ),
        (
            Combination(CombinationType.FULL_HOUSE, 6),
            [
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.SWORDS, 7),
                Card(Color.JADE, 8),
                Card(Color.SWORDS, 8),
                Card(Color.PAGODE, 8),
            ],
            [
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.JADE, 8),
                    Card(Color.SWORDS, 8),
                },
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.JADE, 8),
                    Card(Color.PAGODE, 8),
                },
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.PAGODE, 8),
                    Card(Color.SWORDS, 8),
                },
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.JADE, 8),
                    Card(Color.SWORDS, 8),
                    Card(Color.PAGODE, 8),
                },
                {
                    Card(Color.JADE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.JADE, 8),
                    Card(Color.SWORDS, 8),
                    Card(Color.PAGODE, 8),
                },
                {
                    Card(Color.PAGODE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.JADE, 8),
                    Card(Color.SWORDS, 8),
                    Card(Color.PAGODE, 8),
                },
            ],
        ),
        (
            Combination(CombinationType.FULL_HOUSE, 6),
            [
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.SWORDS, 7),
                Card(Color.JADE, 8),
                Card(Color.STAR, 8),
                SpecialCard.PHOENIX.value,
            ],
            [
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.JADE, 8),
                    Card(Color.STAR, 8),
                },
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.JADE, 8),
                    SpecialCard.PHOENIX.value,
                },
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.STAR, 8),
                    SpecialCard.PHOENIX.value,
                },
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.STAR, 8),
                    Card(Color.JADE, 8),
                    SpecialCard.PHOENIX.value,
                },
                {
                    Card(Color.JADE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.STAR, 8),
                    Card(Color.JADE, 8),
                    SpecialCard.PHOENIX.value,
                },
                {
                    Card(Color.PAGODE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.STAR, 8),
                    Card(Color.JADE, 8),
                    SpecialCard.PHOENIX.value,
                },
            ],
        ),
        (
            Combination(CombinationType.FULL_HOUSE, 6),
            [
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.SWORDS, 7),
                Card(Color.STAR, 8),
                SpecialCard.PHOENIX.value,
            ],
            [
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.SWORDS, 7),
                    Card(Color.STAR, 8),
                    SpecialCard.PHOENIX.value,
                },
            ],
        ),
        (
            Combination(CombinationType.FULL_HOUSE, 6),
            [
                Card(Color.JADE, 5),
                Card(Color.PAGODE, 5),
                Card(Color.SWORDS, 5),
                Card(Color.STAR, 8),
                SpecialCard.PHOENIX.value,
            ],
            [],
        ),
        (
            Combination(CombinationType.FULL_HOUSE, 6),
            [
                Card(Color.JADE, 5),
                Card(Color.PAGODE, 5),
                Card(Color.STAR, 8),
                SpecialCard.PHOENIX.value,
            ],
            [],
        ),
        (
            Combination(CombinationType.STAIR, 6, 2),
            [
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.STAR, 8),
                Card(Color.SWORDS, 8),
            ],
            [
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.STAR, 8),
                    Card(Color.SWORDS, 8),
                },
            ],
        ),
        (
            Combination(CombinationType.STAIR, 6, 3),
            [
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.STAR, 8),
                Card(Color.SWORDS, 8),
                Card(Color.STAR, 9),
                Card(Color.SWORDS, 9),
            ],
            [
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.STAR, 8),
                    Card(Color.SWORDS, 8),
                    Card(Color.STAR, 9),
                    Card(Color.SWORDS, 9),
                },
            ],
        ),
        (
            Combination(CombinationType.STAIR, 6, 2),
            [
                Card(Color.JADE, 7),
                Card(Color.PAGODE, 7),
                Card(Color.STAR, 8),
                Card(Color.SWORDS, 8),
                Card(Color.STAR, 9),
                Card(Color.SWORDS, 9),
            ],
            [
                {
                    Card(Color.JADE, 7),
                    Card(Color.PAGODE, 7),
                    Card(Color.STAR, 8),
                    Card(Color.SWORDS, 8),
                },
                {
                    Card(Color.STAR, 8),
                    Card(Color.SWORDS, 8),
                    Card(Color.STAR, 9),
                    Card(Color.SWORDS, 9),
                },
            ],
        ),
        (
            Combination(CombinationType.STAIR, 6, 2),
            [
                Card(Color.JADE, 7),
                SpecialCard.PHOENIX.value,
                Card(Color.STAR, 8),
                Card(Color.SWORDS, 8),
            ],
            [
                {
                    Card(Color.JADE, 7),
                    SpecialCard.PHOENIX.value,
                    Card(Color.STAR, 8),
                    Card(Color.SWORDS, 8),
                },
            ],
        ),
        (
            Combination(CombinationType.STAIR, 6, 2),
            [
                Card(Color.JADE, 3),
                SpecialCard.PHOENIX.value,
                Card(Color.STAR, 4),
                Card(Color.SWORDS, 4),
            ],
            [],
        ),
    ],
)
def test_possible_plays(
    combination,
    cards,
    expected,
):
    possible_plays = Combination.possible_plays(combination, cards)
    assert len(expected) == len(possible_plays)
    assert all(expected_play in possible_plays for expected_play in expected)
