from enum import Enum
import random
from typing import Literal

from tichu import HAND_SIZE, NUM_PLAYERS
from tichu.card import DRAGON, MAH_JONG, NORMAL_CARD_VALUES, Card
from tichu.combination import Combination
from tichu.player import Player
from tichu.probabilities import get_probability_for_combination_excluding_others
from tichu.tichu import Tichu
from tichu.tichu_state import CardPlay, TichuState


class MiniMax(Enum):
    MAX = 1
    MIN = 2


class MiniMaxPlayer(Player):
    def get_card_play(self, game_state: TichuState) -> CardPlay:
        return self.mini_max(
            MiniMax.MAX, Tichu.from_state(game_state), [game_state], depth=2
        )[1]

    def mini_max(
        self, type: MiniMax, game: Tichu, game_state_stack: list[TichuState], depth: int
    ) -> tuple[float, CardPlay]:
        game_state = game_state_stack[-1]
        player_state = game_state.get_player_state(game_state.current_player_idx)
        possible_sets = Combination.possible_plays(
            game_state.current_combination,
            player_state.hand,
            game_state.current_wish,
        )
        possible_card_plays: list[CardPlay] = []
        for card_set in possible_sets:
            if DRAGON in card_set:
                for opponent in self.get_opponents():
                    possible_card_plays.append((card_set, opponent))
            elif MAH_JONG in card_set:
                for value in NORMAL_CARD_VALUES:
                    possible_card_plays.append((card_set, value))
            else:
                possible_card_plays.append((card_set, None))

        possible_card_plays.append("pass")
        if (
            len(game.state.get_player_state(game_state.current_player_idx).hand)
            == HAND_SIZE
        ):
            possible_card_plays.append("tichu")

        returned_values: list[tuple[float, CardPlay]] = []
        for play in possible_card_plays:
            game.next_turn(game_state.current_player_idx, play)
            if depth == 1 or game.end_of_round:
                if self.player_idx == None:
                    raise ValueError("Player index not set for MiniMaxPlayer.")
                score = float(game.scoring()[self.player_idx % 2])
            else:
                score, _ = self.mini_max(
                    MiniMax.MIN if type == MiniMax.MAX else MiniMax.MAX,
                    game,
                    game_state_stack + [game.state],
                    depth - 1,
                )
            returned_values.append((score, play))
            game.state = game_state_stack[-1]

        sorted_plays = sorted(
            returned_values, key=lambda x: x[0], reverse=(type == MiniMax.MAX)
        )
        expected_value_plays: list[tuple[float, CardPlay]] = []
        if game.state.current_player_idx != self.player_idx:
            opponent_cards: set = set()
            for idx, player_state in enumerate(game.state.player_states):
                if idx != self.player_idx:
                    opponent_cards |= set(player_state.hand)
            hand_size = len(
                game.state.get_player_state(game.state.current_player_idx).hand
            )
            for score, play in sorted_plays:
                if play == "tichu" or play == "pass":
                    expected_value_plays.append(
                        (1 - sum(x[0] for x in expected_value_plays), play)
                    )
                    break
                expected_value_plays.append(
                    (
                        score
                        * get_probability_for_combination_excluding_others(
                            opponent_cards,
                            hand_size,
                            play[0],
                            [
                                play[0]
                                for _, play in expected_value_plays
                                if play != "pass" and play != "tichu"
                            ],
                        ),
                        play,
                    )
                )
        else:
            expected_value_plays = sorted_plays

        return (
            max(expected_value_plays, key=lambda x: x[0])
            if type == MiniMax.MAX
            else min(expected_value_plays, key=lambda x: x[0])
        )

    def get_grand_tichu_play(self, game_state: TichuState):
        return random.choice(["pass", "grand_tichu"])

    def get_push_play(self, game_state: TichuState) -> set[int]:
        return set(random.sample(range(HAND_SIZE), NUM_PLAYERS - 1))
