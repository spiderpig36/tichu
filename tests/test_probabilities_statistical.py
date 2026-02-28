import math
import random

import pytest

from tichu.card import DRAGON, PHOENIX, Card, Color, build_full_deck
from tichu.probabilities import (
    get_combined_probability_for_combinations,
    get_probability_for_combination,
    get_probability_for_combination_excluding_others,
)


HAND_SIZE = 14
TRIALS = 150_000
TARGET_FAILURE_PROBABILITY = 0.001
MIN_CONDITIONAL_SAMPLES = 2_000

PLAY_CASES: list[set[Card]] = [
    {Card(Color.JADE, 3)},
    {Card(Color.JADE, 10), Card(Color.SWORDS, 10)},
    {Card(Color.JADE, 2), Card(Color.JADE, 3), Card(Color.JADE, 4)},
]

CONDITIONAL_CASES: list[tuple[set[Card], list[set[Card]]]] = [
    (
        {Card(Color.JADE, 3)},
        [{Card(Color.JADE, 3)}],
    ),
    (
        {Card(Color.JADE, 10), Card(Color.SWORDS, 10)},
        [{DRAGON}, {PHOENIX}],
    ),
    (
        {Card(Color.JADE, 2), Card(Color.JADE, 3), Card(Color.JADE, 4)},
        [{Card(Color.SWORDS, 5), Card(Color.PAGODE, 5)}, {Card(Color.STAR, 7)}],
    ),
]

COMBINED_CASES: list[list[set[Card]]] = [
    [{Card(Color.JADE, 3)}],
    [{DRAGON}, {PHOENIX}],
    [{Card(Color.SWORDS, 5), Card(Color.PAGODE, 5)}, {Card(Color.STAR, 7)}],
]

def _hoeffding_radius(sample_size: int, alpha: float) -> float:
    """Summary: Compute a two-sided Hoeffding confidence radius for a Bernoulli mean.
    https://en.wikipedia.org/wiki/Hoeffding%27s_inequality#Confidence_intervals

    Parameters:
        sample_size: The number of independent Bernoulli samples.
        alpha: The two-sided failure probability bound for this estimate.
    Returns:
        float: The absolute error radius epsilon.
    Exceptions raised:
        ValueError: If sample_size is not positive or alpha is outside (0, 1).
    """
    if sample_size <= 0:
        raise ValueError("Sample size must be greater than zero.")
    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1.")
    return math.sqrt(math.log(2 / alpha) / (2 * sample_size))


def _estimate_empirical_probabilities(
    play: set[Card], excluded_plays: list[set[Card]], trials: int, seed: int
) -> tuple[float, float, float, int]:
    """Summary: Estimate target probabilities by Monte Carlo sampling random hands.

    Parameters:
        play: The card set defining the play event.
        excluded_plays: A list of card sets treated as excluded events.
        trials: Number of sampled hands.
        seed: Random seed for reproducible sampling.
    Returns:
        tuple[float, float, float, int]: Estimated P(play), P(play | none(excluded_plays)),
        P(any(excluded_plays)), and the conditional sample count.
    Exceptions raised:
        ValueError: If no conditional samples are observed.
    """
    deck = build_full_deck()
    rng = random.Random(seed)
    play_hits = 0
    conditional_hits = 0
    any_excluded_hits = 0
    conditional_samples = 0
    for _ in range(trials):
        hand = set(rng.sample(deck, HAND_SIZE))
        play_in_hand = play.issubset(hand)
        any_excluded_play_in_hand = any(
            excluded_play.issubset(hand) for excluded_play in excluded_plays
        )
        if play_in_hand:
            play_hits += 1
        if any_excluded_play_in_hand:
            any_excluded_hits += 1
        else:
            conditional_samples += 1
            if play_in_hand:
                conditional_hits += 1
    if conditional_samples == 0:
        raise ValueError("No conditional samples were observed.")
    return (
        play_hits / trials,
        conditional_hits / conditional_samples,
        any_excluded_hits / trials,
        conditional_samples,
    )


def _estimate_empirical_play_probability(
    play: set[Card], trials: int, seed: int
) -> float:
    """Summary: Estimate P(play) from Monte Carlo samples of random hands.

    Parameters:
        play: The card set defining the play event.
        trials: Number of sampled hands.
        seed: Random seed for reproducible sampling.
    Returns:
        float: The empirical estimate of P(play).
    Exceptions raised:
        None.
    """
    empirical_play, _, _, _ = _estimate_empirical_probabilities(
        play=play,
        excluded_plays=[],
        trials=trials,
        seed=seed,
    )
    return empirical_play


