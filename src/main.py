import pygame
from player import Player, all_sprites
from pygame.sprite import Sprite
from card import Deck
import random
import os
from enum import Enum, auto
from action import PlayerAction
from result import PokerResult
from chips import Chips
from game_stage import GameStage

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
game_stage = GameStage.PREFLOP
next_stage_time = None
pending_next_stage = False
community_cards = []
deal_index = 0
winner_text = ""
result_time = None

player_bets = [0, 0]  # 記錄每位玩家本輪下注額
current_player = 0    # 0: 玩家1, 1: 玩家2
waiting_for_action = False

font = pygame.font.SysFont(None, 36)

button_rects = get_button_rects(WIDTH, HEIGHT)

last_mouse_check = pygame.time.get_ticks()

compare_players = PokerResult.compare_players
hand_rank = PokerResult.hand_rank
get_hand_type_name = PokerResult.get_hand_type_name
best_five = PokerResult.best_five

pot = 0

players = [Player(0), Player(1)]
big_blind_player = random.randint(0, 1)
players[big_blind_player].set_big_blind(True)
players[1 - big_blind_player].set_big_blind(False)

# 大盲下注10
bet = 0

big_blind_amount = 10
if players[big_blind_player].chips >= big_blind_amount:
    players[big_blind_player].chips -= big_blind_amount
    player_bets[big_blind_player] = big_blind_amount
    bet = big_blind_amount

