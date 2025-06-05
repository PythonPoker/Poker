import pygame
import random
import os
from player import Player, all_sprites
from pygame.sprite import Sprite
from card import Deck
from enum import Enum, auto
from action import PlayerAction
from result import PokerResult
from chips import Chips
from game_stage import GameStage
from game_setting import load_game_settings
from bot import PokerBot
from game_flow import GameFlow
from action_handler import handle_action

# Initialize Pygame and create a window
pygame.init()
game_setting = load_game_settings()
print(game_setting)
screen = pygame.display.set_mode((game_setting["WIDTH"], game_setting["HEIGHT"]))
pygame.display.set_caption("Python Poker")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
game_state = GameFlow.init_game(game_setting)
# Create a player instance
deck = game_state["deck"]
hands = game_state["hands"]
card_images = game_state["card_images"]
showed_hands = game_state["showed_hands"]
showed_result = game_state["showed_result"]
showdown_time = game_state["showdown_time"]
handle_raise_input = game_state["handle_raise_input"]
raise_input_text = game_state["raise_input_text"]
raise_input_active = game_state["raise_input_active"]
pot_given = game_state["pot_given"]
pot_give_time = game_state["pot_give_time"]
game_stage = game_state["game_stage"]
next_stage_time = game_state["next_stage_time"]
pending_next_stage = game_state["pending_next_stage"]
community_cards = game_state["community_cards"]
deal_index = game_state["deal_index"]
winner_text = game_state["winner_text"]
result_time = game_state["result_time"]
player_bets = game_state["player_bets"]
waiting_for_action = game_state["waiting_for_action"]
actions_this_round = game_state["actions_this_round"]
last_actions = game_state["last_actions"]
pot = game_state["pot"]
players = game_state["players"]
bot = game_state["bot"]
big_blind_player = game_state["big_blind_player"]
current_player = game_state["current_player"]
acted_this_round = game_state["acted_this_round"]
bet = game_state["bet"]
big_blind_amount = game_state["big_blind_amount"]
last_raise_amount = game_state["last_raise_amount"]
player_positions = game_state["player_positions"]
bot_action_pending = game_state["bot_action_pending"]
bot_action_time = game_state["bot_action_time"]
bot_action_result = game_state["bot_action_result"]

draw_action_buttons = PlayerAction.draw_action_buttons
get_button_rects = PlayerAction.get_button_rects
handle_raise_input = PlayerAction.handle_raise_input
last_mouse_check = pygame.time.get_ticks()
compare_players = PokerResult.compare_players
hand_rank = PokerResult.hand_rank
get_hand_type_name = PokerResult.get_hand_type_name
best_five = PokerResult.best_five