def _estimate_empirical_combined_probability(
    plays: list[set[Card]], trials: int, seed: int
) -> float:
    """Summary: Estimate P(any(plays)) from Monte Carlo samples of random hands.

    Parameters:
        plays: The list of card sets defining the union event.
        trials: Number of sampled hands.
        seed: Random seed for reproducible sampling.
    Returns:
        float: The empirical estimate of P(any(plays)).
    Exceptions raised:
        None.
    """
    _, _, empirical_any_play, _ = _estimate_empirical_probabilities(
        play=set(),
        excluded_plays=plays,
        trials=trials,
        seed=seed,
    )
    return empirical_any_play


def _get_alpha_each() -> float:
    """Summary: Compute the per-assertion alpha used for family-wise confidence control.

    Parameters:
        None.
    Returns:
        float: The Bonferroni-adjusted per-assertion alpha.
    Exceptions raised:
        None.
    """
    total_assertions = len(PLAY_CASES) + len(CONDITIONAL_CASES) + len(COMBINED_CASES)
    return TARGET_FAILURE_PROBABILITY / total_assertions


@pytest.mark.parametrize("play", PLAY_CASES)
def test_probability_for_combination_matches_theory(play: set[Card]) -> None:
    """Summary: Validate P(play) against simulation with Hoeffding bounds.

    Parameters:
        play: The card set defining the play event.
    Returns:
        None.
    Exceptions raised:
        AssertionError: If the empirical estimate deviates beyond the confidence bound.
    """
    deck = set(build_full_deck())
    alpha_each = _get_alpha_each()
    theoretical_play = get_probability_for_combination(deck, HAND_SIZE, play)
    empirical_play = _estimate_empirical_play_probability(
        play=play, trials=TRIALS, seed=42
    )
    play_radius = _hoeffding_radius(TRIALS, alpha_each)
    assert abs(empirical_play - theoretical_play) <= play_radius


@pytest.mark.parametrize("play,excluded_plays", CONDITIONAL_CASES)
def test_probability_for_combination_excluding_others_matches_theory(
    play: set[Card], excluded_plays: list[set[Card]]
) -> None:
    """Summary: Validate P(play | none(excluded_plays)) against simulation with Hoeffding bounds.

    Parameters:
        play: The card set defining the play event.
        excluded_plays: The excluded card-set events used in the conditional probability.
    Returns:
        None.
    Exceptions raised:
        AssertionError: If the empirical estimate deviates beyond the confidence bound.
    """
    deck = set(build_full_deck())
    alpha_each = _get_alpha_each()
    theoretical_conditional = get_probability_for_combination_excluding_others(
        deck, HAND_SIZE, play, excluded_plays
    )
    _, empirical_conditional, _, conditional_samples = (
        _estimate_empirical_probabilities(
            play=play,
            excluded_plays=excluded_plays,
            trials=TRIALS,
            seed=42,
        )
    )
    assert conditional_samples >= MIN_CONDITIONAL_SAMPLES
    conditional_radius = _hoeffding_radius(conditional_samples, alpha_each)
    assert abs(empirical_conditional - theoretical_conditional) <= conditional_radius


@pytest.mark.parametrize("plays", COMBINED_CASES)
def test_combined_probability_for_combinations_matches_theory(
    plays: list[set[Card]],
) -> None:
    """Summary: Validate P(any(plays)) against simulation with Hoeffding bounds.

    Parameters:
        plays: The card-set events for union probability validation.
    Returns:
        None.
    Exceptions raised:
        AssertionError: If the empirical estimate deviates beyond the confidence bound.
    """
    deck = set(build_full_deck())
    alpha_each = _get_alpha_each()
    theoretical_any_excluded = get_combined_probability_for_combinations(
        deck, HAND_SIZE, plays
    )
    empirical_any_excluded = _estimate_empirical_combined_probability(
        plays=plays,
        trials=TRIALS,
        seed=42,
    )
    any_excluded_radius = _hoeffding_radius(TRIALS, alpha_each)
    assert abs(empirical_any_excluded - theoretical_any_excluded) <= any_excluded_radius
