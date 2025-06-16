import random
import numpy as np
import pygame
from game_stage import GameStage
from card import Deck
from result import PokerResult
from action import PlayerAction


class PokerBot:
    def __init__(self, player_index):
        self.player_index = player_index

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
                "CO":   (0.70, 0.56, 0.41),
                "BTN":  (0.68, 0.54, 0.39),
                "SB":   (0.70, 0.55, 0.40),
                "BB":   (0.68, 0.53, 0.38),
            }
        else:
            # 翻牌後可略降門檻
            thresholds = {
                "UTG":  (0.70, 0.55, 0.40),
                "MP":   (0.68, 0.53, 0.38),
                "CO":   (0.66, 0.51, 0.36),
                "BTN":  (0.64, 0.49, 0.34),
                "SB":   (0.66, 0.51, 0.36),
                "BB":   (0.64, 0.49, 0.34),
            }
        # 預設
        return thresholds.get(position, (0.7, 0.55, 0.4))

    def estimate_win_rate(self, hand, community_cards, hands, players, num_simulations=10000):
        """
        蒙地卡羅模擬，估算bot在目前情境下的勝率（支援多玩家）
        """
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
    ):
        chips = players[self.player_index].chips
        num_players = len(players)
        win_rate = self.estimate_win_rate(
            hand, community_cards, hands, players, num_simulations=200
        )

        position = self.get_position(self.player_index, dealer_index, num_players)
        thr_high, thr_mid, thr_low = self.get_gto_thresholds(position, game_stage)

        r = np.random.rand()
        max_bet = max(player_bets)
        min_total_bet = max_bet + min_raise if max_bet > 0 else min_raise

        if to_call == 0:
            if win_rate > thr_high:
                if r < 0.7 and chips > min_total_bet:
                    bet_amount = min(min_total_bet, chips)
                    if bet_amount >= chips:
                        return ("allin", chips)
                    return ("bet", bet_amount)
                else:
                    return ("check", 0)
            elif win_rate > thr_mid:
                if r < 0.8:
                    return ("check", 0)
                else:
                    return ("bet", min(min_total_bet, chips))
            else:
                return ("check", 0)
        else:
            if win_rate > thr_high and chips > to_call + min_raise:
                if r < 0.6:
                    raise_amount = min(max_bet + min_raise, chips)
                    if raise_amount >= chips:
                        return ("allin", chips)
                    return ("raise", raise_amount)
                else:
                    return ("call", to_call)
            elif win_rate > thr_mid and chips > to_call:
                if r < 0.7:
                    return ("call", to_call)
                else:
                    return ("fold", 0)
            elif chips <= to_call:
                if win_rate > thr_low:
                    return ("allin", chips)
                else:
                    return ("fold", 0)
            else:
                if r < 0.2:
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
