import pygame
from player import Player
from card import Deck
from action import PlayerAction
from result import PokerResult
from chips import Chips
from game_stage import GameStage
from game_setting import load_game_settings
from bot import PokerBot
from game_flow import GameFlow
from action_handler import ActionHandler
from ui_utils import UIUtils

# Initialize Pygame and create a window
pygame.init()
game_setting = load_game_settings()
screen = pygame.display.set_mode((game_setting["WIDTH"], game_setting["HEIGHT"]))
pygame.display.set_caption("Python Poker")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# 遊戲初始化
game_state = GameFlow.init_game(game_setting)
NUM_PLAYERS = 6

# 取出狀態
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
bots = game_state["bots"]
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
best_five = PokerResult.best_five
get_hand_type_name = PokerResult.get_hand_type_name

running = True
first_loop = True
bot_action_delay = 1200  # ms

while running:
    clock.tick(game_setting["FPS"])
    button_rects = get_button_rects(game_setting["WIDTH"], game_setting["HEIGHT"])
    action = None

    max_bet = max(player_bets)
    to_call = max_bet - player_bets[current_player]
    min_raise_amount = Chips.get_min_raise_amount(
        game_stage, big_blind_amount, last_raise_amount
    )
    min_total_bet = Chips.get_min_total_bet(max_bet, min_raise_amount)
    any_allin = any(p.chips == 0 and player_bets[i] > 0 for i, p in enumerate(players))

    # 預設加注金額為最小加注
    if first_loop:
        raise_input_text = str(min_total_bet)
        first_loop = False
    display_raise_input = raise_input_text

    # 事件處理（只在這裡一次！）
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 只有輪到真人玩家時才處理按鈕
        if (
            not pending_next_stage
            and not showed_result
            and game_stage != GameStage.SHOWDOWN
            and current_player == 0
            and not any_allin
        ):
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                action = PlayerAction.get_player_action(button_rects, mouse_pos, (1, 0, 0))
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                raise_input_rect = PlayerAction.get_raise_input_rect(button_rects)
                if raise_input_rect and raise_input_rect.collidepoint(mouse_pos):
                    raise_input_active = True
                else:
                    raise_input_active = False
                    if raise_input_text == "":
                        raise_input_text = str(min_total_bet)
                    elif raise_input_text.isdigit():
                        if int(raise_input_text) < min_total_bet:
                            raise_input_text = str(min_total_bet)
                    else:
                        raise_input_text = str(min_total_bet)

    # --- Bot行動 ---
    action_bot, bot_action_pending, bot_action_time, bot_action_result, raise_input_text = PokerBot.handle_bot_action(
        bots,
        hands,
        community_cards,
        player_bets,
        players,
        min_raise_amount,
        to_call,
        game_stage,
        current_player,
        showed_result,
        pending_next_stage,
        bot_action_pending,
        bot_action_time,
        bot_action_result,
        raise_input_text,
        bot_action_delay
    )
    if not bot_action_pending and action_bot is not None and current_player != 0:
        action = action_bot

    # 行動處理（真人或 bot）
    if action is not None and not bot_action_pending:
        result = ActionHandler.handle_action(
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
        pot_given = result.get("pot_given", pot_given)
        pot_give_time = result.get("pot_give_time", pot_give_time)
        if result.get("continue_flag"):
            continue

    # 2秒後進入下個階段
    if (
        pending_next_stage
        and next_stage_time
        and pygame.time.get_ticks() - next_stage_time > 2000
    ):
        actions_this_round = 0
        acted_this_round = [False] * len(players)
        pot += sum(player_bets)
        player_bets = [0] * len(players)
        bet = 0
        min_raise_amount = big_blind_amount
        raise_input_text = str(min_raise_amount)
        display_raise_input = raise_input_text

        if not showed_hands:
            last_actions = [""] * len(players)

        # 進入下一階段
        game_stage, community_cards, current_player = GameStage.advance_stage(
            game_stage, deck, community_cards, big_blind_player, players
        )

        if game_stage == GameStage.SHOWDOWN:
            showed_result = False
            showed_hands = False
            showdown_time = None
            pending_next_stage = False
            next_stage_time = None
        else:
            pending_next_stage = False
            next_stage_time = None

    # Update screen
    screen.fill((0, 0, 0))

    # Draw action buttons（只顯示真人）
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

    any_allin = any(p.chips == 0 and player_bets[i] > 0 for i, p in enumerate(players))

    if (
        not pending_next_stage
        and not showed_result
        and game_stage != GameStage.SHOWDOWN
        and current_player == 0
        and not any_allin
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
        # 籌碼
        UIUtils.draw_chip_text(screen, font, players[i].chips, start_x, y, game_setting["CARD_HEIGHT"])

        # 下注額顯示在面向中心
        bet_x, bet_y = UIUtils.get_bet_text_pos(start_x, y, hand, game_setting["CARD_HEIGHT"], game_setting)
        bet_text = font.render(f"{player_bets[i]}", True, (0, 255, 255))
        bet_text_rect = bet_text.get_rect(center=(bet_x, bet_y))
        screen.blit(bet_text, bet_text_rect)

        # 棄牌玩家不顯示手牌和牌型，但要顯示行動圓點與行動
        if getattr(players[i], "is_folded", False):
            # 行動圓點
            UIUtils.draw_action_dot(
                screen,
                i == current_player and not showed_result and not pending_next_stage and game_stage != GameStage.SHOWDOWN,
                start_x, y, hand, game_setting["CARD_HEIGHT"]
            )
            # 行動顯示
            UIUtils.draw_action_on_hand(screen, last_actions[i], start_x, y, hand, game_setting["CARD_HEIGHT"])
            continue  # 跳過手牌和牌型

        # 手牌
        show_hand = (i == 0) or (i != 0 and (showed_hands or game_stage == GameStage.SHOWDOWN))
        UIUtils.draw_hand(screen, hand, card_images, start_x, y, show_hand)
        # 牌型
        cards_to_check = hand + community_cards
        if show_hand and len(cards_to_check) >= 5:
            best_rank = best_five(cards_to_check)
            hand_type = get_hand_type_name(best_rank)
        else:
            hand_type = ""
        if show_hand:
            UIUtils.draw_hand_type(screen, font, hand_type, start_x, y, hand, game_setting["CARD_HEIGHT"])
        # 行動圓點
        UIUtils.draw_action_dot(
            screen,
            i == current_player and not showed_result and not pending_next_stage and game_stage != GameStage.SHOWDOWN,
            start_x, y, hand, game_setting["CARD_HEIGHT"]
        )
        # 行動顯示
        UIUtils.draw_action_on_hand(screen, last_actions[i], start_x, y, hand, game_setting["CARD_HEIGHT"])

    # 公牌
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
        ),
        (
            game_setting["WIDTH"] // 2 + 100 - game_setting["CARD_WIDTH"] // 2,
            game_setting["HEIGHT"] // 2 - game_setting["CARD_HEIGHT"] // 2,
        ),
        (
            game_setting["WIDTH"] // 2 + 2 * 100 - game_setting["CARD_WIDTH"] // 2,
            game_setting["HEIGHT"] // 2 - game_setting["CARD_HEIGHT"] // 2,
        ),
    ]
    UIUtils.draw_community_cards(screen, card_images, community_cards, community_card_positions)

    if community_cards:
        UIUtils.draw_pot_text(screen, font, pot, community_card_positions, game_setting["WIDTH"])

    # SHOWDOWN 階段：顯示勝者並自動進入下一局
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

        # pot 分配完畢後，延遲2秒自動開新局
        if pot_given and pot_give_time and pygame.time.get_ticks() - pot_give_time > 2000:
            (
                deck,
                hands,
                community_cards,
                deal_index,
                game_stage,
                showed_result,
                showed_hands,
                winner_text,
                result_time,
                showdown_time,
                pot_given,
                pot_give_time,
                big_blind_player,
                big_blind_amount,
                player_bets,
                acted_this_round,
                bet,
                current_player,
                last_raise_amount,
                last_actions,
                bot_action_pending,
            ) = GameFlow.reset_game(
                deck, players, Chips, big_blind_player, big_blind_amount
            )
            pot = 0
            for player in players:
                if player.chips == 0:
                    player.chips = Chips.chips

    pygame.display.update()

pygame.quit()
