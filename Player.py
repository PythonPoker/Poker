import pygame
from pygame.sprite import Sprite

class Player(Sprite):
    def __init__(self, name, position):
        super().__init__()
        self.name = name
        self.position = position
        self.hand = []
        self.chips = 1000  # Starting chips for the player
        self.is_active = True  # Indicates if the player is active in the game

    def add_card(self, card):
        """Add a card to the player's hand."""
        self.hand.append(card)

    def reset_hand(self):
        """Reset the player's hand for a new round."""
        self.hand.clear()

    def bet(self, amount):
        """Place a bet and deduct chips."""
        if amount <= self.chips:
            self.chips -= amount
            return True
        return False

    def receive_chips(self, amount):
        """Receive chips after winning a hand."""
        self.chips += amount