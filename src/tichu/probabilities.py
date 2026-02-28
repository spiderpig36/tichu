import math
from functools import reduce
from itertools import combinations
from typing import Literal

from tichu.card import Card


def get_probability_for_combination(
    remaining_cards: set[Card], hand_size: int, play: set[Card]
) -> float | Literal[0]:
    if all([card in remaining_cards for card in play]) and len(play) <= hand_size:
        return math.comb(
            len(remaining_cards) - len(play), hand_size - len(play)
        ) / math.comb(len(remaining_cards), hand_size)
    return 0


def get_combined_probability_for_combinations(
    remaining_cards: set[Card], hand_size: int, plays: list[set[Card]]
) -> float:
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
) -> float:
    probability_impossible_plays = 1.0 - get_combined_probability_for_combinations(
        remaining_cards, hand_size, impossible_plays
    )
    combinations_play = get_probability_for_combination(
        remaining_cards, hand_size, play
    )
    and_impossible_plays = [
        impossible_play.union(play) for impossible_play in impossible_plays
    ]
    combinations_play -= get_combined_probability_for_combinations(
        remaining_cards, hand_size, and_impossible_plays
    )

    return (combinations_play) / probability_impossible_plays
