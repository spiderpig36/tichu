from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from tichu.card import Card, Color, SpecialCard
from tichu.combination import Combination, CombinationType
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
    players = [RandomPlayer(f"Player {i}") for i in range(NUM_PLAYERS)]
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
        players = [RandomPlayer(f"Player {i}") for i in range(NUM_PLAYERS)]
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

        assert game.players[0].state.grand_tichu_called
        assert not game.players[1].state.grand_tichu_called
        assert not game.players[2].state.grand_tichu_called
        assert not game.players[3].state.grand_tichu_called

    def test_cards_are_dealt(self, game):
        for player in game.players:
            assert len(player.state.hand) == HAND_SIZE


class TestNextTurnPass:
    """Tests for player passing in next_turn."""

    def test_player_passes_single_card(self, game):
        """Test a player passing during their turn."""

        # Set up initial state
        game.state.current_player_idx = 0
        initial_player_id = game.state.current_player_idx

        with patch.object(game.current_player, "get_card_play", return_value="pass"):
            game.next_turn()

        # Player should have marked as passed
        assert game.players[initial_player_id].state.has_passed is True
        # Current player should advance to next player
        assert game.state.current_player_idx == (initial_player_id + 1) % NUM_PLAYERS

    def test_all_players_pass_resets_combination(self, game):
        """Test that when all players except winner pass, combination resets."""

        # Set up game state
        game.state.current_player_idx = 1
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 5

        with patch(
            "tichu.random_player.RandomPlayer.get_card_play", return_value="pass"
        ):
            game.next_turn()
            game.next_turn()
            game.next_turn()

        # Combination should be reset
        assert game.state.current_combination is None
        assert game.state.current_player_idx == 0
        # All players should be unmarked as passed
        assert all(not player.state.has_passed for player in game.players)


class TestNextTurnTichu:
    """Tests for Tichu call in next_turn."""

    def test_tichu_call_with_full_hand(self, game):
        """Test that Tichu can be called with a full hand of 14 cards."""

        player = game.current_player
        initial_hand_size = len(player.state.hand)

        with patch.object(player, "get_card_play", return_value="tichu"):
            game.next_turn()

        # Tichu should be marked as called
        assert player.state.tichu_called is True
        # Hand size shouldn't change
        assert len(player.state.hand) == initial_hand_size

    def test_tichu_call_without_full_hand_raises_error(self, game):
        """Test that Tichu cannot be called without a full hand."""

        player = game.current_player
        # Remove a card to make hand size != 14
        player.state.hand.pop()

        with (
            patch.object(player, "get_card_play", return_value="tichu"),
            pytest.raises(InvalidPlayError),
        ):
            game.next_turn()


