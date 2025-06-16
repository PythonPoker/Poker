from action import PlayerAction
from game_stage import GameStage
import pygame

class ActionHandler:
    def __init__(self):
        self.pot_given = False
        self.pot_give_time = None

    @staticmethod
    def get_next_active_player(players, acted_this_round, current_player):
        """取得下一個有籌碼且未棄牌的玩家index"""
        num_players = len(players)
        for offset in range(1, num_players + 1):
            idx = (current_player + offset) % num_players
            if players[idx].chips > 0 and not acted_this_round[idx]:
                return idx
        return current_player


    def count_active_players(players, player_bets):
        """計算還有籌碼且未棄牌且有下注的玩家數"""
        return sum(1 for i, p in enumerate(players) if p.chips > 0 or player_bets[i] > 0)


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
        num_players = len(players)

        actions_this_round += 1
        acted_this_round[current_player] = True
        prev_player = current_player  # 保存當前玩家

        if action == PlayerAction.FOLD:
            last_actions[current_player] = "FOLD"
            players[current_player].fold()  # 標記已棄牌

            # 只剩一個未棄牌玩家才直接結束（不管籌碼，只看 is_folded）
            not_folded_players = [i for i, p in enumerate(players) if not getattr(p, "is_folded", False)]
            if len(not_folded_players) == 1:
                winner = not_folded_players[0]
                game_stage = GameStage.SHOWDOWN
                showed_hands = True
                showed_result = False
                pending_next_stage = False
                result_time = None
                showdown_time = None
                winner_text = f"P{winner+1} WINS"
                pot += sum(player_bets)
                players[winner].chips += pot
                pot = 0
                pot_given = True
                pot_give_time = pygame.time.get_ticks()
                # 重設所有下注
                player_bets = [0 for _ in range(num_players)]
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
                    "continue_flag": False,
                    "pot_given": pot_given,
                    "pot_give_time": pot_give_time,
                }
            else:
                current_player = ActionHandler.get_next_active_player(players, acted_this_round, current_player)

        elif action == PlayerAction.CALL_OR_CHECK:
            max_bet = max(player_bets)
            if player_bets[current_player] < max_bet:
                call_amount = max_bet - player_bets[current_player]
                if players[current_player].chips <= call_amount:
                    # ALL-IN
                    call_amount = players[current_player].chips
                    player_bets[current_player] += call_amount
                    players[current_player].chips = 0
                    last_actions[current_player] = "ALL-IN"
                    showed_hands = True  # 立即攤牌
                else:
                    players[current_player].chips -= call_amount
                    player_bets[current_player] += call_amount
                    last_actions[current_player] = "CALL"
            else:
                last_actions[current_player] = "CHECK"

            # 換到下一個有籌碼且未 acted 的玩家
            current_player = ActionHandler.get_next_active_player(players, acted_this_round, current_player)

        elif action == PlayerAction.BET_OR_RAISE:
            max_bet = max(player_bets)
            to_call = max_bet - player_bets[current_player]
            max_raise = players[current_player].chips
            if display_raise_input.isdigit():
                raise_amount = int(display_raise_input)
                total_bet = raise_amount
                min_total_bet = max_bet + min_raise_amount if max_bet > 0 else min_raise_amount
                if total_bet >= min_total_bet and total_bet <= max_bet + max_raise:
                    pay = total_bet - player_bets[current_player]
                    pay = min(pay, players[current_player].chips)
                    players[current_player].chips -= pay
                    player_bets[current_player] += pay
                    if players[current_player].chips == 0:
                        last_actions[current_player] = "ALL-IN"
                    elif max_bet == 0:
                        last_actions[current_player] = "BET"
                    else:
                        last_actions[current_player] = "RAISE"
                    raise_input_text = ""
                    # 加注後，所有人都要重新行動
                    acted_this_round = [False for _ in range(num_players)]
                    acted_this_round[current_player] = True
                    # 換到下一個有籌碼且未 acted 的玩家
                    current_player = ActionHandler.get_next_active_player(players, acted_this_round, current_player)

        # 判斷是否可以進入下一階段（所有有籌碼玩家都已行動且下注額相等）
        active_players = [i for i, p in enumerate(players) if p.chips > 0 or player_bets[i] > 0]
        all_acted = all(acted_this_round[i] for i in active_players)
        all_equal_bet = len(set(player_bets[i] for i in active_players)) == 1

        # 如果所有有籌碼玩家都ALL-IN，立即進入下一階段
        both_allin = all(players[i].chips == 0 for i in active_players)
        if both_allin:
            pending_next_stage = True
            result_time = pygame.time.get_ticks()
            showed_hands = True
        elif all_acted and all_equal_bet:
            pending_next_stage = True
            result_time = pygame.time.get_ticks()
            if any(players[i].chips == 0 for i in active_players) and game_stage != GameStage.SHOWDOWN:
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
