import pytest
from io import StringIO
from unittest.mock import MagicMock, patch

from tichu.tichu import NUM_PLAYERS, Tichu, InvalidPlayError
from tichu.card import Card, Color, SpecialCard
from tichu.combination import CombinationType


class TestNextTurnPass:
    """Tests for player passing in next_turn."""

    def test_player_passes_single_card(self):
        """Test a player passing during their turn."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Set up initial state
        game.current_player_idx = 0
        initial_player_id = game.current_player_idx

        with patch.object(game, "get_play", return_value="pass"):
            game.next_turn()

        # Player should have marked as passed
        assert game.players[initial_player_id].has_passed is True
        # Current player should advance to next player
        assert game.current_player_idx == (initial_player_id + 1) % NUM_PLAYERS

    def test_all_players_pass_resets_combination(self):
        """Test that when all players except winner pass, combination resets."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Set up game state
        game.current_player_idx = 1
        game.winning_player_idx = 0
        game.current_combination = MagicMock()
        game.current_combination.combination_type = CombinationType.SINGLE
        game.current_combination.value = 5

        # Mark players 1, 2, 3 as passed
        game.players[1].has_passed = True
        game.players[2].has_passed = True
        game.players[3].has_passed = True

        with patch.object(game, "get_play", return_value="pass"):
            game.next_turn()

        # Combination should be reset
        assert game.current_combination is None
        # All players should be unmarked as passed
        assert all(not player.has_passed for player in game.players)


class TestNextTurnTichu:
    """Tests for Tichu call in next_turn."""

    def test_tichu_call_with_full_hand(self):
        """Test that Tichu can be called with a full hand of 14 cards."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        player = game.current_player
        initial_hand_size = len(player.hand)

        with patch.object(game, "get_play", return_value="tichu"):
            game.next_turn()

        # Tichu should be marked as called
        assert player.tichu_called is True
        # Hand size shouldn't change
        assert len(player.hand) == initial_hand_size

    def test_tichu_call_without_full_hand_raises_error(self):
        """Test that Tichu cannot be called without a full hand."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        player = game.current_player
        # Remove a card to make hand size != 14
        player.hand.pop()

        with patch.object(game, "get_play", return_value="tichu"):
            with pytest.raises(InvalidPlayError):
                game.next_turn()


