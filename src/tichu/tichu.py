import random
from .combination import Combination
from .card import NORMAL_CARD_VALUES, Card, Color
from .player import Player


class Tichu:
    def __init__(self, num_players: int = 4, goal_score: int = 1000):
        self.num_players = num_players
        self.goal_score = goal_score
        if self.num_players % 2 != 0:
            raise ValueError("Number of players must be even.")
        self.scores = [0] * (self.num_players // 2)
        self.current_round = 0
        self.current_player = 0
        self.players = [Player(f"Player {i}") for i in range(num_players)]

    def start_new_round(self):
        self.current_round += 1
        deck = []
        for color in Color:
            if color == Color.SPECIAL:
                continue
            for value in NORMAL_CARD_VALUES:
                card = Card(color, value)
                deck.append(card)
        deck.append(Card(Color.SPECIAL, -1))   # Dog
        deck.append(Card(Color.SPECIAL, 1))   # Mah Jong
        deck.append(Card(Color.SPECIAL, 15))  # Phoenix
        deck.append(Card(Color.SPECIAL, 16))  # Dragon

        random.shuffle(deck)
        for i, card in enumerate(deck):
            self.players[i % self.num_players].add_card(card)

        self.current_player = next(i for i, p in enumerate(self.players) if p.has_mahjong())
    
    def next_turn(self):
        print(self.players[self.current_player])
        current_hand = self.players[self.current_player].get_hand()

        played_cards = []
        while not played_cards:
            prompt = input("Enter the index of the card to play separated by a comma: ")
            try:
                card_indices = [int(idx.strip()) for idx in prompt.split(",")]
                played_cards = [card for i, card in enumerate(current_hand) if i in card_indices]
            except ValueError:
                print("Invalid input. Please enter valid card indices separated by commas.")
                continue

            try:
                self.current_combination = Combination.from_cards(played_cards)
                print(f"Played combination: {self.current_combination.combination_type.name}")
            except ValueError:
                print("Invalid combination of cards played. Try again.")
                played_cards = []
                continue
        
        print(", ".join([str(card) for card in played_cards]))

if __name__ == "__main__":
    print("Starting Tichu Game")
    game = Tichu()
    game.start_new_round()
    game.next_turn()


