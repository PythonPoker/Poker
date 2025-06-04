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
from game_setting import load_game_settings

# Initialize Pygame and create a window
pygame.init()
game_setting = load_game_settings()
print(game_setting)
screen = pygame.display.set_mode((game_setting["WIDTH"], game_setting["HEIGHT"]))
pygame.display.set_caption("Python Poker")
clock = pygame.time.Clock()
# Create a player instance
deck = Deck()
deck.shuffle()
hands = deck.deal_player_hands(num_players=2, cards_per_player=2)
card_images = deck.load_card_images()
draw_action_buttons = PlayerAction.draw_action_buttons
get_button_rects = PlayerAction.get_button_rects
showed_hands = False
showed_result = False
showdown_time = None
handle_raise_input = PlayerAction.handle_raise_input
raise_input_text = ""
raise_input_active = False

pot_given = False
pot_give_time = None

game_stage = GameStage.PREFLOP
next_stage_time = None
pending_next_stage = False

community_cards = []
deal_index = 0
winner_text = ""
result_time = None

player_bets = [0, 0]  # 記錄每位玩家本輪下注額
waiting_for_action = False
actions_this_round = 0
last_actions = ["", ""]  # 記錄每位玩家最後的行動

font = pygame.font.SysFont(None, 36)

last_mouse_check = pygame.time.get_ticks()

compare_players = PokerResult.compare_players
hand_rank = PokerResult.hand_rank
get_hand_type_name = PokerResult.get_hand_type_name
best_five = PokerResult.best_five

pot = 0

players = [Player(0), Player(1)]
big_blind_player = random.randint(0, 1)
current_player = 1 - big_blind_player
players[big_blind_player].set_big_blind(True)
players[1 - big_blind_player].set_big_blind(False)

# 大盲下注10
bet = 0
big_blind_amount = 10
last_raise_amount = big_blind_amount

if players[big_blind_player].chips >= big_blind_amount:
    players[big_blind_player].chips -= big_blind_amount
    player_bets[big_blind_player] = big_blind_amount
    bet = big_blind_amount

