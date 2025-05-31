import pygame
from Player import Player
from pygame.sprite import Sprite
from card import create_deck, shuffle_deck, deal_cards
from Player import all_sprites
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
deck = create_deck()
shuffle_deck(deck)
hands = deal_cards(deck, num_players=2, cards_per_player=2)
print("玩家手牌：", hands)

card_images = {}
for suit in ['S', 'H', 'D', 'C']:
    for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']:
        card_name = rank + suit
        img_path = f"assets/img/{card_name}.jpg"
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)           # 先載入圖片
            img = pygame.transform.scale(img, (60, 90)) # 再縮小
            card_images[card_name] = img                # 存進字典
        else:
            print(f"警告：找不到圖片 {img_path}")



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

    pygame.display.update()  # Update the display

pygame.quit()  # Quit Pygame