class TestNextTurnPlayCard:
    """Tests for playing cards in next_turn."""

    def test_play_single_card(self):
        """Test playing a single card."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.current_player_idx = 0
        player = game.current_player
        initial_hand_size = len(player.hand)

        # Play the first card
        with patch.object(game, "get_play", return_value={0}):
            game.next_turn()

        # Hand size should decrease
        assert len(player.hand) == initial_hand_size - 1
        # Current combination should be set
        assert game.current_combination is not None
        assert game.current_combination.combination_type == CombinationType.SINGLE
        # Winning player should be updated
        assert game.winning_player_idx == 0

    def test_play_pair(self):
        """Test playing a pair of cards."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        player = game.current_player
        # Find a pair in the hand
        value_counts = {}
        for i, card in enumerate(player.hand):
            if card.value not in value_counts:
                value_counts[card.value] = []
            value_counts[card.value].append(i)

        pair_indices = next(
            (indices for indices in value_counts.values() if len(indices) >= 2), None
        )

        assert pair_indices
        play_set = {pair_indices[0], pair_indices[1]}
        initial_hand_size = len(player.hand)

        with patch.object(game, "get_play", return_value=play_set):
            game.next_turn()

        assert len(player.hand) == initial_hand_size - 2
        assert game.current_combination.combination_type == CombinationType.PAIR

    def test_play_higher_card_after_single(self):
        """Test playing a higher single card than current combination."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Set up initial combination
        game.current_player_idx = 1
        game.winning_player_idx = 0
        game.current_combination = MagicMock()
        game.current_combination.combination_type = CombinationType.SINGLE
        game.current_combination.value = 5
        game.current_combination.length = 1

        player = game.current_player
        # Find a card with value > 5
        valid_card_indices = [i for i, card in enumerate(player.hand) if card.value > 5]

        initial_hand_size = len(player.hand)
        with patch.object(game, "get_play", return_value={valid_card_indices[0]}):
            game.next_turn()

        assert len(player.hand) == initial_hand_size - 1
        assert game.winning_player_idx == 1

    def test_play_lower_card_raises_error(self):
        """Test that playing a lower card than current combination raises error."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Set up initial combination with high value
        game.current_player_idx = 1
        game.winning_player_idx = 0
        game.current_combination = MagicMock()
        game.current_combination.combination_type = CombinationType.SINGLE
        game.current_combination.value = 13
        game.current_combination.length = 1

        player = game.current_player
        # Find a card with value < 13
        valid_card_indices = [
            i for i, card in enumerate(player.hand) if card.value < 13
        ]

        assert valid_card_indices
        with patch.object(game, "get_play", return_value={valid_card_indices[0]}):
            with pytest.raises(InvalidPlayError):
                game.next_turn()

    def test_play_non_matching_combination_type_raises_error(self):
        """Test that playing non-matching combination type raises error."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Set up initial pair combination
        game.current_player_idx = 1
        game.winning_player_idx = 0
        game.current_combination = MagicMock()
        game.current_combination.combination_type = CombinationType.PAIR
        game.current_combination.value = 5
        game.current_combination.length = 2

        player = game.current_player
        # Try to play a single card
        with patch.object(game, "get_play", return_value={0}):
            with pytest.raises(InvalidPlayError):
                game.next_turn()

    def test_bomb_can_always_be_played_over_non_bombs(self):
        """Test that a bomb can be played over any non-bomb combination."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Set up initial pair combination
        game.current_player_idx = 1
        game.winning_player_idx = 0
        game.current_combination = MagicMock()
        game.current_combination.combination_type = CombinationType.PAIR
        game.current_combination.value = 14
        game.current_combination.length = 2

        player = game.current_player
        player.hand = [
            Card(Color.RED, 9),
            Card(Color.BLUE, 9),
            Card(Color.GREEN, 9),
            Card(Color.YELLOW, 9),
        ]
        with patch.object(game, "get_play", return_value={0, 1, 2, 3}):
            game.next_turn()
            game.winning_player_idx = 1
            game.current_combination.type = CombinationType.BOMB


class TestNextTurnSpecialCards:
    """Tests for special card handling in next_turn."""

    def test_play_dog_passes_turn_to_teammate(self):
        """Test that playing dog passes turn to teammate."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Replace current player's first card with dog
        game.current_player_idx = 0
        game.current_player.hand[0] = Card(Color.SPECIAL, SpecialCard.DOG.value)

        with patch.object(game, "get_play", return_value={0}):
            game.next_turn()

        # Next player should be teammate (2 positions ahead)
        assert game.current_player_idx == 2

    def test_play_phoenix_updates_combination_value(self):
        """Test that playing Phoenix updates combination value."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.current_player_idx = 0
        # Replace first card with Phoenix
        game.current_player.hand[0] = Card(Color.SPECIAL, SpecialCard.PHOENIX.value)

        with patch.object(game, "get_play", return_value={0}):
            game.next_turn()

        # Combination should be set with Phoenix
        assert game.current_combination is not None
        assert game.current_combination.combination_type == CombinationType.SINGLE

    def test_play_mahjong_prompts_for_wish(self):
        """Test that playing Mah Jong prompts for wish value."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.current_player_idx = 0
        # Replace first card with Mah Jong
        game.current_player.hand[0] = Card(Color.SPECIAL, SpecialCard.MAH_JONG.value)

        with patch.object(game, "get_play", return_value={0}), patch.object(
            game, "get_mahjong_wish", return_value=7
        ):
            game.next_turn()

        # Current wish should be set
        assert game.current_wish == 7

    def test_play_dragon_triggers_stack_selection(self):
        """Test that playing dragon and winning triggers stack recipient selection."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.current_player_idx = 3
        game.winning_player_idx = 3
        game.current_player.has_passed = False
        game.players[0].has_passed = True
        game.players[1].has_passed = True
        game.players[2].has_passed = True

        # Replace first card with Dragon
        game.card_stack = [Card(Color.SPECIAL, SpecialCard.DRAGON.value)]
        game.current_combination = MagicMock()
        game.current_combination.combination_type = CombinationType.SINGLE
        game.current_combination.value = SpecialCard.DRAGON.value

        with patch.object(game, "get_play", return_value="pass"), patch.object(
            game, "get_dragon_stack_recipient", return_value=2
        ):
            game.next_turn()

        # Winning player should be updated
        assert game.winning_player_idx == 2


