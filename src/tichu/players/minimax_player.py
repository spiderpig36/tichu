import copy
from enum import Enum
import random

from tichu import HAND_SIZE, NUM_PLAYERS
from tichu.card import DRAGON, MAH_JONG, NORMAL_CARD_VALUES, Card, build_full_deck
from tichu.combination import Combination
from tichu.players.player import Player
from tichu.probabilities import get_probability_for_combination
from tichu.tichu import Tichu
from tichu.states.tichu_state import CardPlay, TichuState


class MiniMax(Enum):
    MAX = 1
    MIN = 2


class MiniMaxPlayer(Player):
    def _get_unknown_cards(self, game_state: TichuState) -> set[Card]:
        """Compute unseen cards from the perspective of this player.

        Parameters:
            game_state: The state used to derive known and unknown cards.
        Returns:
            set[Card]: Cards that are not in this player's hand and not already played/scored.
        Exceptions raised:
            ValueError: If player index is not set.
        """
        if self.player_idx is None:
            raise ValueError("Player index not set for MiniMaxPlayer.")
        known_cards: set[Card] = set(game_state.get_player_state(self.player_idx).hand)
        known_cards |= set(game_state.card_stack)
        for player_state in game_state.player_states:
            known_cards |= set(player_state.card_stack)
        return set(build_full_deck()) - known_cards

    def _is_hand_assignment_possible(
        self, game_state: TichuState, play: CardPlay
    ) -> bool:
        """Check whether hidden-opponent hand sampling can satisfy a chosen play.

        Parameters:
            game_state: The state in which hands need to be sampled.
            play: The selected play for the current player.
        Returns:
            bool: True if assignment can be constructed, otherwise False.
        Exceptions raised:
            ValueError: If player index is not set.
        """
        if self.player_idx is None:
            raise ValueError("Player index not set for MiniMaxPlayer.")
        unknown_cards = self._get_unknown_cards(game_state)
        hidden_opponent_indices = [
            idx for idx in range(NUM_PLAYERS) if idx != self.player_idx
        ]
        required_cards: set[Card] = set()
        if play != "pass" and play != "tichu":
            required_cards = set(play[0])
            current_player_hand_size = len(
                game_state.get_player_state(game_state.current_player_idx).hand
            )
            if len(required_cards) > current_player_hand_size:
                return False
            if not required_cards.issubset(unknown_cards):
                return False
        available_count = len(unknown_cards - required_cards)
        remaining_needed = 0
        for idx in hidden_opponent_indices:
            target_size = len(game_state.get_player_state(idx).hand)
            if idx == game_state.current_player_idx:
                target_size -= len(required_cards)
            remaining_needed += max(0, target_size)
        return remaining_needed <= available_count

    def _assign_hidden_opponent_hands(
        self, game_state: TichuState, play: CardPlay
    ) -> None:
        """Sample hidden opponent hands while forcing selected play cards into current hand.

        Parameters:
            game_state: The mutable state to update with sampled hidden hands.
            play: The selected play to enforce for the current player.
        Returns:
            None.
        Exceptions raised:
            ValueError: If player index is not set or assignment is impossible.
        """
        if self.player_idx is None:
            raise ValueError("Player index not set for MiniMaxPlayer.")
        hidden_opponent_indices = [
            idx for idx in range(NUM_PLAYERS) if idx != self.player_idx
        ]
        unknown_cards = self._get_unknown_cards(game_state)
        required_cards: set[Card] = set()
        if play != "pass" and play != "tichu":
            required_cards = set(play[0])
        if not required_cards.issubset(unknown_cards):
            raise ValueError(
                "Selected play cards are not available in unknown card pool."
            )
        available_cards = set(unknown_cards - required_cards)
        current_idx = game_state.current_player_idx
        current_target_size = len(game_state.get_player_state(current_idx).hand)
        remaining_current_cards = current_target_size - len(required_cards)
        if remaining_current_cards < 0:
            raise ValueError("Selected play is larger than current player hand size.")
        sampled_current_cards: set[Card] = set()
        if remaining_current_cards > 0:
            sampled_current_cards = set(
                random.sample(list(available_cards), remaining_current_cards)
            )
            available_cards -= sampled_current_cards
        game_state.get_player_state(current_idx).hand = (
            required_cards | sampled_current_cards
        )
        for idx in hidden_opponent_indices:
            if idx == current_idx:
                continue
            target_size = len(game_state.get_player_state(idx).hand)
            sampled_cards: set[Card] = set()
            if target_size > 0:
                sampled_cards = set(random.sample(list(available_cards), target_size))
                available_cards -= sampled_cards
            game_state.get_player_state(idx).hand = sampled_cards

    def get_card_play(self, game_state: TichuState) -> CardPlay:
        return self.mini_max(
            MiniMax.MAX, Tichu.from_state(game_state), [game_state], depth=2
        )[1]

    def mini_max(
        self, type: MiniMax, game: Tichu, game_state_stack: list[TichuState], depth: int
    ) -> tuple[float, CardPlay]:
        game_state = game_state_stack[-1]
        current_player_state = game_state.get_player_state(
            game_state.current_player_idx
        )
        current_hand = current_player_state.hand
        opponent_cards: set = set()
        if game.state.current_player_idx == self.player_idx:
            possible_sets = Combination.possible_plays(
                game_state.current_combination,
                current_hand,
                game_state.current_wish,
            )
        else:
            current_opponent_hand_size = len(current_player_state.hand)
            for idx, player_state in enumerate(game.state.player_states):
                if idx != self.player_idx:
                    opponent_cards |= set(player_state.hand)
            possible_sets = Combination.possible_plays(
                game_state.current_combination,
                opponent_cards,
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
            if (
                game.state.current_player_idx != self.player_idx
                and self._is_hand_assignment_possible(game.state, play)
            ):
                self._assign_hidden_opponent_hands(game.state, play)
            elif game.state.current_player_idx != self.player_idx:
                continue
            game.next_turn(game_state.current_player_idx, play)
            if depth == 1 or game.end_of_round:
                if self.player_idx is None:
                    raise ValueError("Player index not set for MiniMaxPlayer.")
                score = float(game.scoring()[self.player_idx % 2])
            else:
                score, _ = self.mini_max(
                    MiniMax.MIN if type == MiniMax.MAX else MiniMax.MAX,
                    game,
                    game_state_stack + [copy.deepcopy(game.state)],
                    depth - 1,
                )
            returned_values.append((score, play))

        sorted_plays = sorted(
            returned_values, key=lambda x: x[0], reverse=(type == MiniMax.MAX)
        )
        expected_value_plays: list[tuple[float, CardPlay]] = []
        if game.state.current_player_idx != self.player_idx:
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
