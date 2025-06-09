from action import PlayerAction
from game_stage import GameStage
import pygame


def handle_action(
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
):
    winner_text = None
    continue_flag = False

    actions_this_round += 1
    acted_this_round[current_player] = True
    prev_player = current_player  # 保存當前玩家

    if action == PlayerAction.FOLD:
        last_actions[current_player] = "FOLD"
        other_player = 1 - current_player
        game_stage = GameStage.SHOWDOWN
        showed_hands = True
        showed_result = False
        pending_next_stage = False
        result_time = None
        showdown_time = None
        winner_text = f"P{other_player+1} WINS"
        pot += player_bets[0] + player_bets[1]
        players[other_player].chips += pot
        pot = 0
        pot_given = True
        pot_give_time = pygame.time.get_ticks()
        return {
            "actions_this_round": actions_this_round,
            "acted_this_round": acted_this_round,
            "current_player": current_player,
            "last_actions": last_actions,
            "player_bets": [0, 0],
            "pot": pot,
            "bet": bet,
            "showed_result": showed_result,
            "result_time": result_time,
            "pending_next_stage": pending_next_stage,
            "game_stage": game_stage,
            "showed_hands": showed_hands,
            "showdown_time": showdown_time,
            "raise_input_text": raise_input_text,
            "winner_text": winner_text,
            "continue_flag": False,
            "pot_given": pot_given,
            "pot_give_time": pot_give_time,
        }

    elif action == PlayerAction.CALL_OR_CHECK:
        max_bet = max(player_bets)
        min_bet = min(player_bets)
        if player_bets[current_player] < max_bet:
            call_amount = max_bet - player_bets[current_player]
            if players[current_player].chips <= call_amount:
                over_bet = player_bets[1 - current_player] - (
                    players[current_player].chips + player_bets[current_player]
                )
                if over_bet > 0:
                    player_bets[1 - current_player] -= over_bet
                    players[1 - current_player].chips += over_bet
                player_bets[current_player] += players[current_player].chips
                players[current_player].chips = 0
                last_actions[current_player] = "ALL-IN"
                showed_hands = True  # 立即攤牌
            else:
                players[current_player].chips -= call_amount
                player_bets[current_player] += call_amount
                last_actions[current_player] = "CALL"
        else:
            last_actions[current_player] = "CHECK"
        last_actions[1 - current_player] = ""

        # 如果是Button玩家，則換到大盲玩家行動
        if game_stage == GameStage.PREFLOP:
            current_player = 1 - current_player
        else:
            current_player = 1 - current_player

    elif action == PlayerAction.BET_OR_RAISE:
        max_bet = max(player_bets)
        to_call = max_bet - player_bets[current_player]
        max_raise = players[current_player].chips
        if display_raise_input.isdigit():
            raise_amount = int(display_raise_input)
            # 這次要補的錢
            total_bet = raise_amount
            min_total_bet = (
                max_bet + min_raise_amount if max_bet > 0 else min_raise_amount
            )
            # 判斷是否達到最小加注
            if total_bet >= min_total_bet and total_bet <= max_bet + max_raise:
                pay = total_bet - player_bets[current_player]
                pay = min(pay, players[current_player].chips)
                players[current_player].chips -= pay
                player_bets[current_player] += pay
                #若下注後籌碼歸零，顯示ALL-IN
                if players[current_player].chips == 0:
                    if players[1 - current_player].chips == 0:
                        # 雙方都 ALL-IN，立即設定為待進入下一階段
                        pending_next_stage = True
                        result_time = pygame.time.get_ticks()
                    # 確保大盲注顯示正確的總籌碼
                    if current_player == big_blind_player:
                        # 將玩家的總下注額設為初始籌碼 (通常為 1000)
                        total_chips = player_bets[current_player] + players[current_player].chips
                        # 對於大盲，這應該是 1000 (990 + 10)
                        player_bets[current_player] = total_chips
                elif max_bet == 0:
                    last_actions[current_player] = "BET"
                else:
                    last_actions[current_player] = "RAISE"
                last_actions[1 - current_player] = ""
                current_player = 1 - current_player
                raise_input_text = ""

    # 判斷是否可以進入下一階段（雙方下注額相等且都已行動）
    # 如果雙方都ALL-IN，立即進入下一階段
    both_allin = all(p.chips == 0 for p in players)
    if both_allin:
        pending_next_stage = True
        result_time = pygame.time.get_ticks()
        showed_hands = True
    elif all(acted_this_round) and player_bets[0] == player_bets[1]:
        if (
            game_stage == GameStage.PREFLOP
            and acted_this_round[big_blind_player] == False
        ):
            current_player = big_blind_player
            acted_this_round[big_blind_player] = False
        else:
            pending_next_stage = True
            result_time = pygame.time.get_ticks()
            if any(p.chips == 0 for p in players) and game_stage != GameStage.SHOWDOWN:
                showed_hands = True  # 立即公開手牌

    return {
        "actions_this_round": actions_this_round,
        "acted_this_round": acted_this_round,
        "current_player": current_player,
        "last_actions": last_actions,
        "player_bets": player_bets,
        "pot": pot,
        "bet": bet,
        "showed_result": showed_result,
        "result_time": result_time,
        "pending_next_stage": pending_next_stage,
        "game_stage": game_stage,
        "showed_hands": showed_hands,
        "showdown_time": showdown_time,
        "raise_input_text": raise_input_text,
        "winner_text": winner_text,
        "continue_flag": continue_flag,
    }
