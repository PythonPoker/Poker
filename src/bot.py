import random
import numpy as np
import pygame
from game_stage import GameStage
from card import Deck
from result import PokerResult
from action import PlayerAction


class OpponentModel:
    def __init__(self):
        self.total_hands = 0
        self.raises = 0
        self.calls = 0
        self.folds = 0
        self.allins = 0
        self.big_raises = 0

    def update(self, action, bet_amount, pot, is_folded):
        self.total_hands += 1
        if is_folded:
            self.folds += 1
        elif action in ("RAISE", "BET"):
            self.raises += 1
            if bet_amount > pot * 0.7:
                self.big_raises += 1
        elif action == "CALL":
            self.calls += 1
        elif action == "ALL-IN":
            self.allins += 1

    def style(self):
        if self.total_hands == 0:
            return "unknown"
        raise_freq = self.raises / self.total_hands
        call_freq = self.calls / self.total_hands
        fold_freq = self.folds / self.total_hands
        big_raise_freq = self.big_raises / self.total_hands
        if raise_freq > 0.35 or big_raise_freq > 0.15:
            return "aggressive"
        elif fold_freq > 0.5:
            return "tight"
        elif call_freq > 0.5:
            return "loose"
        else:
            return "balanced"


# 全局保存對手模型
GLOBAL_OPP_MODELS = None


