import pygame
from player import Player, all_sprites
from pygame.sprite import Sprite
from card import Deck
import random
import os


WIDTH = 800
HEIGHT = 600
FPS = 60

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Poker")
clock = pygame.time.Clock()
# Create a player instance
deck = Deck()
deck.shuffle()
hands = deck.deal_player_hands(num_players=2, cards_per_player=2)
card_images = deck.load_card_images()

community_cards = []
deal_index = 0
game_start_time = pygame.time.get_ticks()


# Main game loop
running = True
while running:
    clock.tick(FPS)  # Limit the frame rate to 60 FPS

    # Quitting the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # Update game state
    all_sprites.update()  # Update all sprites


    # Update screen
    screen.fill((255, 255, 255))  # Fill the screen with a color
  

    player_start_x = [100, 500]  # 玩家1從x=100，玩家2從x=500
    for i, hand in enumerate(hands):
        start_x = player_start_x[i]
        for j, card in enumerate(hand):
            img = card_images[card]
            x = start_x + j * 80
            y = 400 if i == 0 else 100  # 玩家1和玩家2不同Y座標
            screen.blit(img, (x, y))
    
    
        if pygame.time.get_ticks() - game_start_time > 3000:
            deal_index, game_start_time = deck.deal_community_cards(
                community_cards, deal_index, game_start_time
        )
    
    community_card_positions = [
        (WIDTH//2 - 2*70, HEIGHT//2 - 45),
        (WIDTH//2 - 70,   HEIGHT//2 - 45),
        (WIDTH//2,        HEIGHT//2 - 45),
        (WIDTH//2 + 70,   HEIGHT//2 - 45),
        (WIDTH//2 + 2*70, HEIGHT//2 - 45),
    ]
    for idx, card in enumerate(community_cards):
        img = card_images[card]
        pos = community_card_positions[idx]
        screen.blit(img, pos)

    pygame.display.update()  # Update the display

pygame.quit()  # Quit Pygame