from .card import Card, Color


class Player:
    def __init__(self, name: str = "Anonymous"):
        self.name = name
        self.hand: list[Card] = []
        self.card_stack: list[Card] = []
        self.reset_for_new_round()

    def reset_for_new_round(self):
        """Reset the player's state for a new round."""
        self.hand.clear()
        self.card_stack.clear()
        self.has_passed = False
        self.tichu_called = False

    def add_card(self, card):
        """Add a card to the player's hand."""
        self.hand.append(card)

    def play_card(self, card):
        """Play a card from the player's hand."""
        if card in self.hand:
            self.hand.remove(card)
            return card
        raise ValueError(f"Card {card} not in hand")

    def has_mahjong(self):
        """Check if the player has the Mah Jong card."""
        return any([card for card in self.hand if card.color == Color.SPECIAL and card.value == 1])

    def __str__(self):
        hand = '\n  '.join([''] + [f"{i}: {card}" for i, card in enumerate(self.hand)])
        return f"Player {self.name} with hand: {hand}"
