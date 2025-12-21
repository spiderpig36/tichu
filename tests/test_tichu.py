import unittest
from unittest.mock import patch, MagicMock
from tichu.tichu import Tichu
from tichu.card import Card, Color, SpecialCard
from tichu.combination import Combination, CombinationType


class TestNextTurn(unittest.TestCase):
    
    def setUp(self):
        """Set up a fresh game for each test."""
        self.game = Tichu()
        self.game.start_new_round()
    
    @patch.object(Tichu, 'get_play', return_value={0})
    def test_next_turn_valid_single_card_play(self, mock_get_play):
        """Test playing a single valid card."""
        initial_player_id = self.game.current_player_id
        initial_hand_size = len(self.game.current_player.hand)
        
        self.game.next_turn()
        
        # Verify a card was played
        self.assertEqual(self.game.current_player_id, (initial_player_id + 1) % self.game.num_players)
        self.assertLess(len(self.game.players[initial_player_id].hand), initial_hand_size)
    
    @patch.object(Tichu, 'get_play', return_value='pass')
    def test_next_turn_pass(self, mock_get_play):
        """Test player passing their turn."""
        initial_player_id = self.game.current_player_id
        current_player = self.game.current_player
        
        self.game.next_turn()
        
        # Verify player passed
        self.assertTrue(current_player.has_passed)
        # Verify turn moved to next player
        self.assertEqual(self.game.current_player_id, (initial_player_id + 1) % self.game.num_players)
    
    @patch.object(Tichu, 'get_play', return_value={0})
    def test_next_turn_updates_current_combination(self, mock_get_play):
        """Test that current combination is updated after a valid play."""
        self.assertIsNone(self.game.current_combination)
        
        self.game.next_turn()
        
        # Verify a combination was set
        self.assertIsNotNone(self.game.current_combination)
        self.assertIsNotNone(self.game.winning_player_id)

    @patch.object(Tichu, 'get_play', side_effect=[{0}, {0}])
    def test_higher_combination_can_beat_lower(self, mock_get_play):
        """Test that a higher value combination can be played on a lower one."""
        # Set up player 0 with a low card (2) and player 1 with a high card (14)
        self.game.players[0].hand = [Card(Color.RED, 2)]
        self.game.players[1].hand = [Card(Color.GREEN, 14)]
        self.game.current_player_id = 0
        
        # Player 0 plays card with value 2
        self.game.next_turn()
        first_combination = self.game.current_combination
        first_winning_player = self.game.winning_player_id
        
        # Move to player 1
        self.game.current_player_id = 1
        
        # Player 1 plays card with value 14 (higher)
        self.game.next_turn()
        
        # Verify higher combination was accepted
        self.assertGreater(self.game.current_combination.value, first_combination.value)
        self.assertEqual(self.game.winning_player_id, 1)

    @patch.object(Tichu, 'get_play', side_effect=[{0}, {0}])
    def test_lower_combination_cannot_beat_higher(self, mock_get_play):
        """Test that a lower value combination cannot be played on a higher one."""
        # Set up player 0 with a high card (14) and player 1 with a low card (2)
        self.game.players[0].hand = [Card(Color.RED, 14)]
        self.game.players[1].hand = [Card(Color.GREEN, 2)]
        self.game.current_player_id = 0
        
        # Player 0 plays card with value 14
        self.game.next_turn()
        first_combination = self.game.current_combination
        first_winning_player = self.game.winning_player_id
        
        # Move to player 1
        self.game.current_player_id = 1
        
        # Player 1 tries to play card with value 2 (lower) - should be invalid
        self.game.next_turn()
        
        # Verify lower combination was rejected and current combination unchanged
        self.assertEqual(self.game.current_combination.value, first_combination.value)
        self.assertEqual(self.game.winning_player_id, first_winning_player)

    @patch.object(Tichu, 'get_play', return_value='pass')
    def test_play_multiple_cards_as_pair(self, mock_get_play):
        """Test playing multiple cards as a pair."""
        # Set up player with two cards of same value
        self.game.players[0].hand = [Card(Color.RED, 5), Card(Color.GREEN, 5)]
        self.game.current_player_id = 0
        
        with patch.object(Tichu, 'get_play', return_value={0, 1}):
            self.game.next_turn()
        
        # Verify pair was played
        self.assertIsNotNone(self.game.current_combination)
        self.assertEqual(self.game.current_combination.combination_type, CombinationType.PAIR)


if __name__ == '__main__':
    unittest.main()