player_positions = [
    (WIDTH // 2 - (len(hands[0]) * 80) // 2, HEIGHT - CARD_HEIGHT - 40),  # 玩家1：下中
    (WIDTH // 2 - (len(hands[1]) * 80) // 2, 40)                          # 玩家2：上中
    ]

# Main game loop
running = True
while running:
    clock.tick(FPS)  # Limit the frame rate to 60 FPS

    action = None

    # Quitting the game & 處理滑鼠釋放事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # 只在未顯示結果時才允許輸入
            if not showed_result:
                mouse_pos = pygame.mouse.get_pos()
                button_rects = get_button_rects(WIDTH, HEIGHT)
                action = PlayerAction.get_player_action(button_rects, mouse_pos, (1,0,0))
    
    # Update game state
    all_sprites.update()  # Update all sprites

    # Update screen
    screen.fill((0,0,0))  # Fill the screen with a color

    # Draw action buttons
    draw_action_buttons(screen, font, button_rects)

    now = pygame.time.get_ticks()

    for i, hand in enumerate(hands):
        start_x, y = player_positions[i]
        # 在手牌左邊顯示籌碼
        chip_text = font.render(f"Chips: {players[i].chips}", True, (255,255,255))
        chip_text_x = start_x - 180
        chip_text_y = y + CARD_HEIGHT // 2 - chip_text.get_height() // 2
        screen.blit(chip_text, (chip_text_x, chip_text_y))

        # 玩家1的下注顯示在手牌上方，玩家2維持在手牌下方
        bet_text = font.render(f"Bet: {player_bets[i]}", True, (0, 255, 255))
        if i == 0:
            bet_text_x = start_x
            bet_text_y = y - bet_text.get_height() - 10  # 手牌上方 10px
        else:
            bet_text_x = start_x
            bet_text_y = y + CARD_HEIGHT + 30  # 玩家2維持下方
        screen.blit(bet_text, (bet_text_x, bet_text_y))

        for j, card in enumerate(hand):
            # 玩家2只有在SHOWDOWN才亮牌
            if i == 1 and game_stage != GameStage.SHOWDOWN:
                img = card_images["BACK"]
            else:
                img = card_images[card]
            x = start_x + j * 80
            screen.blit(img, (x, y))
        # 取得目前最大牌型
        cards_to_check = hand + community_cards
        # 玩家1隨時顯示牌型，玩家2只在SHOWDOWN時顯示
        if i == 0:
            if len(cards_to_check) >= 5:
                best_rank = best_five(cards_to_check)
                hand_type = get_hand_type_name(best_rank)
            else:
                hand_type = ""
            text = font.render(hand_type, True, (255, 255, 255))
            text_x = start_x
            text_y = y + CARD_HEIGHT + 5
            screen.blit(text, (text_x, text_y))
        elif i == 1 and game_stage == GameStage.SHOWDOWN:
            best_rank = best_five(cards_to_check)
            hand_type = get_hand_type_name(best_rank)
            text = font.render(hand_type, True, (255, 255, 255))
            text_x = start_x
            text_y = y + CARD_HEIGHT + 5
            screen.blit(text, (text_x, text_y))

    # 攤牌結算只在 SHOWDOWN 階段
    if game_stage == GameStage.SHOWDOWN and not showed_result:
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
        if winner_text == "P1 WINS":
            players[0].chips += pot
            pot = 0
        elif winner_text == "P2 WINS":
            players[1].chips += pot
            pot = 0
        elif winner_text == "DRAW":
            players[0].chips += pot // 2
            players[1].chips += pot // 2
            pot = 0
        # 重置遊戲狀態
        deck = Deck()
        deck.shuffle()
        hands = deck.deal_player_hands(num_players=2, cards_per_player=2)
        community_cards.clear()
        deal_index = 0
        game_stage = GameStage.PREFLOP
        showed_result = False
        winner_text = ""
        result_time = None
        big_blind_player = 1 - big_blind_player
        players[big_blind_player].set_big_blind(True)
        players[1 - big_blind_player].set_big_blind(False)
        # 新大盲下注10
        big_blind_amount = 10
        player_bets = [0, 0]
        bet = 0
        if players[big_blind_player].chips >= big_blind_amount:
            players[big_blind_player].chips -= big_blind_amount
            player_bets[big_blind_player] = big_blind_amount
            bet = big_blind_amount

    # 行動
    if action and not pending_next_stage:
        if action == PlayerAction.FOLD:
            winner = 1 - current_player
            winner_text = f"P{winner+1} WINS"
            players[winner].chips += pot + sum(player_bets)
            pot = 0
            bet = 0
            player_bets = [0, 0]
            showed_result = True
            result_time = pygame.time.get_ticks()

        elif action == PlayerAction.CALL:
            max_bet = max(player_bets)
            call_amount = max_bet - player_bets[current_player]
            if players[current_player].chips >= call_amount:
                players[current_player].chips -= call_amount
                player_bets[current_player] += call_amount
            current_player = 1 - current_player

        elif action == PlayerAction.CHECK:
            if player_bets[current_player] == max(player_bets):
                current_player = 1 - current_player

        # 判斷是否可以進入下一階段（雙方下注額相等且都已行動）
        if player_bets[0] == player_bets[1]:
            if (player_bets[0] > 0 or player_bets[1] > 0) or action == PlayerAction.CHECK:
                # 設定等待進入下個階段
                pending_next_stage = True
                next_stage_time = pygame.time.get_ticks()

        elif action == PlayerAction.CHECK:
            # 只有當自己已經跟到最大注時才能 check
            if player_bets[current_player] == max(player_bets):
                current_player = 1 - current_player

        elif action == PlayerAction.CHECK:
            # 過牌：不扣籌碼、不加 bet
            if game_stage == GameStage.PREFLOP:
                for _ in range(3):
                    community_cards.append(deck.cards.pop(0))
                game_stage = GameStage.FLOP
                pot += bet
                bet = 0
            elif game_stage == GameStage.FLOP:
                community_cards.append(deck.cards.pop(0))
                game_stage = GameStage.TURN
                pot += bet
                bet = 0
            elif game_stage == GameStage.TURN:
                community_cards.append(deck.cards.pop(0))
                game_stage = GameStage.RIVER
                pot += bet
                bet = 0
            elif game_stage == GameStage.RIVER:
                # 河牌後最後一輪過牌，進入攤牌
                pot += bet
                bet = 0
                game_stage = GameStage.SHOWDOWN
            waiting_for_action = True

        # 2秒後進入下個階段
    if pending_next_stage and next_stage_time and pygame.time.get_ticks() - next_stage_time > 2000:
        pot += player_bets[0] + player_bets[1]
        player_bets = [0, 0]
        bet = 0
        if game_stage == GameStage.PREFLOP:
            for _ in range(3):
                community_cards.append(deck.cards.pop(0))
            game_stage = GameStage.FLOP
        elif game_stage == GameStage.FLOP:
            community_cards.append(deck.cards.pop(0))
            game_stage = GameStage.TURN
        elif game_stage == GameStage.TURN:
            community_cards.append(deck.cards.pop(0))
            game_stage = GameStage.RIVER
        elif game_stage == GameStage.RIVER:
            game_stage = GameStage.SHOWDOWN
        pending_next_stage = False
        next_stage_time = None
    
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

    if community_cards:
        pot_text = font.render(f"Pot: {pot}", True, (255, 255, 0))
        # 讓 pot 顯示在畫面正中央，公牌上方
        pot_x = WIDTH // 2 - pot_text.get_width() // 2
        pot_y = community_card_positions[0][1] - 40  # 公牌上方 40px
        screen.blit(pot_text, (pot_x, pot_y))

    pygame.display.update()  # Update the display

pygame.quit()  # Quit Pygame