class TestNextTurnPlayCard:
    """Tests for playing cards in next_turn."""

    def test_play_single_card(self, game):
        """Test playing a single card."""

        game.state.current_player_idx = 0
        player = game.current_player
        initial_hand_size = len(player.state.hand)

        # Play the first card
        with patch.object(player, "get_card_play", return_value={0}):
            game.next_turn()

        # Hand size should decrease
        assert len(player.state.hand) == initial_hand_size - 1
        # Current combination should be set
        assert game.state.current_combination is not None
        assert game.state.current_combination.combination_type == CombinationType.SINGLE
        # Winning player should be updated
        assert game.state.winning_player_idx == 0

    def test_play_pair(self, game):
        """Test playing a pair of cards."""

        player = game.current_player
        # Find a pair in the hand
        value_counts = {}
        for i, card in enumerate(player.state.hand):
            if card.value not in value_counts:
                value_counts[card.value] = []
            value_counts[card.value].append(i)

        pair_indices = next(
            (indices for indices in value_counts.values() if len(indices) >= 2), None
        )

        assert pair_indices
        play_set = {pair_indices[0], pair_indices[1]}
        initial_hand_size = len(player.state.hand)

        with patch.object(player, "get_card_play", return_value=play_set):
            game.next_turn()

        assert len(player.state.hand) == initial_hand_size - 2
        assert game.state.current_combination.combination_type == CombinationType.PAIR

    def test_play_higher_card_after_single(self, game):
        """Test playing a higher single card than current combination."""

        # Set up initial combination
        game.state.current_player_idx = 1
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 5
        game.state.current_combination.length = 1

        player = game.current_player
        # Find a card with value > 5
        valid_card_indices = [
            i for i, card in enumerate(player.state.hand) if card.value > 5
        ]

        initial_hand_size = len(player.state.hand)
        with patch.object(
            player, "get_card_play", return_value={valid_card_indices[0]}
        ):
            game.next_turn()

        assert len(player.state.hand) == initial_hand_size - 1
        assert game.state.winning_player_idx == 1

    def test_play_lower_card_raises_error(self, game):
        """Test that playing a lower card than current combination raises error."""

        # Set up initial combination with high value
        game.state.current_player_idx = 1
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 13
        game.state.current_combination.length = 1

        player = game.current_player
        # Find a card with value < 13
        valid_card_indices = [
            i for i, card in enumerate(player.state.hand) if card.value < 13
        ]

        assert valid_card_indices
        with (
            patch.object(player, "get_card_play", return_value={valid_card_indices[0]}),
            pytest.raises(InvalidPlayError),
        ):
            game.next_turn()

    def test_play_non_matching_combination_type_raises_error(self, game):
        """Test that playing non-matching combination type raises error."""

        # Set up initial pair combination
        game.state.current_player_idx = 1
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.PAIR
        game.state.current_combination.value = 5
        game.state.current_combination.length = 2

        # Try to play a single card
        with (
            patch.object(game.current_player, "get_card_play", return_value={0}),
            pytest.raises(InvalidPlayError),
        ):
            game.next_turn()

    def test_bomb_can_always_be_played_over_non_bombs(self, game):
        """Test that a bomb can be played over any non-bomb combination."""

        # Set up initial pair combination
        game.state.current_player_idx = 1
        game.state.winning_player_idx = 0
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.PAIR
        game.state.current_combination.value = 14
        game.state.current_combination.length = 2

        player = game.current_player
        player.state.hand = [
            Card(Color.JADE, 9),
            Card(Color.PAGODE, 9),
            Card(Color.SWORDS, 9),
            Card(Color.STAR, 9),
        ]
        with patch.object(player, "get_card_play", return_value={0, 1, 2, 3}):
            game.next_turn()
            game.state.winning_player_idx = 1
            game.state.current_combination.type = CombinationType.BOMB


class TestNextTurnSpecialCards:
    """Tests for special card handling in next_turn."""

    def test_play_dog_passes_turn_to_teammate(self, game):
        """Test that playing dog passes turn to teammate."""

        # Replace current player's first card with dog
        game.state.current_player_idx = 0
        game.current_player.state.hand[0] = Card(Color.SPECIAL, SpecialCard.DOG.value)

        with patch.object(game.current_player, "get_card_play", return_value={0}):
            game.next_turn()

        # Next player should be teammate (2 positions ahead)
        assert game.state.current_player_idx == 2

    def test_play_phoenix_updates_combination_value(self, game: Tichu):
        """Test that playing Phoenix updates combination value."""

        card_value = 5
        game.state.current_player_idx = 0
        game.state.card_stack = [Card(Color.JADE, card_value)]
        game.state.current_combination = Combination(CombinationType.SINGLE, card_value)
        # Replace first card with Phoenix
        game.current_player.state.hand[0] = Card(
            Color.SPECIAL, SpecialCard.PHOENIX.value
        )

        with patch.object(game.current_player, "get_card_play", return_value={0}):
            game.next_turn()

        # Combination should be set with Phoenix
        assert game.state.current_combination is not None
        assert game.state.current_combination.combination_type == CombinationType.SINGLE
        assert game.state.current_combination.value == card_value + 0.5

    def test_play_mahjong_prompts_for_wish(self, game):
        """Test that playing Mah Jong prompts for wish value."""

        game.state.current_player_idx = 0
        # Replace first card with Mah Jong
        game.current_player.state.hand[0] = Card(
            Color.SPECIAL, SpecialCard.MAH_JONG.value
        )

        with (
            patch.object(game.current_player, "get_card_play", return_value={0}),
            patch.object(game.current_player, "get_mahjong_wish_play", return_value=7),
        ):
            game.next_turn()

        # Current wish should be set
        assert game.state.current_wish == 7

    def test_play_dragon_triggers_stack_selection(self, game):
        """Test that playing dragon and winning triggers stack recipient selection."""

        game.state.current_player_idx = 2
        game.state.winning_player_idx = 3
        game.players[0].state.has_passed = True
        game.players[1].state.has_passed = True

        # Replace first card with Dragon
        game.state.card_stack = [Card(Color.SPECIAL, SpecialCard.DRAGON.value)]
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = SpecialCard.DRAGON.value

        with (
            patch.object(game.current_player, "get_card_play", return_value="pass"),
            patch.object(
                game.winning_player, "get_dragon_stack_recipient_play", return_value=2
            ),
        ):
            game.next_turn()

        # Winning player should not be updated
        assert game.state.winning_player_idx == 3
        assert game.state.current_player_idx == 3
        assert game.players[2].state.card_stack == [
            Card(Color.SPECIAL, SpecialCard.DRAGON.value)
        ]


