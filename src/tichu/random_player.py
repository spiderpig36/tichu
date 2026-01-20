import random

from tichu import HAND_SIZE, NUM_PLAYERS
from tichu.card import NORMAL_CARD_VALUES
from tichu.combination import Combination
from tichu.player import Player


class RandomPlayer(Player):
    def get_card_play(self):
        possible_plays = Combination.possible_plays(
            self.game_state.current_combination, self.state.hand
        )
        if not possible_plays:
            return "pass"
        chosen_play = random.choice(possible_plays)
        return {self.state.hand.index(card) for card in chosen_play}

    def get_grand_tichu_play(self):
        return random.choice(["pass", "grand_tichu"])

    def get_dragon_stack_recipient_play(self) -> int:
        return random.randint(0, NUM_PLAYERS - 1)

    def get_mahjong_wish_play(self) -> int:
        return random.choice(NORMAL_CARD_VALUES)

    def get_push_play(self) -> set[int]:
        return set(random.sample(range(HAND_SIZE), NUM_PLAYERS - 1))