player_positions = [
    (
        game_setting["WIDTH"] // 2 - (len(hands[0]) * 80) // 2,
        game_setting["HEIGHT"] - game_setting["CARD_HEIGHT"] - 40,
    ),  # 玩家1：下中
    (game_setting["WIDTH"] // 2 - (len(hands[1]) * 80) // 2, 40),  # 玩家2：上中
]

# Main game loop
running = True
while running:
    clock.tick(game_setting["FPS"])
    button_rects = get_button_rects(game_setting["WIDTH"], game_setting["HEIGHT"])
    action = None

    max_bet = max(player_bets)
    to_call = max_bet - player_bets[current_player]
    # 最小加注金額計算
    if max_bet > 0 and player_bets[1 - current_player] > 0:
        min_raise_amount = player_bets[1 - current_player] * 2 - player_bets[current_player]
        min_raise_amount = max(min_raise_amount, big_blind_amount)  # 不低於大盲
    else:
        min_raise_amount = big_blind_amount

    display_raise_input = raise_input_text

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            raise_input_rect = PlayerAction.get_raise_input_rect(button_rects)
            if raise_input_rect and raise_input_rect.collidepoint(mouse_pos):
                raise_input_active = True
                # 點擊輸入框時，如果目前是空的，填入預設
                if raise_input_text == "":
                    raise_input_text = str(min_raise_amount)
            else:
                # 點擊框外
                raise_input_active = False
                # 若玩家輸入的數字小於最小加注，則自動設為最小加注
                if raise_input_text.isdigit():
                    if int(raise_input_text) < min_raise_amount:
                        raise_input_text = str(min_raise_amount)
                    # 否則保留玩家輸入
                else:
                    # 若輸入不是數字，設為預設
                    raise_input_text = str(min_raise_amount)

        elif event.type == pygame.KEYDOWN and raise_input_active:
            raise_input_text = handle_raise_input(
                event,
                raise_input_text,
                min_raise_amount,
                players[current_player].chips
            )

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if not showed_result:
                mouse_pos = pygame.mouse.get_pos()
                action = PlayerAction.get_player_action(
                    button_rects, mouse_pos, (1, 0, 0)
                )

    # Update game state
    all_sprites.update()  # Update all sprites

    # Update screen
    screen.fill((0, 0, 0))  # Fill the screen with a color

    # Draw action buttons
    is_allin_input = (
        display_raise_input.isdigit() and 
        int(display_raise_input) == players[current_player].chips
    )
    raise_button_text = "ALL-IN" if is_allin_input else "RAISE"

    if not pending_next_stage and not showed_result and game_stage != GameStage.SHOWDOWN:
        draw_action_buttons(
            screen,
            font,
            button_rects,
            player_bets,
            current_player,
            players,
            raise_input=display_raise_input,
            min_raise=min_raise_amount,
            max_raise=players[current_player].chips,
            raise_button_text=raise_button_text,
        )

    now = pygame.time.get_ticks()

    for i, hand in enumerate(hands):
        start_x, y = player_positions[i]
        # 在手牌左邊顯示籌碼
        chip_text = font.render(f"Chips: {players[i].chips}", True, (255, 255, 255))
        chip_text_x = start_x - 180
        chip_text_y = y + game_setting["CARD_HEIGHT"] // 2 - chip_text.get_height() // 2
        screen.blit(chip_text, (chip_text_x, chip_text_y))

        # 在手牌左邊顯示最後行動
        action_text = font.render(last_actions[i], True, (200, 200, 0))
        action_text_x = chip_text_x
        action_text_y = chip_text_y + chip_text.get_height() + 5
        screen.blit(action_text, (action_text_x, action_text_y))

        # 判斷是否ALL-IN
        allin_this_round = (player_bets[i] > 0 and player_bets[i] == players[i].chips + player_bets[i] and players[i].chips == 0)
        # 其實只要本輪下注等於原本籌碼+本輪下注且籌碼為0就代表ALL-IN
        if player_bets[i] > 0 and players[i].chips == 0:
            bet_display = "ALL-IN"
        else:
            bet_display = f"{player_bets[i]}"

        bet_text = font.render(f"{bet_display}", True, (0, 255, 255))
        # 置中顯示下注額
        bet_text_x = start_x + (len(hand) * 80 - bet_text.get_width()) // 2
        if i == 0:
            bet_text_y = y - bet_text.get_height() - 10  # 手牌上方 10px
        else:
            bet_text_y = y + game_setting["CARD_HEIGHT"] + 10  # 玩家2維持下方
        screen.blit(bet_text, (bet_text_x, bet_text_y))

        for j, card in enumerate(hand):
            # 玩家2只有在SHOWDOWN或showed_hands時才亮牌
            if i == 1 and not showed_hands and game_stage != GameStage.SHOWDOWN:
                img = card_images["BACK"]
            else:
                img = card_images[card]
            x = start_x + j * 80
            screen.blit(img, (x, y))

        # 取得目前最大牌型
        cards_to_check = hand + community_cards

        # 玩家1隨時顯示牌型，玩家2只在SHOWDOWN時顯示
        if (i == 0) or (i == 1 and (showed_hands or game_stage == GameStage.SHOWDOWN)):
            if len(cards_to_check) >= 5:
                best_rank = best_five(cards_to_check)
                hand_type = get_hand_type_name(best_rank)
            else:
                hand_type = ""
            # 計算灰底位置與大小
            rect_x = start_x
            rect_y = y + game_setting["CARD_HEIGHT"] - 40  # 蓋住手牌下方
            rect_width = len(hand) * 80
            rect_height = 40
            pygame.draw.rect(screen, (60, 60, 60), (rect_x, rect_y, rect_width, rect_height))
            # 白字置中
            text = font.render(hand_type, True, (255, 255, 255))
            text_x = rect_x + (rect_width - text.get_width()) // 2
            text_y = rect_y + (rect_height - text.get_height()) // 2
            screen.blit(text, (text_x, text_y))

        # 在手牌右邊顯示黃點，表示輪到該玩家行動
        if (
            i == current_player
            and not showed_result
            and not pending_next_stage
            and game_stage != GameStage.SHOWDOWN
        ):
            dot_radius = 15
            dot_x = start_x + len(hand) * 80 + 30
            dot_y = y + game_setting["CARD_HEIGHT"] // 2
            pygame.draw.circle(screen, (255, 215, 0), (dot_x, dot_y), dot_radius)

    # SHOWDOWN階段：先公開手牌，3秒後顯示勝負，再2秒後自動開新局
    if game_stage == GameStage.SHOWDOWN:
        if not showed_hands:
            showdown_time = pygame.time.get_ticks()
            showed_hands = True
            pot_given = False
            pot_give_time = None
        elif showed_hands and not showed_result:
            # 等3秒後顯示勝負
            if showdown_time and pygame.time.get_ticks() - showdown_time > 3000:
                result = compare_players(hands[0], hands[1], community_cards)
                if result == 1:
                    winner_text = "P1 WINS"
                elif result == -1:
                    winner_text = "P2 WINS"
                else:
                    winner_text = "DRAW"
                showed_result = True
                result_time = pygame.time.get_ticks()
        elif showed_result and winner_text:
            # 顯示勝負
            text_surface = font.render(winner_text, True, (255, 255, 0))
            text_rect = text_surface.get_rect(
                center=(
                    game_setting["WIDTH"] // 2,
                    game_setting["HEIGHT"] // 2 + game_setting["CARD_HEIGHT"],
                )
            )
            screen.blit(text_surface, text_rect)
            now = pygame.time.get_ticks()
            # 2秒後加pot到勝者，只加一次
            if not pot_given and result_time and now - result_time > 2000:
                if winner_text == "P1 WINS":
                    players[0].chips += pot
                elif winner_text == "P2 WINS":
                    players[1].chips += pot
                elif winner_text == "DRAW":
                    players[0].chips += pot // 2
                    players[1].chips += pot // 2
                pot = 0
                pot_given = True
                pot_give_time = now

        # pot給出後再等2秒才開新局
        if pot_given and pot_give_time and now - pot_give_time > 2000:
            deck.shuffle()
            hands = deck.deal_player_hands(num_players=2, cards_per_player=2)
            community_cards.clear()
            deal_index = 0
            game_stage = GameStage.PREFLOP
            showed_result = False
            showed_hands = False
            winner_text = ""
            result_time = None
            showdown_time = None
            pot_given = False
            pot_give_time = None
            big_blind_player = 1 - big_blind_player
            players[big_blind_player].set_big_blind(True)
            players[1 - big_blind_player].set_big_blind(False)
            big_blind_amount = 10
            player_bets = [0, 0]
            bet = 0
            if players[big_blind_player].chips >= big_blind_amount:
                players[big_blind_player].chips -= big_blind_amount
                player_bets[big_blind_player] = big_blind_amount
                bet = big_blind_amount
            current_player = 1 - big_blind_player
            last_raise_amount = big_blind_amount

    # 行動
    if action and not pending_next_stage:
        actions_this_round += 1
        if action == PlayerAction.FOLD:
            last_actions[current_player] = "FOLD"
            last_actions[1 - current_player] = ""
            winner = 1 - current_player
            winner_text = f"P{winner+1} WINS"
            players[winner].chips += pot + sum(player_bets)
            pot = 0
            bet = 0
            player_bets = [0, 0]
            showed_result = True
            result_time = pygame.time.get_ticks()
            pending_next_stage = False
            actions_this_round = 0
            continue  # 跳過後續行動處理

        elif action == PlayerAction.CALL_OR_CHECK:
            max_bet = max(player_bets)
            if player_bets[current_player] < max_bet:
                last_actions[current_player] = "CALL"
                # CALL
                call_amount = max_bet - player_bets[current_player]
                if players[current_player].chips >= call_amount:
                    players[current_player].chips -= call_amount
                    player_bets[current_player] += call_amount
                else:
                    # 不夠CALL就ALL IN
                    player_bets[current_player] += players[current_player].chips
                    players[current_player].chips = 0
            # CHECK
            else:
                last_actions[current_player] = "CHECK"
            last_actions[1 - current_player] = ""
            current_player = 1 - current_player

        elif action == PlayerAction.BET_OR_RAISE:
            max_bet = max(player_bets)
            to_call = max_bet - player_bets[current_player]
            # 最小加注金額計算
            if max_bet > 0 and player_bets[1 - current_player] > 0:
                min_raise_amount = player_bets[1 - current_player] * 2 - player_bets[current_player]
                min_raise_amount = max(min_raise_amount, big_blind_amount)
            else:
                min_raise_amount = big_blind_amount
            max_raise = players[current_player].chips
            if display_raise_input.isdigit():
                raise_amount = int(display_raise_input)
                if min_raise_amount <= raise_amount <= max_raise:
                    if max(player_bets) == 0:
                        last_actions[current_player] = "BET"
                    else:
                        last_actions[current_player] = "RAISE"
                    last_actions[1 - current_player] = ""
                    # 處理加注
                    total_bet = to_call + raise_amount
                    total_bet = min(total_bet, players[current_player].chips + player_bets[current_player])
                    pay = total_bet - player_bets[current_player]
                    if players[current_player].chips < pay:
                        pay = players[current_player].chips
                    players[current_player].chips -= pay
                    player_bets[current_player] += pay
                    current_player = 1 - current_player
                    raise_input_text = ""

        # 判斷是否可以進入下一階段（雙方下注額相等且都已行動）
        if actions_this_round >= 2 and player_bets[0] == player_bets[1]:
                pending_next_stage = True
                next_stage_time = pygame.time.get_ticks()
                if any(p.chips == 0 for p in players) and game_stage != GameStage.SHOWDOWN:
                    showed_hands = True  # 立即公開手牌

    # 2秒後進入下個階段
    if (
        pending_next_stage
        and next_stage_time
        and pygame.time.get_ticks() - next_stage_time > 2000
    ):
        pot += player_bets[0] + player_bets[1]
        player_bets = [0, 0]
        bet = 0
        actions_this_round = 0
        min_raise_amount = big_blind_amount
        raise_input_text = ""
        last_actions = ["", ""]  # 重設行動紀錄
        
        # 翻牌、轉牌、河牌都要重設 current_player 為小盲
        if game_stage == GameStage.PREFLOP:
            for _ in range(3):
                community_cards.append(deck.cards.pop(0))
            game_stage = GameStage.FLOP
            current_player = big_blind_player
        elif game_stage == GameStage.FLOP:
            community_cards.append(deck.cards.pop(0))
            game_stage = GameStage.TURN
            current_player = big_blind_player
        elif game_stage == GameStage.TURN:
            community_cards.append(deck.cards.pop(0))
            game_stage = GameStage.RIVER
            current_player = big_blind_player
        elif game_stage == GameStage.RIVER:
            game_stage = GameStage.SHOWDOWN
            showed_result = False
            showed_hands = False
            showdown_time = None
        pending_next_stage = False
        next_stage_time = None

        # 若還有玩家ALL-IN且未到SHOWDOWN，繼續自動進入下階段
        if any(p.chips == 0 for p in players) and game_stage != GameStage.SHOWDOWN:
            pending_next_stage = True
            next_stage_time = pygame.time.get_ticks()
            showed_hands = True  # 持續公開手牌

    community_card_positions = [
        (
            game_setting["WIDTH"] // 2 - 2 * 100 - game_setting["CARD_WIDTH"] // 2,
            game_setting["HEIGHT"] // 2 - game_setting["CARD_HEIGHT"] // 2,
        ),
        (
            game_setting["WIDTH"] // 2 - 100 - game_setting["CARD_WIDTH"] // 2,
            game_setting["HEIGHT"] // 2 - game_setting["CARD_HEIGHT"] // 2,
        ),
        (
            game_setting["WIDTH"] // 2 - game_setting["CARD_WIDTH"] // 2,
            game_setting["HEIGHT"] // 2 - game_setting["CARD_HEIGHT"] // 2,
        ),  # 第三張正中間
        (
            game_setting["WIDTH"] // 2 + 100 - game_setting["CARD_WIDTH"] // 2,
            game_setting["HEIGHT"] // 2 - game_setting["CARD_HEIGHT"] // 2,
        ),
        (
            game_setting["WIDTH"] // 2 + 2 * 100 - game_setting["CARD_WIDTH"] // 2,
            game_setting["HEIGHT"] // 2 - game_setting["CARD_HEIGHT"] // 2,
        ),
    ]

    for idx, card in enumerate(community_cards):
        img = card_images[card]
        pos = community_card_positions[idx]
        screen.blit(img, pos)

    if community_cards:
        pot_text = font.render(f"Pot: {pot}", True, (255, 255, 0))
        # 讓 pot 顯示在畫面正中央，公牌上方
        pot_x = game_setting["WIDTH"] // 2 - pot_text.get_width() // 2
        pot_y = community_card_positions[0][1] - 40  # 公牌上方 40px
        screen.blit(pot_text, (pot_x, pot_y))

    pygame.display.update()  # Update the display

pygame.quit()  # Quit Pygame
