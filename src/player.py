import pygame
from chips import Chips


class Player(pygame.sprite.Sprite):
    def __init__(self, player_id, chips=Chips.chips):
        super().__init__()
        self.player_id = player_id
        self.chips = chips
        self.is_folded = False
        self.is_big_blind = False

    def fold(self):
        self.is_folded = True

    def set_big_blind(self, is_bb):
        self.is_big_blind = is_bb

