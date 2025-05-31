import random

# 定義一副牌
suits = ['S', 'H', 'D', 'C']  # 黑桃、紅心、方塊、梅花
ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

def create_deck():
    """建立一副52張牌"""
    return [rank + suit for suit in suits for rank in ranks]

def shuffle_deck(deck):
    """洗牌"""
    random.shuffle(deck)
    return deck
def deal_cards(deck, num_players=2, cards_per_player=2):
    """發牌給玩家，回傳一個列表，每個元素是玩家的手牌"""
    hands = []
    for _ in range(num_players):
        hand = []
        for _ in range(cards_per_player):
            hand.append(deck.pop(0))  # 從牌堆頂端發牌
        hands.append(hand)
    return hands

# 範例用法
if __name__ == "__main__":
    deck = create_deck()
    shuffle_deck(deck)
    print("洗牌後：", deck)
    hands = deal_cards(deck, num_players=2, cards_per_player=2)
    print("玩家手牌：", hands)
    print("剩餘牌堆：", deck)