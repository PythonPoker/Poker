import pygame

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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # Fill the screen with black
    pygame.display.flip()  # Update the display