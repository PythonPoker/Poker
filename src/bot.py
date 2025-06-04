import random


class PokerBot:
    def __init__(self, player_index):
        self.player_index = player_index

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
    ):
        """
        決定bot行動
        hand: bot手牌
        community_cards: 公牌
        player_bets: 當前每位玩家本輪下注額
        players: 玩家物件列表
        min_raise: 最小加注額
        max_raise: 最大加注額
        to_call: 跟注所需金額
        game_stage: 當前遊戲階段
        回傳: "fold", "call", "check", "bet", "raise", "allin"
        """
        # 簡單策略：有錢就call，偶爾raise，沒錢就fold
        chips = players[self.player_index].chips

        # 如果可以check就check
        if to_call == 0:
            if random.random() < 0.7:
                return ("check", 0)
            else:
                # 偶爾主動下注
                bet_amount = min_raise
                if bet_amount >= chips:
                    return ("allin", chips)
                return ("bet", bet_amount)
        else:
            # 有50%機率跟注
            if chips > to_call and random.random() < 0.7:
                return ("call", to_call)
            elif chips > min_raise and random.random() < 0.2:
                # 偶爾加注
                raise_amount = min(max(min_raise, to_call + min_raise), chips)
                if raise_amount >= chips:
                    return ("allin", chips)
                return ("raise", raise_amount)
            elif chips <= to_call:
                return ("allin", chips)
            else:
                return ("fold", 0)
