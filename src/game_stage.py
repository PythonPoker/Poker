from enum import Enum, auto


class GameStage(Enum):
    PREFLOP = 0  # 發手牌後，還沒翻牌
    FLOP = 1  # 翻牌
    TURN = 2  # 轉牌
    RIVER = 3  # 河牌
    SHOWDOWN = 4  # 攤牌結算
