import pytest
from tichu.card import Card, Color, SpecialCard
from tichu.combination import Combination, CombinationType

@pytest.mark.parametrize("cards, expected_type, expected_value, expected_length", [
    ([Card(Color.RED, 10)], CombinationType.SINGLE, 10, 1),
    ([Card(Color.RED, 5), Card(Color.GREEN, 5)], CombinationType.PAIR, 5, 1),
    ([Card(Color.RED, 8), Card(Color.SPECIAL, SpecialCard.PHOENIX.value)], CombinationType.PAIR, 8, 1),
    ([Card(Color.RED, 7), Card(Color.GREEN, 7), Card(Color.YELLOW, 7)], CombinationType.TRIPLE, 7, 1),
    ([Card(Color.RED, 12), Card(Color.GREEN, 12), Card(Color.SPECIAL, SpecialCard.PHOENIX.value)], CombinationType.TRIPLE, 12, 1),
    ([Card(Color.RED, 6), Card(Color.RED, 3), Card(Color.GREEN, 4), Card(Color.YELLOW, 5), Card(Color.GREEN, 7)], CombinationType.STRAIGHT, 7, 5),
    ([Card(Color.RED, 6), Card(Color.RED, 2), Card(Color.RED, 3), Card(Color.GREEN, 4), Card(Color.YELLOW, 5), Card(Color.GREEN, 7)], CombinationType.STRAIGHT, 7, 6),
    ([Card(Color.RED, 9), Card(Color.GREEN, 10), Card(Color.YELLOW, 11), Card(Color.SPECIAL, SpecialCard.PHOENIX.value), Card(Color.BLUE, 13)], CombinationType.STRAIGHT, 13, 5),
    ([Card(Color.RED, 9), Card(Color.GREEN, 10), Card(Color.YELLOW, 11), Card(Color.BLUE, 12), Card(Color.SPECIAL, SpecialCard.PHOENIX.value)], CombinationType.STRAIGHT, 13, 5),
    ([Card(Color.SPECIAL, SpecialCard.PHOENIX.value), Card(Color.GREEN, 11), Card(Color.YELLOW, 12), Card(Color.BLUE, 13), Card(Color.RED, 14)], CombinationType.STRAIGHT, 14, 5),
    ([Card(Color.RED, 2), Card(Color.BLUE, 2), Card(Color.GREEN, 4), Card(Color.YELLOW, 4), Card(Color.GREEN, 3), Card(Color.RED, 3)], CombinationType.STAIR, 4, 3),
    ([Card(Color.GREEN, 4), Card(Color.YELLOW, 4), Card(Color.SPECIAL, SpecialCard.PHOENIX.value), Card(Color.RED, 3)], CombinationType.STAIR, 4, 2),
    ([Card(Color.RED, 2), Card(Color.BLUE, 2), Card(Color.GREEN, 4), Card(Color.YELLOW, 4), Card(Color.SPECIAL, SpecialCard.PHOENIX.value), Card(Color.RED, 3)], CombinationType.STAIR, 4, 3),
    ([Card(Color.RED, 9), Card(Color.GREEN, 9), Card(Color.YELLOW, 9), Card(Color.RED, 12), Card(Color.GREEN, 12)], CombinationType.FULL_HOUSE, 9, 1),
    ([Card(Color.RED, 14), Card(Color.GREEN, 14), Card(Color.SPECIAL, SpecialCard.PHOENIX.value), Card(Color.RED, 2), Card(Color.GREEN, 2)], CombinationType.FULL_HOUSE, 14, 1),
    ([Card(Color.RED, 14), Card(Color.GREEN, 14), Card(Color.SPECIAL, SpecialCard.PHOENIX.value), Card(Color.RED, 14), Card(Color.GREEN, 2)], CombinationType.FULL_HOUSE, 14, 1),
    ([Card(Color.RED, 11), Card(Color.GREEN, 11), Card(Color.YELLOW, 11), Card(Color.BLUE, 11)], CombinationType.BOMB, 11, 1),
    ([Card(Color.RED, 8), Card(Color.RED, 9), Card(Color.RED, 10), Card(Color.RED, 11), Card(Color.RED, 12)], CombinationType.STRAIGHT_BOMB, 12, 5),
    ([Card(Color.RED, 3), Card(Color.RED, 4), Card(Color.GREEN, 5), Card(Color.RED, 6), Card(Color.RED, 7)], CombinationType.STRAIGHT, 7, 5),
    ([Card(Color.RED, 10), Card(Color.RED, 11), Card(Color.RED, 12), Card(Color.RED, 13), Card(Color.SPECIAL, SpecialCard.PHOENIX.value)], CombinationType.STRAIGHT, 14, 5),
])
def test_valid_combinations(cards, expected_type, expected_value, expected_length):
    combination = Combination.from_cards(cards)
    assert combination is not None
    assert combination.combination_type == expected_type
    assert combination.value == expected_value
    assert combination.length == expected_length

@pytest.mark.parametrize("cards", [
    [Card(Color.RED, 8), Card(Color.GREEN, 9)],
    [Card(Color.RED, 10), Card(Color.GREEN, 10), Card(Color.YELLOW, 11)],
    [Card(Color.RED, 2), Card(Color.GREEN, 4), Card(Color.YELLOW, 5), Card(Color.BLUE, 6), Card(Color.RED, 7)],
    [Card(Color.GREEN, 4), Card(Color.YELLOW, 5), Card(Color.BLUE, 6), Card(Color.RED, 7)],
    [Card(Color.RED, 13), Card(Color.GREEN, 13), Card(Color.YELLOW, 13), Card(Color.BLUE, 12)],
    [Card(Color.RED, 14), Card(Color.GREEN, 14), Card(Color.YELLOW, 14), Card(Color.SPECIAL, SpecialCard.PHOENIX.value)],
    [Card(Color.RED, 2), Card(Color.BLUE, 2), Card(Color.GREEN, 4), Card(Color.YELLOW, 4), Card(Color.GREEN, 5), Card(Color.RED, 3)],
    [Card(Color.SPECIAL, SpecialCard.DOG.value), Card(Color.GREEN, 2)],
    [Card(Color.SPECIAL, SpecialCard.DRAGON.value), Card(Color.GREEN, 14)],
])
def test_invalid_combinations(cards):
    combination = Combination.from_cards(cards)
    assert combination is None