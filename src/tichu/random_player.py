import random

from tichu import HAND_SIZE, NUM_PLAYERS
from tichu.card import NORMAL_CARD_VALUES, Card, Color
from tichu.combination import Combination
from tichu.player import Player


class RandomPlayer(Player):
    def get_card_play(self):
        possible_plays = Combination.possible_plays(
            self.game_state.current_combination,
            self.state.hand,
            self.game_state.current_wish,
        )
        if not possible_plays:
            return "pass"
        chosen_play = random.choice(possible_plays)
        return {self.state.hand.index(card) for card in chosen_play}

    def get_grand_tichu_play(self):
        return random.choice(["pass", "grand_tichu"])

    def get_push_play(self) -> set[int]:
        return set(random.sample(range(HAND_SIZE), NUM_PLAYERS - 1))
