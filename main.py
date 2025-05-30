import pygame
from Player import Player
from pygame.sprite import Sprite
from Player import all_sprites
import random


WIDTH = 800
HEIGHT = 600
FPS = 60

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Poker")
clock = pygame.time.Clock()

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
    all_sprites.draw(screen)  # Draw all sprites
    pygame.display.update()  # Update the display

pygame.quit()  # Quit Pygame