class PokerBot:
    def __init__(self, player_index, num_players=6):
        global GLOBAL_OPP_MODELS
        self.player_index = player_index
        self.num_players = num_players
        if GLOBAL_OPP_MODELS is None or len(GLOBAL_OPP_MODELS) != num_players:
            GLOBAL_OPP_MODELS = [OpponentModel() for _ in range(num_players)]
        self.opp_models = GLOBAL_OPP_MODELS
        self.is_bluffing = False
        self.last_bluff_street = None

    def get_position(self, player_index, dealer_index, num_players):
        """
        回傳玩家在本局的座位名稱
        """
        rel_pos = (player_index - dealer_index) % num_players
        if num_players == 6:
            pos_names = ["BTN", "SB", "BB", "UTG", "MP", "CO"]
        else:
            pos_names = [f"P{i}" for i in range(num_players)]
        return pos_names[rel_pos]

    def get_gto_thresholds(self, position, game_stage):
        """
        根據位置與階段回傳勝率門檻
        """
        # 這裡數值可依需求微調
        if game_stage == GameStage.PREFLOP:
            thresholds = {
                "UTG":  (0.75, 0.60, 0.45),
                "MP":   (0.72, 0.58, 0.43),
                "CO":   (0.66, 0.52, 0.38),  # 更鬆
                "BTN":  (0.62, 0.48, 0.34),  # 更鬆
                "SB":   (0.70, 0.55, 0.40),
                "BB":   (0.68, 0.53, 0.38),
            }
        else:
            # 翻牌後可略降門檻
            thresholds = {
                "UTG":  (0.70, 0.55, 0.40),
                "MP":   (0.68, 0.53, 0.38),
                "CO":   (0.62, 0.48, 0.34),  # 更鬆
                "BTN":  (0.58, 0.44, 0.30),  # 更鬆
                "SB":   (0.66, 0.51, 0.36),
                "BB":   (0.64, 0.49, 0.34),
            }
        # 預設
        return thresholds.get(position, (0.7, 0.55, 0.4))

    def estimate_win_rate(self, hand, community_cards, hands, players, num_simulations=300):
        """
        蒙地卡羅模擬，估算bot在目前情境下的勝率（支援多玩家）
        """
        import random

        wins = 0
        draws = 0
        total = 0

        # 找出已知牌（自己的手牌、所有已知手牌、已知公牌）
        used_cards = set(community_cards + hand)
        for i, h in enumerate(hands):
            if i != self.player_index and h and not getattr(players[i], "is_folded", False):
                used_cards.update(h)

        deck = Deck()
        deck.cards = [c for c in deck.cards if c not in used_cards]

        num_players = len(hands)
        for _ in range(num_simulations):
            sim_deck = deck.cards[:]
            random.shuffle(sim_deck)
            # 為每個對手分配手牌
            sim_hands = []
            for i in range(num_players):
                if i == self.player_index:
                    sim_hands.append(hand)
                elif hands[i] and not getattr(players[i], "is_folded", False):
                    sim_hands.append([sim_deck.pop(), sim_deck.pop()])
                else:
                    sim_hands.append([])  # 已棄牌玩家

            # 發滿公牌
            sim_community = community_cards[:]
            while len(sim_community) < 5:
                sim_community.append(sim_deck.pop())

            # 比牌
            winners, _ = PokerResult.compare_all_players(sim_hands, sim_community)
            if self.player_index in winners:
                if len(winners) == 1:
                    wins += 1
                else:
                    draws += 1 / len(winners)
            total += 1

        return (wins + draws) / total if total > 0 else 0.0

    def act(
        self,
        hand,
        community_cards,
        player_bets,
        players,
        min_raise,
        max_raise,
        to_call,
        game_stage,
        hands=None,
        dealer_index=0,
        last_actions=None,
    ):
        chips = players[self.player_index].chips
        num_players = len(players)
        win_rate = self.estimate_win_rate(
            hand, community_cards, hands, players, num_simulations=200
        )

        position = self.get_position(self.player_index, dealer_index, num_players)
        thr_high, thr_mid, thr_low = self.get_gto_thresholds(position, game_stage)

        # 統計場上行動
        num_raises = num_calls = num_folds = num_allins = 0
        pot = sum(player_bets)
        for i, act in enumerate(last_actions or []):
            if i == self.player_index or getattr(players[i], "is_folded", False):
                continue
            # 更新對手模型
            self.opp_models[i].update(
                act,
                player_bets[i],
                pot,
                getattr(players[i], "is_folded", False)
            )
            if act in ("RAISE", "BET"):
                num_raises += 1
            elif act == "CALL":
                num_calls += 1
            elif act == "FOLD":
                num_folds += 1
            elif act == "ALL-IN":
                num_allins += 1

        # 根據對手風格調整門檻
        adj_thr_high = thr_high
        adj_thr_mid = thr_mid
        adj_thr_low = thr_low
        bet_ratio = 0.5

        for i, opp in enumerate(self.opp_models):
            if i == self.player_index or getattr(players[i], "is_folded", False):
                continue
            style = opp.style()
            if style == "aggressive":
                adj_thr_high += 0.05
                adj_thr_mid += 0.05
            elif style == "tight":
                adj_thr_high -= 0.03
                adj_thr_mid -= 0.03
            elif style == "loose":
                adj_thr_high -= 0.05
                adj_thr_mid -= 0.05

        # 根據本輪行動調整
        if num_allins > 0:
            adj_thr_high += 0.10
            adj_thr_mid += 0.10
            bet_ratio = 1.0
        elif num_raises >= 2:
            adj_thr_high += 0.08
            adj_thr_mid += 0.08
            bet_ratio = 0.8
        elif num_raises == 1:
            adj_thr_high += 0.04
            adj_thr_mid += 0.04
            bet_ratio = 0.7
        elif num_folds >= num_players // 2:
            adj_thr_high -= 0.03
            adj_thr_mid -= 0.03
            bet_ratio = 0.7
        elif num_calls >= num_players // 2:
            bet_ratio = 0.6

        # 根據剩餘人數調整門檻
        active_players = [p for p in players if not getattr(p, "is_folded", False) and p.chips > 0]
        num_active = len(active_players)
        if num_active <= 3:
            adj_thr_high -= 0.04
            adj_thr_mid -= 0.04
            bet_ratio += 0.1
        elif num_active == 2:
            adj_thr_high -= 0.08
            adj_thr_mid -= 0.08
            bet_ratio += 0.2

        r = np.random.rand()
        max_bet = max(player_bets)
        min_total_bet = max_bet + min_raise if max_bet > 0 else min_raise

        # === 支援超池下注與更大preflop下注 ===
        overbet_ratio = 1.0
        if win_rate > adj_thr_high + 0.08 and r < 0.4:
            overbet_ratio = np.random.uniform(1.2, 2.0)
        elif r < 0.2:
            overbet_ratio = np.random.uniform(1.2, 2.0)

        # --- 新增：preflop第一輪允許大額下注 ---
        if game_stage == GameStage.PREFLOP and max(player_bets) <= min_raise:
            # 允許2~5倍大盲隨機下注
            blind_multi = np.random.choice([2, 2.5, 3, 4, 5])
            bet_amount = int(min_raise * blind_multi)
        elif to_call == 0:
            # 翻後沒人下注時，允許直接用底池比例下注
            bet_amount = int(pot * bet_ratio * overbet_ratio)
            bet_amount = max(min_raise, bet_amount)
            bet_amount = min(bet_amount, chips)
        else:
            # 有人下注時，加注必須 >= min_total_bet
            bet_amount = max(min_total_bet, int(pot * bet_ratio * overbet_ratio))
            bet_amount = min(bet_amount, chips)

        # === bluff 延續性邏輯 ===
        bluff_this_street = False

        # 若上一輪已bluff，進入新階段有較高機率繼續bluff
        if self.is_bluffing and self.last_bluff_street is not None:
            if game_stage.value > self.last_bluff_street.value:
                bluff_continue_chance = 0.7 if to_call == 0 else 0.5
                if np.random.rand() < bluff_continue_chance:
                    bluff_this_street = True
                    self.last_bluff_street = game_stage
                else:
                    self.is_bluffing = False
            else:
                bluff_this_street = True  # 同一階段繼續bluff

        # 若這輪本來就有bluff機率，且勝率低
        elif to_call == 0 and bet_ratio > 0 and win_rate < adj_thr_low and np.random.rand() < 0.15:
            bluff_this_street = True
            self.is_bluffing = True
            self.last_bluff_street = game_stage

        # GTO混合策略與pot odds
        pot_odds = to_call / (pot + to_call) if to_call > 0 else 0

        # 面對大額加注更謹慎
        if to_call > 0 and to_call > pot * 0.7 and win_rate < adj_thr_high + 0.05:
            return ("fold", 0)

        # 跟注不划算直接棄牌
        if to_call > 0 and win_rate < pot_odds:
            return ("fold", 0)

        if to_call == 0:
            if bluff_this_street:
                #print(f"[BOT] Flop/Turn/River bet_amount={bet_amount}, pot={pot}, bet_ratio={bet_ratio}, overbet_ratio={overbet_ratio}, min_raise={min_raise}")
                return ("bet", bet_amount)
            if bet_ratio > 0:
                # --- 強牌時更積極 ---
                if game_stage == GameStage.PREFLOP and win_rate > adj_thr_high:
                    # 翻前頂尖牌力，90%主動下注
                    if r < 0.9:
                        return ("bet", bet_amount)
                    else:
                        return ("check", 0)
                elif win_rate > adj_thr_high:
                    if r < 0.5:
                        return ("bet", bet_amount)
                    elif r < 0.8:
                        return ("check", 0)
                    else:
                        return ("bet", bet_amount)
                elif win_rate > adj_thr_mid:
                    if r < 0.7:
                        return ("check", 0)
                    else:
                        return ("bet", bet_amount)
                else:
                    if r < 0.05:
                        return ("bet", bet_amount)
                    return ("check", 0)
            else:
                return ("check", 0)
        else:
            if bluff_this_street and chips > to_call + min_raise:
                raise_amount = max(min_total_bet, int(pot * bet_ratio * overbet_ratio) + to_call)
                raise_amount = min(raise_amount, chips)
                return ("raise", raise_amount)
            raise_amount = max(min_total_bet, int(pot * bet_ratio * overbet_ratio) + to_call)
            raise_amount = min(raise_amount, chips)
            if win_rate > adj_thr_high and chips > to_call + min_raise:
                if r < 0.5 and bet_ratio > 0:
                    if raise_amount >= chips:
                        return ("allin", chips)
                    return ("raise", raise_amount)
                elif r < 0.9:
                    return ("call", to_call)
                else:
                    return ("fold", 0)
            elif win_rate > adj_thr_mid and chips > to_call:
                if r < 0.8:
                    return ("call", to_call)
                else:
                    return ("fold", 0)
            elif chips <= to_call:
                if win_rate > adj_thr_low:
                    return ("allin", chips)
                else:
                    return ("fold", 0)
            else:
                if r < 0.1:
                    return ("call", to_call)
                else:
                    return ("fold", 0)
        return ("fold", 0)

    @staticmethod
    def handle_bot_action(
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
        bot_action_delay=1200,
    ):
        """
        處理目前 current_player 為 bot 時的行動
        回傳 (action, bot_action_pending, bot_action_time, bot_action_result, raise_input_text)
        """
        action = None
        if (
            current_player != 0
            and not showed_result
            and game_stage != GameStage.SHOWDOWN
            and players[current_player].chips > 0
            and (not pending_next_stage or any(p.chips == 0 and player_bets[i] > 0 for i, p in enumerate(players)))
        ):
            now = pygame.time.get_ticks()
            if not bot_action_pending:
                bot_action_time = now
                try:
                    bot_action_result = bots[current_player].act(
                        hands[current_player],
                        community_cards,
                        player_bets,
                        players,
                        min_raise_amount,
                        players[current_player].chips,
                        to_call,
                        game_stage,
                        hands=hands,
                    )
                except Exception as e:
                    bot_action_result = ("call", 0)
                bot_action_pending = True
            elif now - bot_action_time >= bot_action_delay:
                if bot_action_result is not None:
                    bot_action, bot_amount = bot_action_result
                    if bot_action == "fold":
                        action = PlayerAction.FOLD
                    elif bot_action in ("call", "check"):
                        action = PlayerAction.CALL_OR_CHECK
                    elif bot_action in ("bet", "raise", "allin"):
                        if to_call >= players[current_player].chips:
                            action = PlayerAction.CALL_OR_CHECK
                        else:
                            action = PlayerAction.BET_OR_RAISE
                            raise_input_text = str(bot_amount)
                else:
                    action = PlayerAction.CALL_OR_CHECK
                bot_action_pending = False
        else:
            bot_action_pending = False
        return action, bot_action_pending, bot_action_time, bot_action_result, raise_input_text
