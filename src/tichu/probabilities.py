import math
from functools import reduce
from itertools import combinations
import random

from tqdm import tqdm

from tichu import NUM_PLAYERS
from tichu.card import DOG, DRAGON, MAH_JONG, NORMAL_CARD_VALUES, PHOENIX, Card, Color
from tichu.player import Player
from tichu.random_player import RandomPlayer
from tichu.tichu import Tichu


def get_probability_for_combination(
    remaining_cards: set[Card], hand_size: int, play: set[Card]
):
    if all([card in remaining_cards for card in play]) and len(play) <= hand_size:
        return math.comb(
            len(remaining_cards) - len(play), hand_size - len(play)
        ) / math.comb(len(remaining_cards), hand_size)
    return 0


def get_combined_probability_for_combinations(
    remaining_cards: set[Card], hand_size: int, plays: list[set[Card]]
):
    total_probability = 0.0
    for i in range(1, min(len(plays) + 1, hand_size + 1)):
        for play_combination in combinations(plays, i):
            combined_play = reduce(lambda x, y: x.union(y), play_combination)
            probability = get_probability_for_combination(
                remaining_cards, hand_size, combined_play
            )
            total_probability += probability if i % 2 == 1 else -probability
    return total_probability


def get_probability_for_combination_excluding_others(
    remaining_cards: set[Card],
    hand_size: int,
    play: set[Card],
    impossible_plays: list[set[Card]],
):
    probability_impossible_plays = 1.0 - get_combined_probability_for_combinations(
        remaining_cards, hand_size, impossible_plays
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
        Card(Color.JADE, 3),
    }
    not_plays = [
        {
            Card(Color.PAGODE, 2),
        },
        {
            Card(Color.SWORDS, 5),
        },
        {
            Card(Color.STAR, 10),
        },
        {
            Card(Color.JADE, 3),
        },
    ]
    # not_plays = [
    #     {Card(color, i) for color in Color if color != Color.SPECIAL}
    #     for i in NORMAL_CARD_VALUES
    # ]
    player_num = 0
    deck = []
    for color in Color:
        if color == Color.SPECIAL:
            continue
        for value in NORMAL_CARD_VALUES:
            card = Card(color, value)
            deck.append(card)
    deck.extend([DOG, MAH_JONG, PHOENIX, DRAGON])
    trials = 100000
    excluding_trails = 0
    any_trails = 0
    tichu = Tichu()
    for i in tqdm(range(trials)):
        players: list[Player] = [
            RandomPlayer(f"Player {i}") for i in range(NUM_PLAYERS)
        ]
        tichu.new_game(players)

        random.shuffle(deck)
        for j, card in enumerate(deck):
            tichu.state.get_player_state(j % NUM_PLAYERS).hand.append(card)
        if any(
            all(
                card in tichu.state.get_player_state(player_num).hand
                for card in not_play
            )
            for not_play in not_plays
        ):
            any_trails += 1
        if all(
            not all(
                card in tichu.state.get_player_state(player_num).hand
                for card in not_play
            )
            for not_play in not_plays
        ):
            excluding_trails += 1
            if all(
                card in tichu.state.get_player_state(player_num).hand for card in play
            ):
                count_excluding += 1
        if all(card in tichu.state.get_player_state(player_num).hand for card in play):
            count += 1
    emp_prob = count / trials
    emp_prob_excluding = count_excluding / excluding_trails
    emp_prob_any = any_trails / trials
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
    print("Measured probability of any not play ", emp_prob_any)
    print(
        "Calculated probability of any not play ",
        get_combined_probability_for_combinations(
            set(deck),
            14,
            not_plays,
        ),
    )
