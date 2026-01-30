import random

from tichu import HAND_SIZE, NUM_PLAYERS
from tichu.card import NORMAL_CARD_VALUES, Card, Color, DOG, MAH_JONG, PHOENIX, DRAGON
from tichu.combination import Combination
from tichu.player import Player
from tichu.tichu_state import CardPlay, TichuState


class RandomPlayer(Player):
    def get_card_play(self, game_state: TichuState) -> CardPlay:
        player_state = game_state.get_player_state(self.player_idx)
        possible_plays = Combination.possible_plays(
            game_state.current_combination,
            player_state.hand,
            game_state.current_wish,
        )
        if not possible_plays:
            return "pass"
        chosen_play = random.choice(possible_plays)
        argument = None
        if DRAGON in chosen_play:
            argument = random.choice(self.get_opponents())
        if MAH_JONG in chosen_play:
            argument = random.choice(NORMAL_CARD_VALUES)
        return (chosen_play, argument)

    def get_grand_tichu_play(self, game_state: TichuState):
        return random.choice(["pass", "grand_tichu"])

    def get_push_play(self, game_state: TichuState) -> set[int]:
        return set(random.sample(range(HAND_SIZE), NUM_PLAYERS - 1))
