from itertools import combinations
from collections import Counter
import pygame

RANK_ORDER = "23456789TJQKA"
RANK_VALUE = {r: i for i, r in enumerate(RANK_ORDER, 2)}

HAND_TYPE_NAME = {
    10: "Royal Flush",
    9: "Straight Flush",
    8: "Quads",
    7: "Full House",
    6: "Flush",
    5: "Straight",
    4: "Three of a Kind",
    3: "Two Pair",
    2: "One Pair",
    1: "High Card",
}


class PokerResult:

    def hand_rank(hand):
        """傳入5張牌(如['AS','KS','QS','JS','TS'])，回傳(牌型等級, 主要數值, 輔助數值...)"""
        ranks = sorted(
            [card[0] for card in hand], key=lambda r: RANK_VALUE[r], reverse=True
        )
        suits = [card[1] for card in hand]
        rank_counts = Counter(ranks)
        counts = sorted(rank_counts.values(), reverse=True)
        unique_ranks = sorted(
            rank_counts, key=lambda r: (rank_counts[r], RANK_VALUE[r]), reverse=True
        )

        is_flush = len(set(suits)) == 1
        is_straight = False
        high_card = ranks[0]

        # 處理A2345順子
        if ranks == ["A", "5", "4", "3", "2"]:
            is_straight = True
            high_card = "5"
        else:
            idxs = [RANK_ORDER.index(r) for r in ranks]
            if all(idxs[i] - 1 == idxs[i + 1] for i in range(4)):
                is_straight = True

        # 牌型判斷
        if is_straight and is_flush and high_card == "A":
            return (10,)  # 皇家同花順
        if is_straight and is_flush:
            return (9, RANK_VALUE[high_card])  # 同花順
        if counts == [4, 1]:
            return (8, RANK_VALUE[unique_ranks[0]], RANK_VALUE[unique_ranks[1]])  # 四條
        if counts == [3, 2]:
            return (7, RANK_VALUE[unique_ranks[0]], RANK_VALUE[unique_ranks[1]])  # 葫蘆
        if is_flush:
            return (6, [RANK_VALUE[r] for r in ranks])  # 同花
        if is_straight:
            return (5, RANK_VALUE[high_card])  # 順子
        if counts == [3, 1, 1]:
            return (
                4,
                RANK_VALUE[unique_ranks[0]],
                [RANK_VALUE[r] for r in unique_ranks[1:]],
            )  # 三條
        if counts == [2, 2, 1]:
            return (
                3,
                [RANK_VALUE[r] for r in unique_ranks[:2]],
                RANK_VALUE[unique_ranks[2]],
            )  # 兩對
        if counts == [2, 1, 1, 1]:
            return (
                2,
                RANK_VALUE[unique_ranks[0]],
                [RANK_VALUE[r] for r in unique_ranks[1:]],
            )  # 一對
        return (1, [RANK_VALUE[r] for r in ranks])  # 高牌

    @staticmethod
    def best_five(hand7):
        """從7張牌中選出最大牌型的5張"""
        if not hand7 or len(hand7) < 5:
            return []
        return max(
            (PokerResult.hand_rank(list(combo)), combo)
            for combo in combinations(hand7, 5)
        )[0]

    @staticmethod
    def compare_players(player1, player2, community):
        """比較兩位玩家的最大牌型，回傳 1: 玩家1贏, -1: 玩家2贏, 0: 平手"""
        best1 = PokerResult.best_five(player1 + community)
        best2 = PokerResult.best_five(player2 + community)
        if best1 > best2:
            return 1
        elif best1 < best2:
            return -1
        else:
            return 0

    @staticmethod
    def compare_all_players(hands, community):
        """
        比較多位玩家的最大牌型，回傳所有最大牌型玩家的 index list（支援平手）
        """
        best_ranks = []
        for hand in hands:
            if hand:  # 避免已棄牌玩家
                best_ranks.append(PokerResult.best_five(hand + community))
            else:
                best_ranks.append(None)
        max_rank = max([r for r in best_ranks if r is not None])
        winners = [i for i, r in enumerate(best_ranks) if r == max_rank]
        return winners, max_rank

    def get_hand_type_name(rank_tuple):
        return HAND_TYPE_NAME.get(rank_tuple[0], "未知")

    @staticmethod
    def showdown_result(
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
    ):
        now = pygame.time.get_ticks()
        # 先公開手牌
        if not showed_hands:
            showdown_time = now
            showed_hands = True
            pot_given = False
            pot_give_time = None
        elif showed_hands and not showed_result:
            # 如果 winner_text 已經有內容（如棄牌），直接顯示
            if winner_text:
                showed_result = True
                result_time = now
            # 否則等3秒後自動判斷勝負
            elif (
                showdown_time
                and now - showdown_time > 3000
                and len(community_cards) >= 3
            ):
                # 只比未棄牌玩家
                active_hands = [hand if not getattr(players[i], "is_folded", False) else [] for i, hand in enumerate(hands)]
                winners, max_rank = PokerResult.compare_all_players(active_hands, community_cards)
                # 只顯示未棄牌且獲勝的玩家
                if len(winners) == 1:
                    winner_text = f"P{winners[0]+1} WINS"
                else:
                    winner_text = " & ".join([f"P{i+1}" for i in winners]) + " WIN"
                showed_result = True
                result_time = now

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
            # 2秒後加pot到勝者，只加一次
            if not pot_given and result_time and now - result_time > 2000:
                # 重新比一次，確保只分給未棄牌且真正勝出的玩家
                active_hands = [hand if not getattr(players[i], "is_folded", False) else [] for i, hand in enumerate(hands)]
                winners, max_rank = PokerResult.compare_all_players(active_hands, community_cards)
                if winners:
                    share = pot // len(winners)
                    for i in winners:
                        players[i].chips += share
                    pot = 0
                pot_given = True
                pot_give_time = now

        return (
            showed_hands,
            showed_result,
            showdown_time,
            winner_text,
            result_time,
            pot_given,
            pot_give_time,
            pot,
        )