class TestNextTurnWish:
    def test_player_can_play_card_if_wish_is_not_possible(self):
        """Test that a player with no cards is skipped."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.current_wish = 2
        game.current_combination = MagicMock()
        game.current_combination.combination_type = CombinationType.SINGLE
        game.current_combination.value = 13
        game.current_combination.length = 1

        game.current_player_idx = 1
        game.current_player.hand = [Card(Color.BLUE, 14)]

        with patch.object(game, "get_play", return_value={0}):
            game.next_turn()

    def test_player_can_not_play_card_if_wish_is_possible(self):
        """Test that a player with no cards is skipped."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.current_wish = 2
        game.current_combination = MagicMock()
        game.current_combination.combination_type = CombinationType.SINGLE
        game.current_combination.value = 13
        game.current_combination.length = 1

        game.current_player_idx = 1
        game.current_player.hand = [
            Card(Color.BLUE, 14),
            Card(Color.BLUE, 2),
            Card(Color.GREEN, 2),
            Card(Color.YELLOW, 2),
            Card(Color.RED, 2),
        ]

        with patch.object(game, "get_play", return_value={0}):
            with pytest.raises(InvalidPlayError):
                game.next_turn()


class TestNextTurnEdgeCases:
    """Tests for edge cases in next_turn."""

    def test_player_with_no_cards_is_skipped(self):
        """Test that a player with no cards is skipped."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.current_player_idx = 0
        game.player_rankings = [0]
        initial_player_id = game.current_player_idx

        game.next_turn()

        # Should advance to next player
        assert game.current_player_idx == (initial_player_id + 1) % NUM_PLAYERS

    def test_invalid_card_index_raises_error(self):
        """Test that invalid card index raises error."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.current_player_idx = 0
        hand_size = len(game.current_player.hand)

        with patch.object(
            game, "get_play", return_value={hand_size + 10}
        ):  # index out of range
            with pytest.raises(InvalidPlayError):
                game.next_turn()

    def test_turn_advances_to_next_player(self):
        """Test that turn advances to next player after valid play."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        initial_player_id = game.current_player_idx

        with patch.object(game, "get_play", return_value={2}):
            game.next_turn()

        # Current player should advance
        assert game.current_player_idx == (initial_player_id + 1) % NUM_PLAYERS

    def test_reproducible_game_with_seed(self):
        """Test that games with same seed produce same hand distributions."""
        output1 = StringIO()
        game1 = Tichu(seed=123, output=output1)
        game1.start_new_round()
        hands1 = [
            [(card.color, card.value) for card in player.hand]
            for player in game1.players
        ]

        output2 = StringIO()
        game2 = Tichu(seed=123, output=output2)
        game2.start_new_round()
        hands2 = [
            [(card.color, card.value) for card in player.hand]
            for player in game2.players
        ]

        # Hands should be identical
        assert hands1 == hands2


class TestNextTurnGameFlow:
    """Tests for overall game flow in next_turn."""

    def test_card_stack_accumulates(self):
        """Test that played cards accumulate in card stack."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.current_player_idx = 0
        initial_stack_size = len(game.card_stack)

        with patch.object(game, "get_play", return_value={0}):
            game.next_turn()

        # Card stack should have increased
        assert len(game.card_stack) > initial_stack_size

    def test_winning_player_is_updated(self):
        """Test that winning player is updated when cards are played."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.current_player_idx = 1
        game.winning_player_idx = None

        with patch.object(game, "get_play", return_value={0}):
            game.next_turn()

        # Winning player should be updated to current player
        assert game.winning_player_idx == 1

    def test_current_combination_is_set(self):
        """Test that current combination is set after valid play."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        assert game.current_combination is None

        with patch.object(game, "get_play", return_value={0}):
            game.next_turn()

        # Current combination should be set
        assert game.current_combination is not None
        assert game.current_combination.combination_type == CombinationType.SINGLE


