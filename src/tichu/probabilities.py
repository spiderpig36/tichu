from functools import reduce
import math
import random
from tqdm import tqdm
from tichu.card import NORMAL_CARD_VALUES, Card, Color, SpecialCard
from tichu.combination import CombinationType
from tichu.player import Player
from tichu.tichu import NUM_PLAYERS, Tichu


def get_probability_for_combination(
    remaining_cards: list[Card], hand_size: int, play: list[Card]
):
    if all([card in remaining_cards for card in play]):
        return math.comb(
            len(remaining_cards) - len(play), hand_size - len(play)
        ) / math.comb(len(remaining_cards), hand_size)
    else:
        return 0


def get_probability_for_combination_excluding_others(
    remaining_cards: list[Card],
    hand_size: int,
    play: list[Card],
    impossible_plays: list[list[Card]],
):
    probability_impossible_plays = 1 - reduce(
        lambda x, y: x * y,
        [
            get_probability_for_combination(remaining_cards, hand_size, play)
            for play in impossible_plays
        ],
        1,
    )
    if all([card in remaining_cards for card in play]):
        return math.comb(
            len(remaining_cards) - len(play), hand_size - len(play)
        ) / math.comb(len(remaining_cards), hand_size)
    else:
        return 0


if __name__ == "__main__":
    count = 0
    play = [
        Card(Color.JADE, 2),
        Card(Color.PAGODE, 2),
        Card(Color.STAR, 2),
        Card(Color.SWORDS, 2),
    ]
    player_num = 0
    deck = []
    for color in Color:
        if color == Color.SPECIAL:
            continue
        for value in NORMAL_CARD_VALUES:
            card = Card(color, value)
            deck.append(card)
    deck.extend([Card(Color.SPECIAL, card.value) for card in SpecialCard])
    trials = 100000
    for i in tqdm(range(0, trials)):
        players = [Player(f"Player {i}") for i in range(NUM_PLAYERS)]

        random.shuffle(deck)
        for i, card in enumerate(deck):
            player = players[i % NUM_PLAYERS]
            player.add_card(card)
        if all(card in players[player_num].hand for card in play):
            count += 1
    emp_prob = count / trials
    print("Measured probability ", emp_prob)
    print(
        "Calculated probability ",
        get_probability_for_combination(
            deck,
            14,
            play,
        ),
    )
