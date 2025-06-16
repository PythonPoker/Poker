```python
NUM_PLAYERS = 6  # 6人局

# 初始化玩家
players = [Player(f"Player {i+1}", Chips.chips) for i in range(NUM_PLAYERS)]
# 只讓第2~6位是bot
bots = [None] + [PokerBot() for _ in range(1, NUM_PLAYERS)]

# 玩家座位（你可以根據畫面調整座標）
player_positions = [
    (100, 500),   # 玩家1（真人）
    (600, 100),   # 玩家2
    (1000, 200),  # 玩家3
    (1100, 500),  # 玩家4
    (800, 700),   # 玩家5
    (300, 700),   # 玩家6
]

# 其他與玩家數量有關的初始化
hands = [[] for _ in range(NUM_PLAYERS)]
player_bets = [0 for _ in range(NUM_PLAYERS)]
last_actions = ["" for _ in range(NUM_PLAYERS)]
acted_this_round = [False for _ in range(NUM_PLAYERS)]

# 主要遊戲流程中的for迴圈都要改成range(NUM_PLAYERS)
for i in range(NUM_PLAYERS):
    # ...顯示手牌、籌碼、行動等...

# Bot行動邏輯也要改成多bot
for idx in range(1, NUM_PLAYERS):
    if (
        current_player == idx
        and not showed_result
        and game_stage != GameStage.SHOWDOWN
        and players[idx].chips > 0
        and (not pending_next_stage or any_allin)
        and not (players[0].chips == 0 and players[idx].chips == 0)
    ):
        # ...bot邏輯...
        bot = bots[idx]
        # ...呼叫bot.act()...
```