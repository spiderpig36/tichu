from .card import Card, Color


class Player:
    def __init__(self, name: str = "Anonymous"):
        self.name = name
        self.hand: list[Card] = []

    def add_card(self, card):
        """Add a card to the player's hand."""
        self.hand.append(card)

    def play_card(self, card):
        """Play a card from the player's hand."""
        if card in self.hand:
            self.hand.remove(card)
            return card
        raise ValueError(f"Card {card} not in hand")

    def get_hand(self):
        """Return the player's current hand."""
        return self.hand

    def has_mahjong(self):
        """Check if the player has the Mah Jong card."""
        return any([card for card in self.hand if card.color == Color.SPECIAL and card.value == 1])

    def __str__(self):
        hand = '\n  '.join([''] + [f"{i}: {card}" for i, card in enumerate(self.hand)])
        return f"Player {self.name} with hand: {hand}"
