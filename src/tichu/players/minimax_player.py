import copy
from enum import Enum
import random

from tichu import HAND_SIZE, NUM_PLAYERS
from tichu.card import DRAGON, MAH_JONG, NORMAL_CARD_VALUES
from tichu.combination import Combination
from tichu.players.player import Player
from tichu.probabilities import get_probability_for_combination
from tichu.tichu import Tichu
from tichu.states.tichu_state import CardPlay, TichuState


class MiniMax(Enum):
    MAX = 1
    MIN = 2


MINI_MAX_DEPTH = 4


class MiniMaxPlayer(Player):
    def get_card_play(self, game_state: TichuState) -> CardPlay:
        game = Tichu.from_state(game_state, simulated_player_idx=self.player_idx)
        return self.mini_max(MiniMax.MAX, game, [game.state], depth=MINI_MAX_DEPTH)[1]

    def mini_max(
        self, type: MiniMax, game: Tichu, game_state_stack: list[TichuState], depth: int
    ) -> tuple[float, CardPlay]:
        game_state = game_state_stack[-1]
        current_player_state = game_state.get_player_state(
            game_state.current_player_idx
        )
        current_hand = current_player_state.hand
        opponent_cards: set = set()
        if game_state.current_player_idx == self.player_idx:
            possible_sets = Combination.possible_plays(
                game_state.current_combination,
                current_hand,
                game_state.current_wish,
            )
        else:
            current_opponent_hand_size = len(current_player_state.hand)
            possible_sets = Combination.possible_plays(
                game_state.current_combination,
                current_player_state.hand,
                game_state.current_wish,
            )
            possible_sets = [
                card_set
                for card_set in possible_sets
                if len(card_set) <= current_opponent_hand_size
            ]
        possible_card_plays: list[CardPlay] = []
        for card_set in possible_sets:
            if DRAGON in card_set:
                if game.state.current_player_idx % 2 == 0:
                    opponents = [1, 3]
                else:
                    opponents = [0, 2]
                for opponent in opponents:
                    possible_card_plays.append((card_set, opponent))
            elif MAH_JONG in card_set:
                for value in NORMAL_CARD_VALUES:
                    possible_card_plays.append((card_set, value))
            else:
                possible_card_plays.append((card_set, None))

        if not game_state.current_wish or not Combination.can_fulfill_wish(
            game_state.current_combination, game_state.current_wish, current_hand
        ):
            possible_card_plays.append("pass")
        if (
            len(current_player_state.hand) == HAND_SIZE
            and not current_player_state.tichu_called
            and not current_player_state.grand_tichu_called
        ):
            possible_card_plays.append("tichu")

        returned_values: list[tuple[float, CardPlay]] = []
        for play in possible_card_plays:
            game.state = copy.deepcopy(game_state)
            game.next_turn(game_state.current_player_idx, play)
            if depth == 1 or game.end_of_round:
                if self.player_idx is None:
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

        sorted_plays = sorted(
            returned_values, key=lambda x: x[0], reverse=(type == MiniMax.MAX)
        )
        expected_value_plays: list[tuple[float, CardPlay]] = []
        if game_state.current_player_idx != self.player_idx:
            hand_size = len(
                game_state.get_player_state(game_state.current_player_idx).hand
            )
            for score, play in sorted_plays:
                if play == "tichu" or play == "pass":
                    expected_value_plays.append(
                        (1 - sum(x[0] for x in expected_value_plays), play)
                    )
                    break
                expected_value_plays.append(
                    (
                        # score
                        # * get_probability_for_combination_excluding_others(
                        #     opponent_cards,
                        #     hand_size,
                        #     play[0],
                        #     [
                        #         play[0]
                        #         for _, play in expected_value_plays
                        #         if play != "pass" and play != "tichu"
                        #     ],
                        # ),
                        score
                        * get_probability_for_combination(
                            opponent_cards,
                            hand_size,
                            play[0],
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
