import pygame
from player import Player, all_sprites
from pygame.sprite import Sprite
from card import Deck
import random
import os
from enum import Enum, auto
from action import PlayerAction
from result import PokerResult


WIDTH = 1280
HEIGHT = 720
FPS = 60
CARD_WIDTH = 80
CARD_HEIGHT = 120

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
draw_action_buttons = PlayerAction.draw_action_buttons
get_button_rects = PlayerAction.get_button_rects
showed_result = False

community_cards = []
deal_index = 0
game_stage = 0
winner_text = ""
result_time = None

font = pygame.font.SysFont(None, 36)

button_rects = get_button_rects(WIDTH, HEIGHT)

last_mouse_check = pygame.time.get_ticks()

compare_players = PokerResult.compare_players
hand_rank = PokerResult.hand_rank
get_hand_type_name = PokerResult.get_hand_type_name
best_five = PokerResult.best_five

player_positions = [
    (WIDTH // 2 - (len(hands[0]) * 80) // 2, HEIGHT - CARD_HEIGHT - 40),  # 玩家1：下中
    (WIDTH // 2 - (len(hands[1]) * 80) // 2, 40)                          # 玩家2：上中
    ]

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
    screen.fill((0,0,0))  # Fill the screen with a color

    # Draw action buttons
    draw_action_buttons(screen, font, button_rects)
    # Get mouse position and pressed state
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    action = PlayerAction.get_player_action(button_rects, mouse_pos, mouse_pressed)
    action = PlayerAction.get_player_action(button_rects, mouse_pos, mouse_pressed)
    now = pygame.time.get_ticks()
    action = None

    for i, hand in enumerate(hands):
        start_x, y = player_positions[i]
        for j, card in enumerate(hand):
            img = card_images[card]
            x = start_x + j * 80
            screen.blit(img, (x, y))
    
    for i, hand in enumerate(hands):
        start_x, y = player_positions[i]
        for j, card in enumerate(hand):
            img = card_images[card]
            x = start_x + j * 80
            screen.blit(img, (x, y))
        # 取得目前最大牌型
        cards_to_check = hand + community_cards
        if len(cards_to_check) >= 5:
            best_rank = best_five(cards_to_check)
            hand_type = get_hand_type_name(best_rank)
        else:
            hand_type = ""
        # 顯示在手牌下方
        text = font.render(hand_type, True, (255, 255, 255))
        text_x = start_x
        text_y = y + CARD_HEIGHT + 5  # 在手牌下方5px
        screen.blit(text, (text_x, text_y))

    if len(community_cards) == 5 and not showed_result:
        result = compare_players(hands[0], hands[1], community_cards)
        if result == 1:
            winner_text = "P1 WINS"
        elif result == -1:
            winner_text = "P2 WINS"
        else:
            winner_text = "DRAW"
        showed_result = True
        result_time = pygame.time.get_ticks()
        
    if showed_result and winner_text:
        text_surface = font.render(winner_text, True, (255, 255, 0))
        text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + CARD_HEIGHT))
        screen.blit(text_surface, text_rect)

    # 勝負顯示3秒後自動開新局
    if showed_result and result_time and pygame.time.get_ticks() - result_time > 3000:
        deck = Deck()
        deck.shuffle()
        hands = deck.deal_player_hands(num_players=2, cards_per_player=2)
        community_cards.clear()
        deal_index = 0
        game_stage = 0
        showed_result = False
        winner_text = ""
        result_time = None

    if now - last_mouse_check >= 48:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        action = PlayerAction.get_player_action(button_rects, mouse_pos, mouse_pressed)
        last_mouse_check = now

    if action:
        if action == PlayerAction.FOLD:
            # 棄牌：重洗重發
            deck = Deck()
            deck.shuffle()
            hands = deck.deal_player_hands(num_players=2, cards_per_player=2)
            community_cards.clear()
            deal_index = 0
            game_stage = 0
            waiting_for_action = True
            showed_result = False
        elif action == PlayerAction.CALL or action == PlayerAction.CHECK:
            # 跟注或過牌：進入下一階段
            if game_stage == 0:
                # 翻牌（3張）
                for _ in range(3):
                    community_cards.append(deck.cards.pop(0))
                game_stage = 1
            elif game_stage in [1, 2]:
                # 轉牌或河牌（各1張）
                community_cards.append(deck.cards.pop(0))
                game_stage += 1
            waiting_for_action = True
    
    community_card_positions = [
    (WIDTH//2 - 2*100 - CARD_WIDTH//2, HEIGHT//2 - CARD_HEIGHT//2),
    (WIDTH//2 - 100   - CARD_WIDTH//2, HEIGHT//2 - CARD_HEIGHT//2),
    (WIDTH//2        - CARD_WIDTH//2, HEIGHT//2 - CARD_HEIGHT//2),  # 第三張正中間
    (WIDTH//2 + 100   - CARD_WIDTH//2, HEIGHT//2 - CARD_HEIGHT//2),
    (WIDTH//2 + 2*100 - CARD_WIDTH//2, HEIGHT//2 - CARD_HEIGHT//2),
    ]   

    for idx, card in enumerate(community_cards):
        img = card_images[card]
        pos = community_card_positions[idx]
        screen.blit(img, pos)
    

    


    pygame.display.update()  # Update the display

pygame.quit()  # Quit Pygame