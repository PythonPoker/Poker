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
            # 等3秒後顯示勝負
            if (
                showdown_time
                and now - showdown_time > 3000
                and len(hands[0]) > 0
                and len(hands[1]) > 0
                and len(community_cards) >= 3
            ):
                result = PokerResult.compare_players(
                    hands[0], hands[1], community_cards
                )
                if result == 1:
                    winner_text = "P1 WINS"
                elif result == -1:
                    winner_text = "P2 WINS"
                else:
                    winner_text = "DRAW"
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
                if winner_text == "P1 WINS":
                    players[0].chips += pot
                elif winner_text == "P2 WINS":
                    players[1].chips += pot
                elif winner_text == "DRAW":
                    players[0].chips += pot // 2
                    players[1].chips += pot // 2
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
