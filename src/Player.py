import pygame
from pygame.sprite import Sprite
from chips import Chips


class Player(pygame.sprite.Sprite):
    def __init__(self, player_id, chips=Chips.chips):
        super().__init__()
        self.player_id = player_id
        self.chips = chips
        self.is_big_blind = False

    def set_big_blind(self, is_bb):
        self.is_big_blind = is_bb

    def bet(self, amount):
        if self.chips >= amount:
            self.chips -= amount
            return amount
        else:
            bet_amt = self.chips
            self.chips = 0
            return bet_amt

    def add_chips(self, amount):
        self.chips += amount


all_sprites = pygame.sprite.Group()
