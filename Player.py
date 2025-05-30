import pygame
from pygame.sprite import Sprite
import random

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.speedy = 5
        self.rect.center = (400, 300)

    def chips(self):
        self.chips = 1000
        return self.chips
    
    def card(self):
        self.card = random.randint(1, 13)
        return self.card
    def suit(self):
        self.suit = random.choice(['Hearts', 'Diamonds', 'Clubs', 'Spades'])
        return self.suit
    def bet(self, amount):
        if amount <= self.chips:
            self.chips -= amount
            return True
        else:
            return False

    def update(self):
        self.rect.y += self.speedy
        key_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        if mouse_pressed[0]:
            self.rect.x -= 5
        
        if mouse_pressed[2]:
            self.rect.x += 5 

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player) 