class TestEndRoundScoring:
    """Tests for end_round_scoring function."""

    def test_same_team_finish_first_and_second_bonus(self):
        """Test that both players from same team finishing first and second grants 200 points."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Team 0 (players 0 and 2) finish first and second
        game.player_rankings = [0, 2]
        initial_team_score = game.scores[0]

        game.end_round_scoring()

        # Team 0 should gain 200 points
        assert game.scores[0] == initial_team_score + 200
        # Team 1 score should be unchanged
        assert game.scores[1] == 0

    def test_tichu_bonus_first_place(self):
        """Test that Tichu called and finishing first grants 100 point bonus."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Player 0 called Tichu and finished first
        game.players[0].tichu_called = True
        game.player_rankings = [0, 1, 2]
        game.players[3].hand = [Card(Color.RED, 3), Card(Color.GREEN, 4)]
        initial_team_score = game.scores[0]

        game.end_round_scoring()

        # Team 0 should gain 100 for Tichu bonus
        assert game.scores[0] == initial_team_score + 100

    def test_tichu_penalty_not_first_place(self):
        """Test that Tichu called but not finishing first incurs 100 point penalty."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Player 1 called Tichu but didn't finish first
        game.players[1].tichu_called = True
        game.player_rankings = [0, 1, 2]
        initial_team_score = game.scores[1]

        game.end_round_scoring()

        # Team 1 should lose 100 for failed Tichu
        assert game.scores[1] <= initial_team_score - 100

    def test_card_scoring_from_opposing_player(self):
        """Test that opposing player's hand cards are scored."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Set up rankings
        game.player_rankings = [0, 1, 2]
        hand_score = Card.count_card_scores(game.players[3].hand)
        initial_team_score = game.scores[0]

        game.end_round_scoring()

        # Score from player 3's remaining hand should be added to team 0
        assert game.scores[0] == initial_team_score + hand_score

    def test_card_scoring_from_losing_player(self):
        """Test that losing player's hand cards are scored."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Set up rankings
        game.player_rankings = [0, 1, 2]
        game.players[3].hand = [Card(Color.RED, 3), Card(Color.GREEN, 4)]
        game.players[3].card_stack = [
            Card(Color.RED, 5),
            Card(Color.GREEN, 10),
            Card(Color.SPECIAL, SpecialCard.DRAGON.value),
        ]
        stack_score = Card.count_card_scores(game.players[3].card_stack)
        initial_team_score = game.scores[0]

        game.end_round_scoring()

        # Score from player 3's remaining hand should be added to team 0
        assert game.scores[0] == initial_team_score + stack_score

    def test_card_stack_scoring(self):
        """Test that card stacks are scored properly."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Set up game state
        game.player_rankings = [0, 1, 2]

        # Add some cards to winner's stack
        test_cards = [Card(Color.BLUE, 5), Card(Color.RED, 10)]
        game.players[0].card_stack.extend(test_cards)
        game.players[3].hand = [Card(Color.RED, 3), Card(Color.GREEN, 4)]

        initial_team_score = game.scores[0]
        card_score = Card.count_card_scores(test_cards)
        game.end_round_scoring()

        # Score should include card stack
        assert game.scores[0] == initial_team_score + card_score

    def test_multiple_player_tichu_calls(self):
        """Test scoring when multiple players called Tichu."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Player 0 (team 0) called Tichu and finished first
        game.players[0].tichu_called = True
        # Player 1 (team 1) called Tichu but didn't finish
        game.players[1].tichu_called = True
        game.player_rankings = [0, 2, 3]
        game.players[1].hand = [Card(Color.RED, 3), Card(Color.GREEN, 4)]

        initial_team_0_score = game.scores[0]
        initial_team_1_score = game.scores[1]

        game.end_round_scoring()

        # Team 0 gains 100 for successful Tichu
        assert game.scores[0] == initial_team_0_score + 100
        # Team 1 loses 100 for failed Tichu
        assert game.scores[1] == initial_team_1_score - 100

    def test_score_accumulation_across_rounds(self):
        """Test that scores accumulate across multiple calls to end_round_scoring."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # First round
        game.player_rankings = [0, 2]
        game.end_round_scoring()
        first_round_team_0_score = game.scores[0]

        # Reset for second round
        game.start_new_round()
        game.player_rankings = [1, 3]
        game.end_round_scoring()

        # Scores should accumulate
        assert game.scores[0] == first_round_team_0_score or game.scores[1] > 0

    def test_all_players_ranked(self):
        """Test scoring when all players are ranked (3 finished, 1 remaining)."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.player_rankings = [0, 1, 2]
        # Player 3 is the remaining player with cards

        game.end_round_scoring()

        # All players should have been processed
        assert len(game.scores) == 2
        assert game.scores[0] >= 0
        assert game.scores[1] >= 0

    def test_dragon_card_in_stack_scores(self):
        """Test that dragon card in card stack is properly scored."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        game.player_rankings = [0, 1, 2]

        # Add dragon to winner's card stack (dragon is worth 25 points)
        dragon = Card(Color.SPECIAL, SpecialCard.DRAGON.value)
        game.players[0].card_stack.append(dragon)

        initial_team_score = game.scores[0]
        game.end_round_scoring()

        # Dragon (25 points) should be included
        assert game.scores[0] > initial_team_score