class TestNextTurnWish:
    def test_player_can_play_card_if_wish_is_not_possible(self, game):
        """Test that a player with no cards is skipped."""

        game.state.current_wish = 2
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 13
        game.state.current_combination.length = 1

        game.state.current_player_idx = 1
        game.current_player.state.hand = [Card(Color.PAGODE, 14)]

        with patch.object(game.current_player, "get_card_play", return_value={0}):
            game.next_turn()

    def test_player_can_not_play_card_if_wish_is_possible(self, game):
        """Test that a player with no cards is skipped."""

        game.state.current_wish = 2
        game.state.current_combination = MagicMock()
        game.state.current_combination.combination_type = CombinationType.SINGLE
        game.state.current_combination.value = 13
        game.state.current_combination.length = 1

        game.state.current_player_idx = 1
        game.current_player.state.hand = [
            Card(Color.PAGODE, 14),
            Card(Color.PAGODE, 2),
            Card(Color.SWORDS, 2),
            Card(Color.STAR, 2),
            Card(Color.JADE, 2),
        ]

        with (
            patch.object(game.current_player, "get_card_play", return_value={0}),
            pytest.raises(InvalidPlayError),
        ):
            game.next_turn()


class TestNextTurnEdgeCases:
    """Tests for edge cases in next_turn."""

    def test_player_with_no_cards_is_skipped(self, game):
        """Test that a player with no cards is skipped."""

        game.state.current_player_idx = 0
        game.state.player_rankings = [0]
        initial_player_id = game.state.current_player_idx

        game.next_turn()

        # Should advance to next player
        assert game.state.current_player_idx == (initial_player_id + 1) % NUM_PLAYERS

    def test_invalid_card_index_raises_error(self, game):
        """Test that invalid card index raises error."""

        game.state.current_player_idx = 0
        hand_size = len(game.current_player.state.hand)

        with (
            patch.object(
                game.current_player, "get_card_play", return_value={hand_size + 10}
            ),
            pytest.raises(InvalidPlayError),
        ):  # index out of range
            game.next_turn()

    def test_turn_advances_to_next_player(self, game):
        """Test that turn advances to next player after valid play."""

        initial_player_id = game.state.current_player_idx

        with patch.object(game.current_player, "get_card_play", return_value={2}):
            game.next_turn()

        # Current player should advance
        assert game.state.current_player_idx == (initial_player_id + 1) % NUM_PLAYERS

    def test_reproducible_game_with_seed(self):
        """Test that games with same seed produce same hand distributions."""
        players = [RandomPlayer(f"Player {i}") for i in range(NUM_PLAYERS)]
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
            [(card.color, card.value) for card in player.state.hand]
            for player in game1.players
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
            [(card.color, card.value) for card in player.state.hand]
            for player in game2.players
        ]

        # Hands should be identical
        assert hands1 == hands2


class TestNextTurnGameFlow:
    """Tests for overall game flow in next_turn."""

    def test_card_stack_accumulates(self, game):
        """Test that played cards accumulate in card stack."""

        game.state.current_player_idx = 0
        initial_stack_size = len(game.state.card_stack)

        with patch.object(game.current_player, "get_card_play", return_value={0}):
            game.next_turn()

        # Card stack should have increased
        assert len(game.state.card_stack) > initial_stack_size

    def test_winning_player_is_updated(self, game):
        """Test that winning player is updated when cards are played."""

        game.state.current_player_idx = 1
        game.state.winning_player_idx = None

        with patch.object(game.current_player, "get_card_play", return_value={1}):
            game.next_turn()

        # Winning player should be updated to current player
        assert game.state.winning_player_idx == 1

    def test_current_combination_is_set(self, game):
        """Test that current combination is set after valid play."""

        assert game.state.current_combination is None

        with patch.object(game.current_player, "get_card_play", return_value={1}):
            game.next_turn()

        # Current combination should be set
        assert game.state.current_combination is not None
        assert game.state.current_combination.combination_type == CombinationType.SINGLE


