import logging

from tichu import HAND_SIZE, NUM_PLAYERS
from tichu.card import NORMAL_CARD_VALUES
from tichu.player import Player


class HumanPlayer(Player):
    def get_card_play(self):
        play = self._get_input(
            "Enter the index of the card to play separated by a comma, 'pass' or 'tichu': "
        )
        if play == "pass":
            return "pass"
        if play == "tichu":
            return "tichu"
        try:
            card_indices = [int(idx.strip()) for idx in play.split(",")]
            return set(card_indices)
        except ValueError:
            logging.error(
                "Invalid input. Please enter valid card indices separated by commas. Try again."
            )
            return self.get_card_play()

    def get_grand_tichu_play(self):
        play = self._get_input("Enter 'grand_tichu' to call a grand tichu or 'pass': ")
        if play == "pass":
            return "pass"
        if play == "grand_tichu":
            return "grand_tichu"
        logging.error("Invalid input. Please enter 'pass' or 'grand_tichu'. Try again.")
        return self.get_grand_tichu_play()

    def get_dragon_stack_recipient_play(self) -> int:
        recipient = self._get_input(
            "Enter the index of the player who will receive the dragon stack: "
        )
        try:
            return int(recipient)
        except ValueError:
            logging.error(
                "Invalid input. Please enter a valid player index. Try again."
            )
            return self.get_dragon_stack_recipient_play()

    def get_mahjong_wish_play(self) -> int:
        wish = self._get_input("Enter the value of the card you wish for (2-14): ")
        try:
            value = int(wish)
            if value in NORMAL_CARD_VALUES:
                return value
            logging.error(
                "Invalid input. Please enter a value between 2 and 14. Try again."
            )
            return self.get_mahjong_wish_play()
        except ValueError:
            logging.error(
                "Invalid input. Please enter a numeric card value. Try again."
            )
            return self.get_mahjong_wish_play()

    def get_push_play(self) -> set[int]:
        push = self._get_input(
            "Enter cards to push, first player to the left, next partner player and last player to the right, separated by commas: "
        )
        try:
            card_indices = [int(idx.strip()) for idx in push.split(",")]
            if len(card_indices) != NUM_PLAYERS - 1:
                logging.error("You must enter exactly three card indices. Try again.")
                return self.get_push_play()
            if not all(0 <= idx < HAND_SIZE for idx in card_indices):
                logging.error("One or more card indices are out of range. Try again.")
                return self.get_push_play()
            return set(card_indices)
        except ValueError:
            logging.error(
                "Invalid input. Please enter valid card indices separated by commas. Try again."
            )
            return self.get_push_play()
