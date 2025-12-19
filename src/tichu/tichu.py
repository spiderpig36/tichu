import random

from card import NORMAL_CARD_VALUES, NUM_COLORS, Card, Color
from player import Player


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
        for color in range(NUM_COLORS):
            for value in NORMAL_CARD_VALUES:
                card = Card(Color(color), value)
                deck.append(card)
        deck.append(Card(Color.SPECIAL, 0))   # Dog
        deck.append(Card(Color.SPECIAL, 1))   # Mah Jong
        deck.append(Card(Color.SPECIAL, 15))  # Phoenix
        deck.append(Card(Color.SPECIAL, 16))  # Dragon

        random.shuffle(deck)
        for i, card in enumerate(deck):
            self.players[i % self.num_players].add_card(card)

        self.current_player = next(i for i, p in enumerate(self.players) if p.has_mahjong())


def __main__():
    print("Starting Tichu Game")
    game = Tichu()
    game.start_new_round()
    for player in game.players:
        print(player)

if __name__ == "__main__":
    __main__()


