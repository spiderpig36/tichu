import logging
import random

from tichu import (
    GRAND_TICHU_HAND_SIZE,
    GRAND_TICHU_SCORE,
    HAND_SIZE,
    MATCH_SCORE,
    NUM_PLAYERS,
    TICHU_SCORE,
)
from tichu.card import (
    DOG,
    DRAGON,
    MAH_JONG,
    NORMAL_CARD_VALUES,
    PHOENIX,
    Card,
    build_full_deck,
)
from tichu.combination import Combination, CombinationType
from tichu.players.player import Player
from tichu.states.player_state import PlayerState
from tichu.states.tichu_state import CardPlay, TichuState


class TichuError(Exception):
    """Base class for Tichu-related exceptions."""


class InvalidPlayError(TichuError):
    """Raised when a player makes an invalid play."""


class Tichu:
    def __init__(
        self,
        goal_score: int = 1000,
        seed: int | None = None,
    ):
        self.goal_score = goal_score
        self.random = random.Random(seed)

    def new_game(self, players: list[Player]):
        self.state = TichuState()
        self.state.player_states = [PlayerState() for _ in range(NUM_PLAYERS)]
        if len(players) != NUM_PLAYERS:
            raise ValueError("Number of players must match NUM_PLAYERS")
        self.players = players
        for idx, player in enumerate(self.players):
            player.set_game(idx)

    @classmethod
    def from_state(cls, state: TichuState) -> "Tichu":
        tichu = cls()
        tichu.state = state
        return tichu

    def push_cards(self, player_idx: int, card_indices: set[int]) -> bool:
        player_state = self.state.get_player_state(player_idx)
        player_state.push_selection = card_indices

        if all(
            len(self.state.get_player_state(i).push_selection) > 0
            for i in range(NUM_PLAYERS)
        ):
            self._execute_push_exchange()
            return True
        return False

    def _execute_push_exchange(self):
        cards_for_players = [[], [], [], []]
        for player_idx in range(NUM_PLAYERS):
            player_state = self.state.get_player_state(player_idx)
            card_indices = player_state.push_selection
            sorted_hand = player_state.get_sorted_hand()
            cards_to_push = [
                card for card_idx, card in enumerate(sorted_hand) if card_idx in card_indices
            ]
            for card in cards_to_push:
                player_state.hand.remove(card)
            cards_for_players[(player_idx - 1) % NUM_PLAYERS].append(cards_to_push[0])
            cards_for_players[(player_idx + 2) % NUM_PLAYERS].append(cards_to_push[1])
            cards_for_players[(player_idx + 1) % NUM_PLAYERS].append(cards_to_push[2])

        for player_idx in range(NUM_PLAYERS):
            player_state = self.state.get_player_state(player_idx)
            for card in cards_for_players[player_idx]:
                player_state.hand.add(card)
            player_state.push_selection.clear()

        self.state.current_player_idx = next(
            i
            for i, player_state in enumerate(self.state.player_states)
            if MAH_JONG in player_state.hand
        )
        self.state.winning_player_idx = self.state.current_player_idx

    def start_new_round(self):
        self.state.play_log.clear()
        self.state.current_round += 1
        for idx, player in enumerate(self.players):
            player.reset_for_new_round(self.state)
        deck = build_full_deck()

        self.random.shuffle(deck)
        for i, card in enumerate(deck):
            player_idx = i % NUM_PLAYERS
            player_state = self.state.get_player_state(player_idx)
            player_state.hand.add(card)
            if (
                len(player_state.hand) == GRAND_TICHU_HAND_SIZE
                and self.players[player_idx].get_grand_tichu_play(self.state)
                == "grand_tichu"
            ):
                player_state.grand_tichu_called = True

        self.state.current_combination = None
        self.state.current_wish = None
        self.state.card_stack.clear()
        self.state.player_rankings.clear()

    @property
    def current_player(self) -> Player:
        return self.players[self.state.current_player_idx]

    @property
    def end_of_round(self) -> bool:
        return len(self.state.player_rankings) == NUM_PLAYERS - 1 or (
            len(self.state.player_rankings) == NUM_PLAYERS / 2
            and self.state.player_rankings[0] % 2 == self.state.player_rankings[1] % 2
        )

    def add_play_log_entry(self, play: CardPlay):
        self.state.play_log.append((self.state.current_player_idx, play))

    def next_turn(self, player_idx: int, card_play: CardPlay):
        player_state = self.state.get_player_state(player_idx)
        current_hand = player_state.hand
        if card_play == "pass":
            if player_idx != self.state.current_player_idx:
                raise InvalidPlayError("Only the current player can pass.")
            if self.state.current_wish is not None and Combination.can_fulfill_wish(
                self.state.current_combination,
                self.state.current_wish,
                current_hand,
            ):
                msg = f"You can fulfill the wish for card value {self.state.current_wish} and cannot pass."
                raise InvalidPlayError(msg)
            logging.info("Current player has passed.")
            self.add_play_log_entry(card_play)
            player_state.has_passed = True
            if all(
                self.state.get_player_state(idx).has_passed
                for idx in range(NUM_PLAYERS)
                if idx != self.state.winning_player_idx
                and idx not in self.state.player_rankings
            ):
                logging.info(
                    "All other players have passed. Resetting current combination."
                )
                for ps in self.state.player_states:
                    ps.has_passed = False
                if (
                    self.state.current_combination
                    and self.state.current_combination.combination_type
                    == CombinationType.SINGLE
                    and self.state.current_combination.value == DRAGON.value
                ):
                    logging.info(
                        "Winning player wins the single card round and collects the card stack."
                    )
                    if self.state.dragon_stack_recipient_id is None:
                        msg = "Dragon stack recipient id is not set."
                        raise RuntimeError(msg)

                    self.state.get_player_state(
                        self.state.dragon_stack_recipient_id
                    ).card_stack.update(self.state.card_stack)
                else:
                    self.state.get_player_state(
                        self.state.winning_player_idx
                    ).card_stack.update(self.state.card_stack)
                self.state.current_combination = None
                self.state.card_stack.clear()
        elif card_play == "tichu":
            if player_state.grand_tichu_called:
                msg = "Grand Tichu was already called."
                raise InvalidPlayError(msg)
            if len(player_state.hand) != HAND_SIZE:
                msg = (
                    "Tichu can only be called at the start of a turn with a full hand."
                )
                raise InvalidPlayError(msg)
            logging.info("Current player has called Tichu!")
            player_state.tichu_called = True
            self.add_play_log_entry(card_play)
            return
        else:
            cards, play_argument = card_play
            if not all([card in current_hand for card in cards]):
                msg = "Play contains cards that are not in the current players hand."
                raise InvalidPlayError(msg)

            next_combination = Combination.from_cards(list(cards))
            if next_combination is None:
                msg = "Cards are not a valid combination."
                raise InvalidPlayError(msg)
            if (
                self.state.current_combination is not None
                and not next_combination.can_be_played_on(
                    self.state.current_combination
                )
            ):
                msg = "Played combination must be of the same kind as the current combination and higher than the current combination."
                raise InvalidPlayError(msg)
            if (
                next_combination.combination_type
                not in (CombinationType.BOMB, CombinationType.STRAIGHT_BOMB)
                and player_idx != self.state.current_player_idx
            ):
                raise InvalidPlayError(
                    "Only the current player can play this combination."
                )
            self.state.current_player_idx = player_idx
            if self.state.current_wish is not None:
                if self.state.current_wish in [card.value for card in cards]:
                    logging.info(
                        f"Current player has fulfilled the wish for card value {self.state.current_wish}."
                    )
                    self.state.current_wish = None
                elif self.state.current_wish in [
                    card.value for card in self.state.get_player_state(player_idx).hand
                ]:
                    if Combination.can_fulfill_wish(
                        self.state.current_combination,
                        self.state.current_wish,
                        self.state.get_player_state(player_idx).hand,
                    ):
                        msg = f"The played combination does not fulfill the wish for card value {self.state.current_wish}."
                        raise InvalidPlayError(msg)

            for reset_player_idx in range(NUM_PLAYERS):
                self.state.get_player_state(reset_player_idx).has_passed = False
            self.state.current_combination = next_combination
            self.state.winning_player_idx = player_idx
            for card in cards:
                player_state.hand.remove(card)
            if len(player_state.hand) == 0:
                logging.info(
                    "Current player has played all their cards and finished the round!"
                )
                self.state.player_rankings.append(player_idx)
            self.state.card_stack.extend(list(cards))

            self.add_play_log_entry(card_play)
            logging.info(", ".join([str(card) for card in cards]))

            if (
                self.state.current_combination.combination_type
                == CombinationType.SINGLE
            ):
                match self.state.current_combination.value:
                    case DOG.value:
                        logging.info(
                            "Current player played the Dog and passes the turn to their teammate."
                        )
                        self.state.current_player_idx = (player_idx + 2) % NUM_PLAYERS
                        return
                    case PHOENIX.value:
                        self.state.current_combination.value = (
                            self.state.card_stack[-2].value + 0.5
                            if len(self.state.card_stack) > 1
                            else NORMAL_CARD_VALUES[0]
                        )
                    case DRAGON.value:
                        if play_argument is None:
                            msg = "Dragon stack recipient id must be provided when playing the Dragon."
                            raise InvalidPlayError(msg)
                        self.state.dragon_stack_recipient_id = play_argument
                        if (
                            self.state.dragon_stack_recipient_id < 0
                            or self.state.dragon_stack_recipient_id >= NUM_PLAYERS
                        ):
                            msg = f"Dragon stack recipient id must be between 0 and {NUM_PLAYERS - 1}."
                            raise InvalidPlayError(msg)
                        if (
                            self.state.dragon_stack_recipient_id % 2
                            == self.state.winning_player_idx % 2
                        ):
                            msg = "Dragon stack recipient cannot be on the same team as the player who played the Dragon."
                            raise InvalidPlayError(msg)
                    case MAH_JONG.value:
                        if (
                            play_argument is None
                            or play_argument not in NORMAL_CARD_VALUES
                        ):
                            msg = "A valid card value must be provided when playing the Mah Jong."
                            raise InvalidPlayError(msg)
                        self.state.current_wish = play_argument
                        logging.info(
                            f"Current player wishes for card value {self.state.current_wish}."
                        )

        next_player_idx = self.state.current_player_idx
        while (
            next_player_idx == self.state.current_player_idx
            or next_player_idx in self.state.player_rankings
        ):
            next_player_idx = (next_player_idx + 1) % NUM_PLAYERS
        self.state.current_player_idx = next_player_idx

    def scoring(self) -> list[int]:
        team_scores = [0, 0]
        if len(self.state.player_rankings) > 0:
            for i, player_state in enumerate(self.state.player_states):
                if player_state.tichu_called or player_state.grand_tichu_called:
                    if self.state.player_rankings[0] == i:
                        team_scores[i % 2] += (
                            GRAND_TICHU_SCORE
                            if player_state.grand_tichu_called
                            else TICHU_SCORE
                        )
                    else:
                        team_scores[i % 2] -= (
                            GRAND_TICHU_SCORE
                            if player_state.grand_tichu_called
                            else TICHU_SCORE
                        )
        if (
            len(self.state.player_rankings) == NUM_PLAYERS / 2
            and self.state.player_rankings[0] % 2 == self.state.player_rankings[1] % 2
        ):
            team_scores[self.state.player_rankings[0] % 2] += MATCH_SCORE
        else:
            if self.end_of_round:
                loosing_player = next(
                    i for i in range(NUM_PLAYERS) if i not in self.state.player_rankings
                )
                team_scores[self.state.player_rankings[0] % 2] += (
                    Card.count_card_scores(
                        self.state.get_player_state(loosing_player).card_stack
                    )
                )
                team_scores[(loosing_player + 1) % 2] += Card.count_card_scores(
                    self.state.get_player_state(loosing_player).hand
                )
            for i, player_state in enumerate(self.state.player_states):
                team_id = i % 2
                team_scores[team_id] += Card.count_card_scores(player_state.card_stack)
        return team_scores

    def end_round_scoring(self):
        team_scores = self.scoring()
        for i in range(len(team_scores)):
            self.state.scores[i] += team_scores[i]
            logging.info(
                f"Team {i} scored {team_scores[i]} points this round. Total score: {self.state.scores[i]}"
            )
