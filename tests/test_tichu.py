from unittest.mock import MagicMock, patch

import pytest

from tichu.card import Card, Color, DOG, MAH_JONG, PHOENIX, DRAGON
from tichu.combination import Combination, CombinationType
from tichu.player import Player
from tichu.random_player import RandomPlayer
from tichu.tichu import (
    GRAND_TICHU_SCORE,
    HAND_SIZE,
    NUM_PLAYERS,
    TICHU_SCORE,
    InvalidPlayError,
    Tichu,
)


@pytest.fixture
def game() -> Tichu:
    """Create a game instance and start a new round."""
    players: list[Player] = [RandomPlayer(f"Player {i}") for i in range(NUM_PLAYERS)]
    game_instance = Tichu(seed=42)
    game_instance.new_game(players)
    with patch(
        "tichu.random_player.RandomPlayer.get_grand_tichu_play", return_value="pass"
    ):
        with patch(
            "tichu.random_player.RandomPlayer.get_push_play", return_value={0, 1, 2}
        ):
            game_instance.start_new_round()
    return game_instance


class TestStartNewRound:
    def test_grand_tichu_called(self):
        players: list[Player] = [
            RandomPlayer(f"Player {i}") for i in range(NUM_PLAYERS)
        ]
        game = Tichu(seed=42)
        game.new_game(players)
        with patch(
            "tichu.random_player.RandomPlayer.get_grand_tichu_play",
            side_effect=["grand_tichu", "pass", "pass", "pass"],
        ):
            with patch(
                "tichu.random_player.RandomPlayer.get_push_play", return_value={0, 1, 2}
            ):
                game.start_new_round()

        assert game.state.get_player_state(0).grand_tichu_called
        assert not game.state.get_player_state(1).grand_tichu_called
        assert not game.state.get_player_state(2).grand_tichu_called
        assert not game.state.get_player_state(3).grand_tichu_called

    def test_cards_are_dealt(self, game: Tichu):
        for player_idx in range(NUM_PLAYERS):
            assert len(game.state.get_player_state(player_idx).hand) == HAND_SIZE