# Main game loop
running = True
first_loop = True
while running:
    clock.tick(game_setting["FPS"])
    button_rects = get_button_rects(game_setting["WIDTH"], game_setting["HEIGHT"])
    action = None

    max_bet = max(player_bets)
    to_call = max_bet - player_bets[current_player]
    # 最小加注金額計算
    max_bet = max(player_bets)
    to_call = max_bet - player_bets[current_player]
    min_raise_amount = Chips.get_min_raise_amount(
        game_stage, big_blind_amount, last_raise_amount
    )
    min_total_bet = Chips.get_min_total_bet(max_bet, min_raise_amount)

    # 預設加注金額為最小加注
    if first_loop:
        raise_input_text = str(min_total_bet)
        first_loop = False
    display_raise_input = raise_input_text

    # --- Bot行動 ---
    if (
        current_player == 1
        and not showed_result
        and not pending_next_stage
        and game_stage != GameStage.SHOWDOWN
    ):
        if not bot_action_pending:
            bot_action_time = pygame.time.get_ticks()
            bot_action_result = bot.act(
                hands[1],
                community_cards,
                player_bets,
                players,
                min_raise_amount,
                players[1].chips,
                to_call,
                game_stage,
                hands=hands,  # 傳入手牌以便bot計算
            )
            bot_action_pending = True
        elif pygame.time.get_ticks() - bot_action_time >= 2000:
            bot_action, bot_amount = bot_action_result
            if bot_action == "fold":
                action = PlayerAction.FOLD
            elif bot_action in ("call", "check"):
                action = PlayerAction.CALL_OR_CHECK
            elif bot_action in ("bet", "raise", "allin"):
                action = PlayerAction.BET_OR_RAISE
                raise_input_text = str(bot_amount)
            bot_action_pending = False
    else:
        bot_action_pending = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                raise_input_rect = PlayerAction.get_raise_input_rect(button_rects)
                if raise_input_rect and raise_input_rect.collidepoint(mouse_pos):
                    raise_input_active = True
                else:
                    # 點擊框外
                    raise_input_active = False
                    # 若玩家輸入的內容為空字串，才自動補最小加注
                    if raise_input_text == "":
                        raise_input_text = str(min_total_bet)
                    elif raise_input_text.isdigit():
                        if int(raise_input_text) < min_total_bet:
                            raise_input_text = str(min_total_bet)
                    else:
                        # 若不是數字且不是空字串，補最小加注
                        raise_input_text = str(min_total_bet)

            elif event.type == pygame.KEYDOWN and raise_input_active:
                raise_input_text = handle_raise_input(
                    event,
                    raise_input_text,
                    min_raise_amount,
                    players[current_player].chips,
                )
                if raise_input_text.isdigit():
                    max_raise = players[current_player].chips
                    if int(raise_input_text) > max_raise:
                        raise_input_text = str(max_raise)

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
    max_raise = players[current_player].chips
    is_allin_input = (
        display_raise_input.isdigit() and int(display_raise_input) == max_raise
    )
    if max_bet == 0:
        raise_button_text = "BET" if not is_allin_input else "ALL-IN"
    else:
        raise_button_text = "RAISE" if not is_allin_input else "ALL-IN"

    call_is_allin = to_call > 0 and players[current_player].chips == to_call
    call_button_text = (
        "ALL-IN" if call_is_allin else ("CHECK" if to_call == 0 else "CALL")
    )

    only_allin_call = (
        to_call == players[current_player].chips
        and players[current_player].chips > 0
        and min_raise_amount > players[current_player].chips
    )
    filtered_button_rects = button_rects
    if only_allin_call:
        filtered_button_rects = [
            (action, rect)
            for action, rect in button_rects
            if action != PlayerAction.BET_OR_RAISE
        ]

    if (
        not pending_next_stage
        and not showed_result
        and game_stage != GameStage.SHOWDOWN
        and not (
            current_player == 1 and bot_action_pending
        )  # 玩家2是bot且未行動時不顯示按鈕
    ):
        draw_action_buttons(
            screen,
            font,
            filtered_button_rects,
            player_bets,
            current_player,
            players,
            raise_input=display_raise_input,
            min_raise=min_raise_amount,
            max_raise=players[current_player].chips,
            raise_button_text=raise_button_text,
            call_button_text=call_button_text,
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
        allin_this_round = (
            player_bets[i] > 0
            and player_bets[i] == players[i].chips + player_bets[i]
            and players[i].chips == 0
        )

        # 顯示手牌下注額
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
            pygame.draw.rect(
                screen, (60, 60, 60), (rect_x, rect_y, rect_width, rect_height)
            )
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

    # 顯示勝負結果
    if game_stage == GameStage.SHOWDOWN:
        (
            showed_hands,
            showed_result,
            showdown_time,
            winner_text,
            result_time,
            pot_given,
            pot_give_time,
            pot,
        ) = PokerResult.showdown_result(
            hands,
            community_cards,
            players,
            pot,
            showed_hands,
            showed_result,
            showdown_time,
            winner_text,
            result_time,
            pot_given,
            pot_give_time,
            Chips,
            font,
            game_setting,
            screen,
        )

        # pot給出後再等2秒才開新局
        if pot_given and pot_give_time and now - pot_give_time > 2000:
            deck = Deck()
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
            acted_this_round = [False, False]
            bet = 0

            # 重設玩家籌碼
            for player in players:
                if player.chips == 0:
                    player.chips = Chips.chips

            if players[big_blind_player].chips >= big_blind_amount:
                players[big_blind_player].chips -= big_blind_amount
                player_bets[big_blind_player] = big_blind_amount
                bet = big_blind_amount
            current_player = 1 - big_blind_player
            last_raise_amount = big_blind_amount
            last_actions = ["", ""]

    # 行動
    if action and not pending_next_stage:
        result = handle_action(
            action,
            players,
            player_bets,
            last_actions,
            acted_this_round,
            current_player,
            game_stage,
            pot,
            bet,
            raise_input_text,
            min_raise_amount,
            display_raise_input,
            big_blind_player,
            showed_hands,
            showed_result,
            result_time,
            pending_next_stage,
            actions_this_round,
            showdown_time,
        )
        actions_this_round = result["actions_this_round"]
        acted_this_round = result["acted_this_round"]
        current_player = result["current_player"]
        last_actions = result["last_actions"]
        player_bets = result["player_bets"]
        pot = result["pot"]
        bet = result["bet"]
        showed_result = result["showed_result"]
        result_time = result["result_time"]
        if not pending_next_stage and result["pending_next_stage"]:
            next_stage_time = pygame.time.get_ticks()
        pending_next_stage = result["pending_next_stage"]
        game_stage = result["game_stage"]
        showed_hands = result["showed_hands"]
        showdown_time = result["showdown_time"]
        raise_input_text = result["raise_input_text"]
        winner_text = result["winner_text"] if result["winner_text"] else winner_text

        if result.get("continue_flag"):
            continue

    # 2秒後進入下個階段
    if (
        pending_next_stage
        and next_stage_time
        and pygame.time.get_ticks() - next_stage_time > 2000
    ):
        actions_this_round = 0
        acted_this_round = [False, False]
        pot += player_bets[0] + player_bets[1]
        player_bets = [0, 0]
        bet = 0
        min_raise_amount = big_blind_amount
        raise_input_text = str(min_raise_amount)
        display_raise_input = raise_input_text

        if not showed_hands:
            last_actions = ["", ""]

        # 使用 GameStage.advance_stage 進入下一階段
        game_stage, community_cards, current_player = GameStage.advance_stage(
            game_stage, deck, community_cards, big_blind_player
        )

        if game_stage == GameStage.SHOWDOWN:
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
