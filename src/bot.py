import random
import pygame
from game_stage import GameStage
from card import Deck
from result import PokerResult
from action import PlayerAction


class PokerBot:
    def __init__(self, player_index):
        self.player_index = player_index

    def estimate_win_rate(self, hand, community_cards, hands, num_simulations=300):
        """
        蒙地卡羅模擬，估算bot在目前情境下的勝率（支援多玩家）
        """
        wins = 0
        draws = 0
        total = 0

        # 找出已知牌（自己的手牌、所有已知手牌、已知公牌）
        used_cards = set(community_cards + hand)
        for i, h in enumerate(hands):
            if i != self.player_index and h:
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
                elif hands[i]:  # 對手未棄牌
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
        hands=None,  # 新增 hands 參數
    ):
        """
        決定bot行動（蒙地卡羅模擬勝率）
        """
        chips = players[self.player_index].chips

        # 蒙地卡羅估算勝率
        win_rate = self.estimate_win_rate(
            hand, community_cards, hands, num_simulations=200
        )

        # 決策邏輯（可依需求調整閾值）
        if to_call == 0:
            if win_rate > 0.7 and chips > min_raise:
                # 強牌主動下注
                bet_amount = min(min_raise * 2, chips)
                if bet_amount >= chips:
                    return ("allin", chips)
                return ("bet", bet_amount)
            elif win_rate > 0.4:
                return ("check", 0)
            else:
                return ("check", 0)
        else:
            if win_rate > 0.8 and chips > to_call + min_raise:
                # 超強牌加注
                raise_amount = min(to_call + min_raise * 2, chips)
                if raise_amount >= chips:
                    return ("allin", chips)
                return ("raise", raise_amount)
            elif win_rate > 0.5 and chips > to_call:
                return ("call", to_call)
            elif chips <= to_call:
                # 只剩下allin選擇時，根據勝率決定要不要call allin
                if win_rate > 0.4:
                    return ("allin", chips)
                else:
                    return ("fold", 0)
        # fallback: 若沒命中任何條件，預設棄牌
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
