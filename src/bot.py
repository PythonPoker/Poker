import random
from card import Deck
from result import PokerResult

class PokerBot:
    def __init__(self, player_index):
        self.player_index = player_index

    def estimate_win_rate(self, hand, community_cards, hands, num_simulations=500):
        """
        蒙地卡羅模擬，估算bot在目前情境下的勝率
        """
        wins = 0
        draws = 0
        total = 0
        # 找出未出現的牌
        used_cards = set(community_cards + hand + hands[1 - self.player_index])
        deck = Deck()
        deck.cards = [c for c in deck.cards if c not in used_cards]

        for _ in range(num_simulations):
            sim_deck = deck.cards[:]
            random.shuffle(sim_deck)
            opp_hand = sim_deck[:2]
            sim_deck = sim_deck[2:]
            sim_community = community_cards[:]
            while len(sim_community) < 5:
                sim_community.append(sim_deck.pop())
            cmp = PokerResult.compare_players(hand, opp_hand, sim_community)
            if cmp == 1:
                wins += 1
            elif cmp == 0:
                draws += 1
            total += 1
        return (wins + draws * 0.5) / total if total > 0 else 0.0

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
        win_rate = self.estimate_win_rate(hand, community_cards, hands, num_simulations=300)

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
                return ("allin", chips)
            else:
                return ("fold", 0)