from functools import reduce
import math
import random
from tichu import NUM_PLAYERS
from tichu.player import Player
from tichu.random_player import RandomPlayer
from tichu.tichu import Tichu
from tqdm import tqdm
from tichu.card import DOG, DRAGON, MAH_JONG, NORMAL_CARD_VALUES, PHOENIX, Card, Color


def get_probability_for_combination(
    remaining_cards: set[Card], hand_size: int, play: set[Card]
):
    if all([card in remaining_cards for card in play]):
        return math.comb(
            len(remaining_cards) - len(play), hand_size - len(play)
        ) / math.comb(len(remaining_cards), hand_size)
    else:
        return 0


def get_probability_for_combination_excluding_others(
    remaining_cards: set[Card],
    hand_size: int,
    play: set[Card],
    impossible_plays: list[set[Card]],
):
    probability_impossible_plays = 1.0 - (
        reduce(
            lambda x, y: x + y,
            [
                math.comb(len(remaining_cards) - len(play), hand_size - len(play))
                for play in impossible_plays
            ],
        )
        / math.comb(len(remaining_cards), hand_size)
    )
    combinations_play = math.comb(
        len(remaining_cards) - len(play), hand_size - len(play)
    )
    for impossible_play in impossible_plays:
        combinations_play -= math.comb(
            len(remaining_cards) - len(play) - len(impossible_play - play),
            hand_size - len(play) - len(impossible_play - play),
        )
    return (
        combinations_play / math.comb(len(remaining_cards), hand_size)
    ) / probability_impossible_plays


if __name__ == "__main__":
    count = 0
    count_excluding = 0
    play = {
        Card(Color.JADE, 2),
        Card(Color.SWORDS, 2),
        Card(Color.STAR, 2),
        Card(Color.PAGODE, 2),
    }
    not_plays = [
        {
            Card(Color.JADE, 2),
            Card(Color.JADE, 3),
            Card(Color.JADE, 4),
            Card(Color.JADE, 5),
            Card(Color.JADE, 6),
        },
        {
            Card(Color.SWORDS, 2),
            Card(Color.SWORDS, 3),
            Card(Color.SWORDS, 4),
            Card(Color.SWORDS, 5),
            Card(Color.SWORDS, 6),
        },
    ]
    player_num = 0
    deck = []
    for color in Color:
        if color == Color.SPECIAL:
            continue
        for value in NORMAL_CARD_VALUES:
            card = Card(color, value)
            deck.append(card)
    deck.extend([DOG, MAH_JONG, PHOENIX, DRAGON])
    trials = 1000000
    excluding_trails = 0
    tichu = Tichu()
    for i in tqdm(range(0, trials)):
        players: list[Player] = [
            RandomPlayer(f"Player {i}") for i in range(NUM_PLAYERS)
        ]
        tichu.new_game(players)

        random.shuffle(deck)
        for i, card in enumerate(deck):
            player = players[i % NUM_PLAYERS]
            player.add_card(card)
        if all(
            not all(card in players[player_num].state.hand for card in not_play)
            for not_play in not_plays
        ):
            excluding_trails += 1
            if all(card in players[player_num].state.hand for card in play):
                count_excluding += 1
        if all(card in players[player_num].state.hand for card in play):
            count += 1
    emp_prob = count / trials
    emp_prob_excluding = count_excluding / excluding_trails
    print("Measured probability ", emp_prob)
    print(
        "Calculated probability ",
        get_probability_for_combination(
            set(deck),
            14,
            play,
        ),
    )
    print("Measured probability excluding others ", emp_prob_excluding)
    print(
        "Calculated probability excluding others ",
        get_probability_for_combination_excluding_others(
            set(deck),
            14,
            play,
            not_plays,
        ),
    )
