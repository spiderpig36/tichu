import pytest
from tichu.card import Card, Color, SpecialCard
from tichu.combination import Combination, CombinationType, InvalidCombinationError

def test_single():
    card = Card(Color.RED, 10)
    combination = Combination.from_cards([card])

    assert combination.combination_type == CombinationType.SINGLE
    assert combination.value == 10

def test_pair():
    card1 = Card(Color.RED, 5)
    card2 = Card(Color.GREEN, 5)
    combination = Combination.from_cards([card1, card2])

    assert combination.combination_type == CombinationType.PAIR
    assert combination.value == 5

def test_pair_with_phoenix():
    card1 = Card(Color.RED, 8)
    card2 = Card(Color.SPECIAL, SpecialCard.PHOENIX.value)
    combination = Combination.from_cards([card1, card2])

    assert combination.combination_type == CombinationType.PAIR
    assert combination.value == 8

def test_invalid_pair():
    card1 = Card(Color.RED, 8)
    card2 = Card(Color.GREEN, 9)
    with pytest.raises(InvalidCombinationError):
        Combination.from_cards([card1, card2])

def test_triple():
    cards = [Card(Color.RED, 7), Card(Color.GREEN, 7), Card(Color.YELLOW, 7)]
    combination = Combination.from_cards(cards)

    assert combination.combination_type == CombinationType.TRIPLE
    assert combination.value == 7

def test_triple_with_phoenix():
    cards = [Card(Color.RED, 12), Card(Color.GREEN, 12), Card(Color.SPECIAL, SpecialCard.PHOENIX.value)]
    combination = Combination.from_cards(cards)

    assert combination.combination_type == CombinationType.TRIPLE
    assert combination.value == 12

def test_invalid_triple():
    cards = [Card(Color.RED, 10), Card(Color.GREEN, 10), Card(Color.YELLOW, 11)]
    with pytest.raises(InvalidCombinationError):
        Combination.from_cards(cards)

def test_straight():
    cards = [
        Card(Color.RED, 6),
        Card(Color.RED, 3),
        Card(Color.GREEN, 4),
        Card(Color.YELLOW, 5),
        Card(Color.GREEN, 7)
    ]
    combination = Combination.from_cards(cards)

    assert combination.combination_type == CombinationType.STRAIGHT
    assert combination.value == 7
    assert combination.length == 5

def test_full_house():
    cards = [
        Card(Color.RED, 9),
        Card(Color.GREEN, 9),
        Card(Color.YELLOW, 9),
        Card(Color.RED, 12),
        Card(Color.GREEN, 12)
    ]
    combination = Combination.from_cards(cards)

    assert combination.combination_type == CombinationType.FULL_HOUSE
    assert combination.value == 9

def test_full_house_with_phoenix():
    cards = [
        Card(Color.RED, 14),
        Card(Color.GREEN, 14),
        Card(Color.SPECIAL, SpecialCard.PHOENIX.value),
        Card(Color.RED, 2),
        Card(Color.GREEN, 2)
    ]
    combination = Combination.from_cards(cards)

    assert combination.combination_type == CombinationType.FULL_HOUSE
    assert combination.value == 14

def test_stair():
    cards = [
        Card(Color.RED, 2),
        Card(Color.GREEN, 2),
        Card(Color.RED, 3),
        Card(Color.GREEN, 3),
        Card(Color.RED, 4),
        Card(Color.GREEN, 4)
    ]
    combination = Combination.from_cards(cards)

    assert combination.combination_type == CombinationType.STAIR
    assert combination.value == 4
    assert combination.length == 3

def test_bomb():
    cards = [
        Card(Color.RED, 11),
        Card(Color.GREEN, 11),
        Card(Color.YELLOW, 11),
        Card(Color.BLUE, 11)
    ]
    combination = Combination.from_cards(cards)

    assert combination.combination_type == CombinationType.BOMB
    assert combination.value == 11

def test_invalid_bomb():
    cards = [
        Card(Color.RED, 13),
        Card(Color.GREEN, 13),
        Card(Color.YELLOW, 13),
        Card(Color.BLUE, 12)
    ]
    with pytest.raises(InvalidCombinationError):
        Combination.from_cards(cards)

def test_invalid_bomb_with_phoenix():
    cards = [
        Card(Color.RED, 14),
        Card(Color.GREEN, 14),
        Card(Color.YELLOW, 14),
        Card(Color.SPECIAL, SpecialCard.PHOENIX.value)
    ]
    with pytest.raises(InvalidCombinationError):
        Combination.from_cards(cards)

def test_straight_bomb():
    cards = [
        Card(Color.RED, 8),
        Card(Color.RED, 9),
        Card(Color.RED, 10),
        Card(Color.RED, 11),
        Card(Color.RED, 12)
    ]
    combination = Combination.from_cards(cards)

    assert combination.combination_type == CombinationType.STRAIGHT_BOMB
    assert combination.value == 12
    assert combination.length == 5