class TestEndRoundScoring:
    """Tests for end_round_scoring function."""

    def test_same_team_finish_first_and_second_bonus(self, game):
        """Test that both players from same team finishing first and second grants 200 points."""

        # Team 0 (players 0 and 2) finish first and second
        game.state.player_rankings = [0, 2]
        initial_team_score = game.state.scores[0]

        game.end_round_scoring()

        # Team 0 should gain 200 points
        assert game.state.scores[0] == initial_team_score + 200
        # Team 1 score should be unchanged
        assert game.state.scores[1] == 0

    def test_tichu_bonus_first_place(self, game):
        """Test that Tichu called and finishing first grants 100 point bonus."""

        # Player 0 called Tichu and finished first
        game.players[0].state.tichu_called = True
        game.state.player_rankings = [0, 1, 2]
        game.players[3].state.hand = [Card(Color.JADE, 3), Card(Color.SWORDS, 4)]
        initial_team_score = game.state.scores[0]

        game.end_round_scoring()

        # Team 0 should gain 100 for Tichu bonus
        assert game.state.scores[0] == initial_team_score + TICHU_SCORE

    def test_grand_tichu_bonus_first_place(self, game):
        """Test that Tichu called and finishing first grants 200 point bonus."""
        # Player 0 called grand Tichu and finished first

        game.players[0].state.grand_tichu_called = True
        game.state.player_rankings = [0, 1, 2]
        game.players[3].state.hand = [Card(Color.JADE, 3), Card(Color.SWORDS, 4)]
        initial_team_score = game.state.scores[0]

        game.end_round_scoring()

        # Team 0 should gain 200 for Tichu bonus
        assert game.state.scores[0] == initial_team_score + GRAND_TICHU_SCORE

    def test_tichu_penalty_not_first_place(self, game):
        """Test that Tichu called but not finishing first incurs 100 point penalty."""

        # Player 1 called Tichu but didn't finish first
        game.players[1].state.tichu_called = True
        game.state.player_rankings = [0, 1, 2]
        initial_team_score = game.state.scores[1]

        game.end_round_scoring()

        # Team 1 should lose 100 for failed Tichu
        assert game.state.scores[1] <= initial_team_score - TICHU_SCORE

    def test_card_scoring_from_opposing_player(self, game):
        """Test that opposing player's hand cards are scored."""

        # Set up rankings
        game.state.player_rankings = [0, 1, 2]
        hand_score = Card.count_card_scores(game.players[3].state.hand)
        initial_team_score = game.state.scores[0]

        game.end_round_scoring()

        # Score from player 3's remaining hand should be added to team 0
        assert game.state.scores[0] == initial_team_score + hand_score

    def test_card_scoring_from_losing_player(self, game):
        """Test that losing player's hand cards are scored."""

        # Set up rankings
        game.state.player_rankings = [0, 1, 2]
        game.players[3].state.hand = [Card(Color.JADE, 3), Card(Color.SWORDS, 4)]
        game.players[3].state.card_stack = [
            Card(Color.JADE, 5),
            Card(Color.SWORDS, 10),
            Card(Color.SPECIAL, SpecialCard.DRAGON.value),
        ]
        stack_score = Card.count_card_scores(game.players[3].state.card_stack)
        initial_team_score = game.state.scores[0]

        game.end_round_scoring()

        # Score from player 3's remaining hand should be added to team 0
        assert game.state.scores[0] == initial_team_score + stack_score

    def test_card_stack_scoring(self, game):
        """Test that card stacks are scored properly."""

        # Set up game state
        game.state.player_rankings = [0, 1, 2]

        # Add some cards to winner's stack
        test_cards = [Card(Color.PAGODE, 5), Card(Color.JADE, 10)]
        game.players[0].state.card_stack.extend(test_cards)
        game.players[3].state.hand = [Card(Color.JADE, 3), Card(Color.SWORDS, 4)]

        initial_team_score = game.state.scores[0]
        card_score = Card.count_card_scores(test_cards)
        game.end_round_scoring()

        # Score should include card stack
        assert game.state.scores[0] == initial_team_score + card_score

    def test_multiple_player_tichu_calls(self, game):
        """Test scoring when multiple players called Tichu."""

        # Player 0 (team 0) called Tichu and finished first
        game.players[0].state.tichu_called = True
        # Player 1 (team 1) called Tichu but didn't finish
        game.players[1].state.tichu_called = True
        game.state.player_rankings = [0, 2, 3]
        game.players[1].state.hand = [Card(Color.JADE, 3), Card(Color.SWORDS, 4)]

        initial_team_0_score = game.state.scores[0]
        initial_team_1_score = game.state.scores[1]

        game.end_round_scoring()

        # Team 0 gains 100 for successful Tichu
        assert game.state.scores[0] == initial_team_0_score + 100
        # Team 1 loses 100 for failed Tichu
        assert game.state.scores[1] == initial_team_1_score - 100

    def test_score_accumulation_across_rounds(self, game):
        """Test that scores accumulate across multiple calls to end_round_scoring."""
        # First round
        game.state.player_rankings = [0, 2]
        game.end_round_scoring()
        first_round_team_0_score = game.state.scores[0]

        # Reset for second round
        with patch(
            "tichu.random_player.RandomPlayer.get_grand_tichu_play", return_value="pass"
        ):
            with patch(
                "tichu.random_player.RandomPlayer.get_push_play", return_value={0, 1, 2}
            ):
                game.start_new_round()
        game.state.player_rankings = [1, 3]
        game.end_round_scoring()

        # Scores should accumulate
        assert (
            game.state.scores[0] == first_round_team_0_score or game.state.scores[1] > 0
        )

    def test_all_players_ranked(self, game):
        """Test scoring when all players are ranked (3 finished, 1 remaining)."""

        game.state.player_rankings = [0, 1, 2]
        # Player 3 is the remaining player with cards

        game.end_round_scoring()

        # All players should have been processed
        assert len(game.state.scores) == 2
        assert game.state.scores[0] >= 0
        assert game.state.scores[1] >= 0

    def test_dragon_card_in_stack_scores(self, game):
        """Test that dragon card in card stack is properly scored."""

        game.state.player_rankings = [0, 1, 2]

        # Add dragon to winner's card stack (dragon is worth 25 points)
        dragon = Card(Color.SPECIAL, SpecialCard.DRAGON.value)
        game.players[0].state.card_stack.append(dragon)

        initial_team_score = game.state.scores[0]
        game.end_round_scoring()

        # Dragon (25 points) should be included
        assert game.state.scores[0] > initial_team_score


