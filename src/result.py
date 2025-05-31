from itertools import combinations
from collections import Counter

RANK_ORDER = '23456789TJQKA'
RANK_VALUE = {r: i for i, r in enumerate(RANK_ORDER, 2)}

def hand_rank(hand):
    """傳入5張牌(如['AS','KS','QS','JS','TS'])，回傳(牌型等級, 主要數值, 輔助數值...)"""
    ranks = sorted([card[0] for card in hand], key=lambda r: RANK_VALUE[r], reverse=True)
    suits = [card[1] for card in hand]
    rank_counts = Counter(ranks)
    counts = sorted(rank_counts.values(), reverse=True)
    unique_ranks = sorted(rank_counts, key=lambda r: (rank_counts[r], RANK_VALUE[r]), reverse=True)

    is_flush = len(set(suits)) == 1
    is_straight = False
    high_card = ranks[0]
    # 處理A2345順子
    if ranks == ['A', '5', '4', '3', '2']:
        is_straight = True
        high_card = '5'
    else:
        idxs = [RANK_ORDER.index(r) for r in ranks]
        if all(idxs[i] - 1 == idxs[i+1] for i in range(4)):
            is_straight = True

    # 牌型判斷
    if is_straight and is_flush and high_card == 'A':
        return (10, )  # 皇家同花順
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
        return (4, RANK_VALUE[unique_ranks[0]], [RANK_VALUE[r] for r in unique_ranks[1:]])  # 三條
    if counts == [2, 2, 1]:
        return (3, [RANK_VALUE[r] for r in unique_ranks[:2]], RANK_VALUE[unique_ranks[2]])  # 兩對
    if counts == [2, 1, 1, 1]:
        return (2, RANK_VALUE[unique_ranks[0]], [RANK_VALUE[r] for r in unique_ranks[1:]])  # 一對
    return (1, [RANK_VALUE[r] for r in ranks])  # 散牌

def best_five(hand7):
    """從7張牌中選出最大牌型的5張"""
    return max((hand_rank(list(combo)), combo) for combo in combinations(hand7, 5))[0]

def compare_players(player1, player2, community):
    """比較兩位玩家的最大牌型，回傳 1: 玩家1贏, -1: 玩家2贏, 0: 平手"""
    best1 = best_five(player1 + community)
    best2 = best_five(player2 + community)
    if best1 > best2:
        return 1
    elif best1 < best2:
        return -1
    else:
        return 0