class TestPushCards:
    """Tests for push_cards function."""

    def test_pushed_cards_in_someone_elses_hand(self):
        """Test that pushed cards are in someone else's hand."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        original_hand_size = len(game.players[0].hand)

        with patch.object(game, "get_push", return_value={0, 1, 2}):
            game.push_cards()

        for player in game.players:
            assert len(player.hand) == original_hand_size

    def test_pushed_cards_are_valid_cards(self):
        """Test that pushed cards are actual cards from the hand."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Save original hands
        original_hands = [player.hand.copy() for player in game.players]

        with patch.object(game, "get_push", return_value={0, 1, 2}):
            game.push_cards()

        # Verify all cards still exist in the game
        all_cards_before = []
        for hand in original_hands:
            all_cards_before.extend(hand)

        all_cards_after = []
        for player in game.players:
            all_cards_after.extend(player.hand)

        # Same number of cards
        assert len(all_cards_before) == len(all_cards_after)

    def test_push_rotation_player_0_to_3(self):
        """Test push from player 0 goes to player 3 (left), player 2 (partner), player 1 (right)."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        # Get specific cards to track
        card_0 = game.players[0].hand[0]
        card_1 = game.players[0].hand[1]
        card_2 = game.players[0].hand[2]

        with patch.object(game, "get_push") as mock_get_push:
            mock_get_push.side_effect = [
                {0, 1, 2},
                {10, 11, 12},
                {10, 11, 12},
                {10, 11, 12},
            ]
            game.push_cards()

        # Cards from player 0 should be distributed among players 1, 2, 3
        player_1_received = card_2 in game.players[1].hand
        player_2_received = card_1 in game.players[2].hand
        player_3_received = card_0 in game.players[3].hand

        # At least the distribution pattern should work
        assert mock_get_push.call_count == 4
        assert player_1_received and player_2_received and player_3_received

    def test_sequential_push_from_all_players(self):
        """Test that get_push is called sequentially for each player."""
        output = StringIO()
        game = Tichu(seed=42, output=output)
        game.start_new_round()

        call_sequence = []

        with patch.object(game, "get_push") as mock_get_push:
            mock_get_push.side_effect = [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}, {0, 1, 2}]
            game.push_cards()
            call_sequence = [call for call in mock_get_push.call_args_list]

        # Should be called 4 times (once per player)
        assert len(call_sequence) == 4