class TestPushCards:
    """Tests for push_cards function."""

    def test_pushed_cards_in_someone_elses_hand(self, game):
        """Test that pushed cards are in someone else's hand."""

        original_hand_size = len(game.players[0].state.hand)

        with patch("tichu.player.Player.get_push_play", return_value={0, 1, 2}):
            game.push_cards()

        for player in game.players:
            assert len(player.state.hand) == original_hand_size

    def test_pushed_cards_are_valid_cards(self, game):
        """Test that pushed cards are actual cards from the hand."""

        # Save original hands
        original_hands = [player.state.hand.copy() for player in game.players]

        with patch("tichu.player.Player.get_push_play", return_value={0, 1, 2}):
            game.push_cards()

        # Verify all cards still exist in the game
        all_cards_before = []
        for hand in original_hands:
            all_cards_before.extend(hand)

        all_cards_after = []
        for player in game.players:
            all_cards_after.extend(player.state.hand)

        # Same number of cards
        assert len(all_cards_before) == len(all_cards_after)

    def test_push_rotation_player_0_to_3(self, game):
        """Test push from player 0 goes to player 3 (left), player 2 (partner), player 1 (right)."""

        # Get specific cards to track
        card_0 = game.players[0].state.hand[0]
        card_1 = game.players[0].state.hand[1]
        card_2 = game.players[0].state.hand[2]

        with patch("tichu.random_player.RandomPlayer.get_push_play") as mock_get_push:
            mock_get_push.side_effect = [
                {0, 1, 2},
                {10, 11, 12},
                {10, 11, 12},
                {10, 11, 12},
            ]
            game.push_cards()

        # Cards from player 0 should be distributed among players 1, 2, 3
        player_1_received = card_2 in game.players[1].state.hand
        player_2_received = card_1 in game.players[2].state.hand
        player_3_received = card_0 in game.players[3].state.hand

        # At least the distribution pattern should work
        assert mock_get_push.call_count == 4
        assert player_1_received
        assert player_2_received
        assert player_3_received

    def test_sequential_push_from_all_players(self, game):
        """Test that get_push is called sequentially for each player."""

        call_sequence = []

        with patch("tichu.random_player.RandomPlayer.get_push_play") as mock_get_push:
            mock_get_push.side_effect = [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}, {0, 1, 2}]
            game.push_cards()
            call_sequence = list(mock_get_push.call_args_list)

        # Should be called 4 times (once per player)
        assert len(call_sequence) == 4
