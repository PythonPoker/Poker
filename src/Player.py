import pygame
from pygame.sprite import Sprite

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

    def update(self):
        key_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)