import logging
import random
import sys
from typing import IO, Literal

from tichu import (
    GRAND_TICHU_HAND_SIZE,
    GRAND_TICHU_SCORE,
    HAND_SIZE,
    MATCH_SCORE,
    NUM_PLAYERS,
    TICHU_SCORE,
)
from tichu.card import NORMAL_CARD_VALUES, Card, Color, SpecialCard
from tichu.combination import Combination, CombinationType
from tichu.human_player import HumanPlayer
from tichu.llm_player import LLMPlayer
from tichu.random_player import RandomPlayer
from tichu.player import Player
from tichu.tichu_state import Play, TichuState


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
        if len(players) != NUM_PLAYERS:
            raise ValueError("Number of players must match NUM_PLAYERS")
        self.players = players
        for player in self.players:
            player.set_game(self.state)

    def start_new_round(self):
        self.state.play_log.clear()
        self.state.current_round += 1
        for player in self.players:
            player.reset_for_new_round()
        deck = []
        for color in Color:
            if color == Color.SPECIAL:
                continue
            for value in NORMAL_CARD_VALUES:
                card = Card(color, value)
                deck.append(card)
        deck.extend([Card(Color.SPECIAL, card.value) for card in SpecialCard])

        self.random.shuffle(deck)
        for i, card in enumerate(deck):
            player = self.players[i % NUM_PLAYERS]
            player.add_card(card)
            if (
                len(player.state.hand) == GRAND_TICHU_HAND_SIZE
                and player.get_grand_tichu_play() == "grand_tichu"
            ):
                player.state.grand_tichu_called = True

        for player in self.players:
            player.state.hand.sort(key=lambda c: c.value)

        self.push_cards()

        self.state.current_player_idx = next(
            i for i, p in enumerate(self.players) if p.has_mahjong()
        )
        self.state.winning_player_idx = self.state.current_player_idx
        self.state.current_combination = None
        self.state.current_wish = None
        self.state.card_stack.clear()
        self.state.player_rankings.clear()

    @property
    def current_player(self) -> Player:
        return self.players[self.state.current_player_idx]

    @property
    def winning_player(self) -> Player:
        return self.players[self.state.winning_player_idx]

    @property
    def end_of_round(self) -> bool:
        return len(self.state.player_rankings) == NUM_PLAYERS - 1 or (
            len(self.state.player_rankings) == NUM_PLAYERS / 2
            and self.state.player_rankings[0] % 2 == self.state.player_rankings[1] % 2
        )

    def push_cards(self):
        cards_for_players = [[], [], [], []]
        for player_idx, player in enumerate(self.players):
            card_indices = player.get_push_play()
            cards_to_push = [
                card
                for card_idx, card in enumerate(player.state.hand)
                if card_idx in card_indices
            ]
            for card in cards_to_push:
                player.play_card(card)
            cards_for_players[(player_idx - 1) % NUM_PLAYERS].append(cards_to_push[0])
            cards_for_players[(player_idx + 2) % NUM_PLAYERS].append(cards_to_push[1])
            cards_for_players[(player_idx + 1) % NUM_PLAYERS].append(cards_to_push[2])
        for player_idx, player in enumerate(self.players):
            for card in cards_for_players[player_idx]:
                player.add_card(card)
            player.state.hand.sort(key=lambda c: c.value)

    def add_play_log_entry(self, play: Play):
        self.state.play_log.append((self.state.current_player_idx, play))

    def next_turn(self):
        if self.state.current_player_idx in self.state.player_rankings:
            logging.info(
                f"{self.current_player.name} has no cards left and is skipped!"
            )
        else:
            current_hand = self.current_player.state.hand
            play = self.current_player.get_card_play()
            if play == "pass":
                if (
                    self.state.current_wish is not None
                    and Combination.can_fulfill_wish(
                        self.state.current_combination,
                        self.state.current_wish,
                        current_hand,
                    )
                ):
                    msg = f"You can fulfill the wish for card value {self.state.current_wish} and cannot pass."
                    raise InvalidPlayError(msg)
                logging.info(f"{self.current_player.name} has passed.")
                self.add_play_log_entry(play)
                self.current_player.state.has_passed = True
                if all(
                    player.state.has_passed
                    for idx, player in enumerate(self.players)
                    if player != self.winning_player
                    and idx not in self.state.player_rankings
                ):
                    logging.info(
                        "All other players have passed. Resetting current combination."
                    )
                    for player in self.players:
                        player.state.has_passed = False
                    if (
                        self.state.current_combination
                        and self.state.current_combination.combination_type
                        == CombinationType.SINGLE
                        and self.state.current_combination.value
                        == SpecialCard.DRAGON.value
                    ):
                        logging.info(
                            f"{self.winning_player.name} wins the single card round and collects the card stack."
                        )
                        recipient_id = None
                        while not recipient_id:
                            recipient_id = (
                                self.winning_player.get_dragon_stack_recipient_play()
                            )
                            if recipient_id < 0 or recipient_id >= NUM_PLAYERS:
                                logging.info("Invalid player index. Try again.")
                                recipient_id = None
                            elif recipient_id % 2 == self.state.winning_player_idx % 2:
                                logging.info(
                                    "Cannot give the dragon stack to your teammate. Try again."
                                )
                                recipient_id = None

                        self.players[recipient_id].state.card_stack.extend(
                            self.state.card_stack
                        )
                    else:
                        self.winning_player.state.card_stack.extend(
                            self.state.card_stack
                        )
                    self.state.current_combination = None
                    self.state.card_stack.clear()
            elif play == "tichu":
                if self.current_player.state.grand_tichu_called:
                    msg = "Grand Tichu was already called."
                    raise InvalidPlayError(msg)
                if len(self.current_player.state.hand) != HAND_SIZE:
                    msg = "Tichu can only be called at the start of a turn with a full hand."
                    raise InvalidPlayError(msg)
                logging.info(f"{self.current_player.name} has called Tichu!")
                self.current_player.state.tichu_called = True
                self.add_play_log_entry(play)
                return
            else:
                try:
                    played_cards = [current_hand[idx] for idx in play]
                except IndexError as ie:
                    msg = "One or more card indices are out of range."
                    raise InvalidPlayError(msg) from ie

                next_combination = Combination.from_cards(played_cards)
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
                if self.state.current_wish is not None:
                    if self.state.current_wish in [card.value for card in played_cards]:
                        logging.info(
                            f"{self.current_player.name} has fulfilled the wish for card value {self.state.current_wish}."
                        )
                        self.state.current_wish = None
                    elif self.state.current_wish in [
                        card.value for card in self.current_player.state.hand
                    ]:
                        if Combination.can_fulfill_wish(
                            self.state.current_combination,
                            self.state.current_wish,
                            self.current_player.state.hand,
                        ):
                            msg = f"The played combination does not fulfill the wish for card value {self.state.current_wish}."
                            raise InvalidPlayError(msg)

                for player in self.players:
                    player.state.has_passed = False
                self.state.current_combination = next_combination
                self.state.winning_player_idx = self.state.current_player_idx
                for card in played_cards:
                    self.current_player.play_card(card)
                if len(self.current_player.state.hand) == 0:
                    logging.info(
                        f"{self.current_player.name} has played all their cards and finished the round!"
                    )
                    self.state.player_rankings.append(self.state.current_player_idx)
                self.state.card_stack.extend(played_cards)

                self.add_play_log_entry(play)
                logging.info(", ".join([str(card) for card in played_cards]))

                if (
                    self.state.current_combination.combination_type
                    == CombinationType.SINGLE
                    and self.state.current_combination.value == SpecialCard.DOG.value
                ):
                    logging.info(
                        f"{self.current_player.name} played the Dog and passes the turn to their teammate."
                    )
                    self.state.current_player_idx = (
                        self.state.current_player_idx + 2
                    ) % NUM_PLAYERS
                    return
                if (
                    self.state.current_combination.combination_type
                    == CombinationType.SINGLE
                    and self.state.current_combination.value
                    == SpecialCard.PHOENIX.value
                ):
                    self.state.current_combination.value = (
                        self.state.card_stack[-2].value + 0.5
                        if len(self.state.card_stack) > 1
                        else NORMAL_CARD_VALUES[0]
                    )
                if (
                    self.state.current_combination.combination_type
                    == CombinationType.SINGLE
                    and self.state.current_combination.value
                    == SpecialCard.MAH_JONG.value
                ):
                    self.state.current_wish = (
                        self.current_player.get_mahjong_wish_play()
                    )
                    logging.info(
                        f"{self.current_player.name} wishes for card value {self.state.current_wish}."
                    )

        self.state.current_player_idx = (
            self.state.current_player_idx + 1
        ) % NUM_PLAYERS

    def end_round_scoring(self):
        team_scores = [0, 0]
        for i, player in enumerate(self.players):
            if player.state.tichu_called or player.state.grand_tichu_called:
                if self.state.player_rankings[0] == i:
                    team_scores[i % 2] += (
                        GRAND_TICHU_SCORE
                        if player.state.grand_tichu_called
                        else TICHU_SCORE
                    )
                else:
                    team_scores[i % 2] -= (
                        GRAND_TICHU_SCORE
                        if player.state.grand_tichu_called
                        else TICHU_SCORE
                    )
        if (
            len(self.state.player_rankings) == NUM_PLAYERS / 2
            and self.state.player_rankings[0] % 2 == self.state.player_rankings[1] % 2
        ):
            team_scores[self.state.player_rankings[0] % 2] += MATCH_SCORE
        else:
            loosing_player = next(
                i for i in range(NUM_PLAYERS) if i not in self.state.player_rankings
            )
            self.players[self.state.player_rankings[0]].state.card_stack.extend(
                self.players[loosing_player].state.card_stack
            )
            team_scores[(loosing_player + 1) % 2] += Card.count_card_scores(
                self.players[loosing_player].state.hand
            )
            for i, player in enumerate(self.players):
                team_id = i % 2
                team_scores[team_id] += Card.count_card_scores(player.state.card_stack)
        for i in range(len(team_scores)):
            self.state.scores[i] += team_scores[i]
            logging.info(
                f"Team {i} scored {team_scores[i]} points this round. Total score: {self.state.scores[i]}"
            )


if __name__ == "__main__":
    players: list[Player] = [
        RandomPlayer(f"Player RANDOM {i}") for i in range(NUM_PLAYERS)
    ]
    # players.append(LLMPlayer("Player LLM"))
    game = Tichu()
    game.new_game(players)
    game.start_new_round()
    while not game.end_of_round:
        print(game.state)
        print(game.current_player)
        print()
        try:
            game.next_turn()
        except InvalidPlayError as e:
            logging.info(f"Invalid play: {e}")
            continue