class TestNextTurnPass:
    """Tests for player passing in next_turn."""

    def test_player_passes_single_card(self, game: Tichu):
        """Test a player passing during their turn."""

        game.state.current_player_idx = 0
        initial_player_id = game.state.current_player_idx

        with patch.object(game.current_player, "get_card_play", return_value="pass"):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(initial_player_id, play)

        assert game.state.get_player_state(initial_player_id).has_passed is True
        assert game.state.current_player_idx == (initial_player_id + 1) % NUM_PLAYERS

    def test_all_players_pass_resets_combination(self, game: Tichu):
        """Test that when all players except winner pass, combination resets."""

        game.state.current_player_idx = 1
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 5

        with patch(
            "tichu.random_player.RandomPlayer.get_card_play", return_value="pass"
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(1, play)
            play = game.current_player.get_card_play(game.state)
            game.next_turn(game.state.current_player_idx, play)
            play = game.current_player.get_card_play(game.state)
            game.next_turn(game.state.current_player_idx, play)

        assert game.state.current_combination is None
        assert game.state.current_player_idx == 0
        assert all(
            not game.state.get_player_state(i).has_passed for i in range(NUM_PLAYERS)
        )


class TestNextTurnTichu:
    """Tests for Tichu call in next_turn."""

    def test_tichu_call_with_full_hand(self, game: Tichu):
        """Test that Tichu can be called with a full hand of 14 cards."""

        player = game.current_player
        initial_hand_size = len(
            game.state.get_player_state(game.state.current_player_idx).hand
        )

        with patch.object(player, "get_card_play", return_value="tichu"):
            play = player.get_card_play(game.state)
            game.next_turn(game.state.current_player_idx, play)

        assert (
            game.state.get_player_state(game.state.current_player_idx).tichu_called
            is True
        )
        assert (
            len(game.state.get_player_state(game.state.current_player_idx).hand)
            == initial_hand_size
        )

    def test_tichu_call_without_full_hand_raises_error(self, game: Tichu):
        """Test that Tichu cannot be called without a full hand."""

        player_idx = game.state.current_player_idx
        game.state.get_player_state(player_idx).hand.pop()

        with (
            patch.object(game.current_player, "get_card_play", return_value="tichu"),
            pytest.raises(InvalidPlayError),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(player_idx, play)


class TestNextTurnPlayCard:
    """Tests for playing cards in next_turn."""

    def test_play_single_card_not_in_hand(self, game: Tichu):
        """Test playing a single card."""

        game.state.current_player_idx = 0
        player = game.current_player
        initial_hand_size = len(game.state.get_player_state(0).hand)

        with (
            patch.object(
                player,
                "get_card_play",
                return_value=({game.state.get_player_state(1).hand[0]}, None),
            ),
            pytest.raises(InvalidPlayError),
        ):
            play = player.get_card_play(game.state)
            game.next_turn(0, play)

        assert len(game.state.get_player_state(0).hand) == initial_hand_size
        assert game.state.current_combination is None

    def test_play_single_card(self, game: Tichu):
        """Test playing a single card."""

        game.state.current_player_idx = 0
        player = game.current_player
        initial_hand_size = len(game.state.get_player_state(0).hand)

        with patch.object(
            player,
            "get_card_play",
            return_value=({game.state.get_player_state(0).hand[0]}, None),
        ):
            play = player.get_card_play(game.state)
            game.next_turn(0, play)

        assert len(game.state.get_player_state(0).hand) == initial_hand_size - 1
        assert game.state.current_combination is not None
        assert game.state.current_combination.combination_type == CombinationType.SINGLE
        assert game.state.winning_player_idx == 0

    def test_play_pair(self, game: Tichu):
        """Test playing a pair of cards."""

        player_idx = game.state.current_player_idx
        player_state = game.state.get_player_state(player_idx)
        value_counts = {}
        for card in player_state.hand:
            if card.value not in value_counts:
                value_counts[card.value] = []
            value_counts[card.value].append(card)

        pair = next((cards for cards in value_counts.values() if len(cards) >= 2), None)

        assert pair
        play_set = {pair[0], pair[1]}
        initial_hand_size = len(player_state.hand)

        with patch.object(
            game.current_player, "get_card_play", return_value=(play_set, None)
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(player_idx, play)

        assert (
            len(game.state.get_player_state(player_idx).hand) == initial_hand_size - 2
        )
        assert (
            game.state.current_combination
            and game.state.current_combination.combination_type == CombinationType.PAIR
        )

    def test_play_higher_card_after_single(self, game: Tichu):
        """Test playing a higher single card than current combination."""

        game.state.current_player_idx = 1
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 5
        game.state.current_combination.length = 1

        player = game.current_player
        valid_cards = {
            card for card in game.state.get_player_state(1).hand if card.value == 6
        }

        initial_hand_size = len(game.state.get_player_state(1).hand)
        with patch.object(player, "get_card_play", return_value=(valid_cards, None)):
            play = player.get_card_play(game.state)
            game.next_turn(1, play)

        assert len(game.state.get_player_state(1).hand) == initial_hand_size - 1
        assert game.state.winning_player_idx == 1

    def test_play_lower_card_raises_error(self, game: Tichu):
        """Test that playing a lower card than current combination raises error."""

        game.state.current_player_idx = 1
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 13
        game.state.current_combination.length = 1

        player = game.current_player
        valid_card = {
            card for card in game.state.get_player_state(1).hand if card.value == 12
        }

        assert valid_card
        with (
            patch.object(player, "get_card_play", return_value=(valid_card, None)),
            pytest.raises(InvalidPlayError),
        ):
            play = player.get_card_play(game.state)
            game.next_turn(1, play)

    def test_play_non_matching_combination_type_raises_error(self, game: Tichu):
        """Test that playing non-matching combination type raises error."""

        game.state.current_player_idx = 1
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.PAIR
        game.state.current_combination.value = 5
        game.state.current_combination.length = 2

        with (
            patch.object(
                game.current_player,
                "get_card_play",
                return_value=({game.state.get_player_state(1).hand[0]}, None),
            ),
            pytest.raises(InvalidPlayError),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(1, play)

    def test_bomb_can_always_be_played_over_non_bombs(self, game: Tichu):
        """Test that a bomb can be played over any non-bomb combination."""

        game.state.current_player_idx = 1
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.PAIR
        game.state.current_combination.value = 14
        game.state.current_combination.length = 2

        game.state.get_player_state(1).hand = [
            Card(Color.JADE, 9),
            Card(Color.PAGODE, 9),
            Card(Color.SWORDS, 9),
            Card(Color.STAR, 9),
        ]
        with patch.object(
            game.current_player,
            "get_card_play",
            return_value=(set(game.state.get_player_state(1).hand), None),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(1, play)
            game.state.winning_player_idx = 1
            game.state.current_combination.type = CombinationType.BOMB

    def test_bomb_can_be_played_out_of_turn(self, game: Tichu):
        """Test that a bomb can be played even if it's not the player's turn."""

        game.state.current_player_idx = 0
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 5
        game.state.current_combination.length = 1

        bomb_cards = [
            Card(Color.JADE, 9),
            Card(Color.PAGODE, 9),
            Card(Color.SWORDS, 9),
            Card(Color.STAR, 9),
        ]
        game.state.get_player_state(1).hand = bomb_cards

        with patch.object(
            game.players[1], "get_card_play", return_value=(set(bomb_cards), None)
        ):
            play = game.players[1].get_card_play(game.state)
            game.next_turn(1, play)

        assert game.state.current_player_idx == 2
        assert game.state.winning_player_idx == 1
        assert game.state.current_combination.combination_type == CombinationType.BOMB

    def test_non_bomb_cannot_be_played_out_of_turn(self, game: Tichu):
        """Test that a non-bomb combination cannot be played if it's not the player's turn."""

        game.state.current_player_idx = 0
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 5
        game.state.current_combination.length = 1

        single_card = {Card(Color.JADE, 6)}
        game.state.get_player_state(1).hand = list(single_card)

        with (
            patch.object(
                game.players[1], "get_card_play", return_value=(single_card, None)
            ),
            pytest.raises(InvalidPlayError),
        ):
            play = game.players[1].get_card_play(game.state)
            game.next_turn(1, play)

        assert game.state.current_player_idx == 0


class TestNextTurnSpecialCards:
    """Tests for special card handling in next_turn."""

    def test_play_dog_passes_turn_to_teammate(self, game: Tichu):
        """Test that playing dog passes turn to teammate."""

        game.state.current_player_idx = 0
        game.state.get_player_state(0).hand = [DOG]
        with patch.object(
            game.current_player,
            "get_card_play",
            return_value=(set(game.state.get_player_state(0).hand), None),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(0, play)

        assert game.state.current_player_idx == 2

    def test_play_phoenix_updates_combination_value(self, game: Tichu):
        """Test that playing Phoenix updates combination value."""

        card_value = 5
        game.state.current_player_idx = 0
        game.state.card_stack = [Card(Color.JADE, card_value)]
        game.state.current_combination = Combination(CombinationType.SINGLE, card_value)
        game.state.get_player_state(0).hand = [PHOENIX]

        with patch.object(
            game.current_player,
            "get_card_play",
            return_value=(set(game.state.get_player_state(0).hand), None),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(0, play)

        assert game.state.current_combination is not None
        assert game.state.current_combination.combination_type == CombinationType.SINGLE
        assert game.state.current_combination.value == card_value + 0.5

    def test_play_mahjong_wish_is_set(self, game: Tichu):
        """Test that playing Mah Jong prompts for wish value."""

        game.state.current_player_idx = 0
        game.state.get_player_state(0).hand = [MAH_JONG]

        with (
            patch.object(
                game.current_player,
                "get_card_play",
                return_value=(set(game.state.get_player_state(0).hand), 7),
            ),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(0, play)

        assert game.state.current_wish == 7

    def test_play_mahjong_wish_invalid_choice(self, game: Tichu):
        """Test that playing Mah Jong with invalid wish raises error."""

        game.state.current_player_idx = 0
        game.state.get_player_state(0).hand = [MAH_JONG]

        with (
            patch.object(
                game.current_player,
                "get_card_play",
                return_value=(set(game.state.get_player_state(0).hand), 15),
            ),
            pytest.raises(InvalidPlayError),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(0, play)

    def test_play_mahjong_wish_invalid(self, game: Tichu):
        """Test that playing Mah Jong without wish raises error."""

        game.state.current_player_idx = 0
        game.state.get_player_state(0).hand = [MAH_JONG]

        with (
            patch.object(
                game.current_player,
                "get_card_play",
                return_value=(set(game.state.get_player_state(0).hand), None),
            ),
            pytest.raises(InvalidPlayError),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(0, play)

    def test_play_dragon_triggers_stack_selection(self, game: Tichu):
        """Test that playing dragon and winning triggers stack recipient selection."""

        game.state.current_player_idx = 0
        game.state.get_player_state(0).hand = [Card(Color.JADE, 2), DRAGON]

        with patch(
            "tichu.random_player.RandomPlayer.get_card_play",
            side_effect=[
                ({game.state.get_player_state(0).hand[1]}, 1),
                "pass",
                "pass",
                "pass",
            ],
        ):
            for _ in range(4):
                play = game.current_player.get_card_play(game.state)
                game.next_turn(game.state.current_player_idx, play)

        assert game.state.winning_player_idx == 0
        assert game.state.current_player_idx == 0
        assert game.state.get_player_state(1).card_stack == [DRAGON]

    def test_play_dragon_stack_selection_invalid_player(self, game: Tichu):
        """Test that playing dragon with invalid recipient raises error."""

        game.state.current_player_idx = 0
        game.state.get_player_state(0).hand = [DRAGON]

        with (
            patch(
                "tichu.random_player.RandomPlayer.get_card_play",
                side_effect=[
                    ({game.state.get_player_state(0).hand[0]}, 2),
                    "pass",
                    "pass",
                    "pass",
                ],
            ),
            pytest.raises(InvalidPlayError),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(0, play)

    def test_play_dragon_stack_selection_invalid(self, game: Tichu):
        """Test that playing dragon without recipient raises error."""

        game.state.current_player_idx = 0
        game.state.get_player_state(0).hand = [DRAGON]

        with (
            patch(
                "tichu.random_player.RandomPlayer.get_card_play",
                side_effect=[
                    ({game.state.get_player_state(0).hand[0]}, None),
                    "pass",
                    "pass",
                    "pass",
                ],
            ),
            pytest.raises(InvalidPlayError),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(0, play)


class TestNextTurnWish:
    def test_player_can_play_card_if_wish_is_not_possible(self, game: Tichu):
        game.state.current_wish = 2
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 13
        game.state.current_combination.length = 1

        game.state.current_player_idx = 1
        game.state.get_player_state(1).hand = [Card(Color.PAGODE, 14)]

        with (
            patch.object(
                game.current_player,
                "get_card_play",
                return_value=(set(game.state.get_player_state(1).hand), None),
            ),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(1, play)

    def test_player_can_not_play_card_if_wish_is_possible(self, game: Tichu):
        game.state.current_wish = 2
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 13
        game.state.current_combination.length = 1

        game.state.current_player_idx = 1
        game.state.get_player_state(1).hand = [
            Card(Color.PAGODE, 14),
            Card(Color.PAGODE, 2),
            Card(Color.SWORDS, 2),
            Card(Color.STAR, 2),
            Card(Color.JADE, 2),
        ]

        with (
            patch.object(
                game.current_player,
                "get_card_play",
                return_value=(set(game.state.get_player_state(1).hand), None),
            ),
            pytest.raises(InvalidPlayError),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(1, play)


class TestNextTurnEdgeCases:
    """Tests for edge cases in next_turn."""

    def test_player_with_no_cards_is_skipped(self, game: Tichu):
        """Test that a player with no cards is skipped."""

        game.state.current_player_idx = 0
        game.state.player_rankings = [1]
        initial_player_id = game.state.current_player_idx

        play = "pass"
        game.next_turn(initial_player_id, play)

        assert game.state.current_player_idx == initial_player_id + 2

    def test_invalid_card_raises_error(self, game: Tichu):
        """Test that invalid card index raises error."""

        game.state.current_player_idx = 0
        hand_size = len(game.state.get_player_state(0).hand)

        with (
            patch.object(
                game.current_player,
                "get_card_play",
                return_value=({Card(Color.JADE, 9)}, None),
            ),
            pytest.raises(InvalidPlayError),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(0, play)

    def test_turn_advances_to_next_player(self, game: Tichu):
        """Test that turn advances to next player after valid play."""

        initial_player_id = game.state.current_player_idx

        with patch.object(
            game.current_player,
            "get_card_play",
            return_value=(
                {game.state.get_player_state(initial_player_id).hand[1]},
                None,
            ),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(initial_player_id, play)

        assert game.state.current_player_idx == (initial_player_id + 1) % NUM_PLAYERS

    def test_reproducible_game_with_seed(self):
        """Test that games with same seed produce same hand distributions."""
        players: list[Player] = [
            RandomPlayer(f"Player {i}") for i in range(NUM_PLAYERS)
        ]
        game1 = Tichu(seed=123)
        game1.new_game(players)
        with patch(
            "tichu.random_player.RandomPlayer.get_grand_tichu_play", return_value="pass"
        ):
            with patch(
                "tichu.random_player.RandomPlayer.get_push_play", return_value={0, 1, 2}
            ):
                game1.start_new_round()
        hands1 = [
            [(card.color, card.value) for card in game1.state.get_player_state(i).hand]
            for i in range(NUM_PLAYERS)
        ]

        players = [RandomPlayer(f"Player {i}") for i in range(NUM_PLAYERS)]
        game2 = Tichu(seed=123)
        game2.new_game(players)
        with patch(
            "tichu.random_player.RandomPlayer.get_grand_tichu_play", return_value="pass"
        ):
            with patch(
                "tichu.random_player.RandomPlayer.get_push_play", return_value={0, 1, 2}
            ):
                game2.start_new_round()
        hands2 = [
            [(card.color, card.value) for card in game2.state.get_player_state(i).hand]
            for i in range(NUM_PLAYERS)
        ]

        assert hands1 == hands2


class TestNextTurnGameFlow:
    """Tests for overall game flow in next_turn."""

    def test_card_stack_accumulates(self, game: Tichu):
        """Test that played cards accumulate in card stack."""

        game.state.current_player_idx = 0
        initial_stack_size = len(game.state.card_stack)

        with patch.object(
            game.current_player,
            "get_card_play",
            return_value=({game.state.get_player_state(0).hand[1]}, None),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(0, play)

        assert len(game.state.card_stack) > initial_stack_size

    def test_winning_player_is_updated(self, game: Tichu):
        """Test that winning player is updated when cards are played."""

        game.state.current_player_idx = 1
        game.state.winning_player_idx = 1

        with patch.object(
            game.current_player,
            "get_card_play",
            return_value=({game.state.get_player_state(1).hand[1]}, None),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(1, play)

        assert game.state.winning_player_idx == 1

    def test_current_combination_is_set(self, game: Tichu):
        """Test that current combination is set after valid play."""

        assert game.state.current_combination is None

        with patch.object(
            game.current_player,
            "get_card_play",
            return_value=(
                {game.state.get_player_state(game.state.current_player_idx).hand[1]},
                None,
            ),
        ):
            play = game.current_player.get_card_play(game.state)
            game.next_turn(game.state.current_player_idx, play)

        assert game.state.current_combination is not None
        assert game.state.current_combination.combination_type == CombinationType.SINGLE


class TestEndRoundScoring:
    """Tests for end_round_scoring function."""

    def test_same_team_finish_first_and_second_bonus(self, game: Tichu):
        """Test that both players from same team finishing first and second grants 200 points."""

        game.state.player_rankings = [0, 2]
        initial_team_score = game.state.scores[0]

        game.end_round_scoring()

        assert game.state.scores[0] == initial_team_score + 200
        assert game.state.scores[1] == 0

    def test_tichu_bonus_first_place(self, game: Tichu):
        """Test that Tichu called and finishing first grants 100 point bonus."""

        game.state.get_player_state(0).tichu_called = True
        game.state.player_rankings = [0, 1, 2]
        game.state.get_player_state(3).hand = [
            Card(Color.JADE, 3),
            Card(Color.SWORDS, 4),
        ]
        initial_team_score = game.state.scores[0]

        game.end_round_scoring()

        assert game.state.scores[0] == initial_team_score + TICHU_SCORE

    def test_grand_tichu_bonus_first_place(self, game: Tichu):
        """Test that Tichu called and finishing first grants 200 point bonus."""

        game.state.get_player_state(0).grand_tichu_called = True
        game.state.player_rankings = [0, 1, 2]
        game.state.get_player_state(3).hand = [
            Card(Color.JADE, 3),
            Card(Color.SWORDS, 4),
        ]
        initial_team_score = game.state.scores[0]

        game.end_round_scoring()

        assert game.state.scores[0] == initial_team_score + GRAND_TICHU_SCORE

    def test_tichu_penalty_not_first_place(self, game: Tichu):
        """Test that Tichu called but not finishing first incurs 100 point penalty."""

        game.state.get_player_state(1).tichu_called = True
        game.state.player_rankings = [0, 1, 2]
        initial_team_score = game.state.scores[1]

        game.end_round_scoring()

        assert game.state.scores[1] <= initial_team_score - TICHU_SCORE

    def test_card_scoring_from_opposing_player(self, game: Tichu):
        """Test that opposing player's hand cards are scored."""

        game.state.player_rankings = [0, 1, 2]
        hand_score = Card.count_card_scores(game.state.get_player_state(3).hand)
        initial_team_score = game.state.scores[0]

        game.end_round_scoring()

        assert game.state.scores[0] == initial_team_score + hand_score

    def test_card_scoring_from_losing_player(self, game: Tichu):
        """Test that losing player's hand cards are scored."""

        game.state.player_rankings = [0, 1, 2]
        game.state.get_player_state(3).hand = [
            Card(Color.JADE, 3),
            Card(Color.SWORDS, 4),
        ]
        game.state.get_player_state(3).card_stack = [
            Card(Color.JADE, 5),
            Card(Color.SWORDS, 10),
            DRAGON,
        ]
        stack_score = Card.count_card_scores(game.state.get_player_state(3).card_stack)
        initial_team_score = game.state.scores[0]

        game.end_round_scoring()

        assert game.state.scores[0] == initial_team_score + stack_score

    def test_card_stack_scoring(self, game: Tichu):
        """Test that card stacks are scored properly."""

        game.state.player_rankings = [0, 1, 2]

        test_cards = [Card(Color.PAGODE, 5), Card(Color.JADE, 10)]
        game.state.get_player_state(0).card_stack.extend(test_cards)
        game.state.get_player_state(3).hand = [
            Card(Color.JADE, 3),
            Card(Color.SWORDS, 4),
        ]

        initial_team_score = game.state.scores[0]
        card_score = Card.count_card_scores(test_cards)
        game.end_round_scoring()

        assert game.state.scores[0] == initial_team_score + card_score

    def test_multiple_player_tichu_calls(self, game: Tichu):
        """Test scoring when multiple players called Tichu."""

        game.state.get_player_state(0).tichu_called = True
        game.state.get_player_state(1).tichu_called = True
        game.state.player_rankings = [0, 2, 3]
        game.state.get_player_state(1).hand = [
            Card(Color.JADE, 3),
            Card(Color.SWORDS, 4),
        ]

        initial_team_0_score = game.state.scores[0]
        initial_team_1_score = game.state.scores[1]

        game.end_round_scoring()

        assert game.state.scores[0] == initial_team_0_score + 100
        assert game.state.scores[1] == initial_team_1_score - 100

    def test_score_accumulation_across_rounds(self, game: Tichu):
        """Test that scores accumulate across multiple calls to end_round_scoring."""
        game.state.player_rankings = [0, 2]
        game.end_round_scoring()
        first_round_team_0_score = game.state.scores[0]

        with patch(
            "tichu.random_player.RandomPlayer.get_grand_tichu_play", return_value="pass"
        ):
            with patch(
                "tichu.random_player.RandomPlayer.get_push_play", return_value={0, 1, 2}
            ):
                game.start_new_round()
        game.state.player_rankings = [1, 3]
        game.end_round_scoring()

        assert (
            game.state.scores[0] == first_round_team_0_score or game.state.scores[1] > 0
        )

    def test_all_players_ranked(self, game: Tichu):
        """Test scoring when all players are ranked (3 finished, 1 remaining)."""

        game.state.player_rankings = [0, 1, 2]

        game.end_round_scoring()

        assert len(game.state.scores) == 2
        assert game.state.scores[0] >= 0
        assert game.state.scores[1] >= 0

    def test_dragon_card_in_stack_scores(self, game: Tichu):
        """Test that dragon card in card stack is properly scored."""

        game.state.player_rankings = [0, 1, 2]

        game.state.get_player_state(0).card_stack.append(DRAGON)

        initial_team_score = game.state.scores[0]
        game.end_round_scoring()

        assert game.state.scores[0] > initial_team_score


class TestPushCards:
    """Tests for push_cards function."""

    def test_pushed_cards_in_someone_elses_hand(self, game: Tichu):
        """Test that pushed cards are in someone else's hand."""

        original_hand_size = len(game.state.get_player_state(0).hand)

        with patch("tichu.player.Player.get_push_play", return_value={0, 1, 2}):
            game.push_cards()

        for player_idx in range(NUM_PLAYERS):
            assert (
                len(game.state.get_player_state(player_idx).hand) == original_hand_size
            )

    def test_pushed_cards_are_valid_cards(self, game: Tichu):
        """Test that pushed cards are actual cards from the hand."""

        original_hands = [
            game.state.get_player_state(i).hand.copy() for i in range(NUM_PLAYERS)
        ]

        with patch("tichu.player.Player.get_push_play", return_value={0, 1, 2}):
            game.push_cards()

        all_cards_before = []
        for hand in original_hands:
            all_cards_before.extend(hand)

        all_cards_after = []
        for player_idx in range(NUM_PLAYERS):
            all_cards_after.extend(game.state.get_player_state(player_idx).hand)

        assert len(all_cards_before) == len(all_cards_after)

    def test_push_rotation_player_0_to_3(self, game: Tichu):
        """Test push from player 0 goes to player 3 (left), player 2 (partner), player 1 (right)."""

        card_0 = game.state.get_player_state(0).hand[0]
        card_1 = game.state.get_player_state(0).hand[1]
        card_2 = game.state.get_player_state(0).hand[2]

        with patch("tichu.random_player.RandomPlayer.get_push_play") as mock_get_push:
            mock_get_push.side_effect = [
                {0, 1, 2},
                {10, 11, 12},
                {10, 11, 12},
                {10, 11, 12},
            ]
            game.push_cards()

        player_1_received = card_2 in game.state.get_player_state(1).hand
        player_2_received = card_1 in game.state.get_player_state(2).hand
        player_3_received = card_0 in game.state.get_player_state(3).hand

        assert mock_get_push.call_count == 4
        assert player_1_received
        assert player_2_received
        assert player_3_received

    def test_sequential_push_from_all_players(self, game: Tichu):
        """Test that get_push is called sequentially for each player."""

        with patch("tichu.random_player.RandomPlayer.get_push_play") as mock_get_push:
            mock_get_push.side_effect = [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}, {0, 1, 2}]
            game.push_cards()
            call_sequence = list(mock_get_push.call_args_list)

        assert len(call_sequence) == 4
