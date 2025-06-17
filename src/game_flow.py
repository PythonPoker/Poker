import random
from player import Player
from card import Deck
from chips import Chips
from game_stage import GameStage
from bot import PokerBot
from action import PlayerAction

NUM_PLAYERS = 6


class GameFlow:
    @staticmethod
    def init_game(game_setting):
        deck = Deck()
        deck.shuffle()
        hands = deck.deal_player_hands(num_players=NUM_PLAYERS, cards_per_player=2)
        card_images = deck.load_card_images()
        showed_hands = False
        showed_result = False
        showdown_time = None
        handle_raise_input = PlayerAction.handle_raise_input
        raise_input_text = ""
        raise_input_active = False

        pot_given = False
        pot_give_time = None

        game_stage = GameStage.PREFLOP
        next_stage_time = None
        pending_next_stage = False

        community_cards = []
        deal_index = 0
        winner_text = ""
        result_time = None

        player_bets = [0 for _ in range(NUM_PLAYERS)]
        waiting_for_action = False
        actions_this_round = 0
        last_actions = ["" for _ in range(NUM_PLAYERS)]

        pot = 0

        players = [Player(i) for i in range(NUM_PLAYERS)]
        bots = [None] + [PokerBot(i) for i in range(1, NUM_PLAYERS)]  # 玩家1真人，其餘為bot

        # 隨機選一位玩家作為小盲
        small_blind_player = random.randint(0, NUM_PLAYERS - 1)
        big_blind_player = (small_blind_player + 1) % NUM_PLAYERS
        for i, player in enumerate(players):
            player.set_big_blind(i == big_blind_player)

        # Preflop 第一位行動玩家為大盲左手邊一位
        current_player = (big_blind_player + 1) % NUM_PLAYERS  # 大盲左手邊第二位先行

        acted_this_round = [False for _ in range(NUM_PLAYERS)]

        bet = 0
        big_blind_amount = 10
        last_raise_amount = big_blind_amount

        # 扣除大盲、小盲籌碼
        if players[big_blind_player].chips >= big_blind_amount:
            players[big_blind_player].chips -= big_blind_amount
            player_bets[big_blind_player] = big_blind_amount
            bet = big_blind_amount
        small_blind_amount = big_blind_amount // 2
        if players[small_blind_player].chips >= small_blind_amount:
            players[small_blind_player].chips -= small_blind_amount
            player_bets[small_blind_player] = small_blind_amount

        W, H = game_setting["WIDTH"], game_setting["HEIGHT"]
        player_positions = [
            (W // 2 - 80, H - 170),      # 玩家1（中下，真人）
            (150, H - 250),              # 玩家2（左下）
            (100, H // 3),               # 玩家3（左中）
            (300 , 40),                  # 玩家4（左上）
            (W - 480, 40),              # 玩家5（右上）
            (W - 300, H // 3),           # 玩家6（右中）
        ]

        bot_action_pending = False
        bot_action_time = 0
        bot_action_result = None
        dealer_index = (big_blind_player - 2) % NUM_PLAYERS

        return {
            "deck": deck,
            "hands": hands,
            "card_images": card_images,
            "showed_hands": showed_hands,
            "showed_result": showed_result,
            "showdown_time": showdown_time,
            "dealer_index": dealer_index,
            "handle_raise_input": handle_raise_input,
            "raise_input_text": raise_input_text,
            "raise_input_active": raise_input_active,
            "pot_given": pot_given,
            "pot_give_time": pot_give_time,
            "game_stage": game_stage,
            "next_stage_time": next_stage_time,
            "pending_next_stage": pending_next_stage,
            "community_cards": community_cards,
            "deal_index": deal_index,
            "winner_text": winner_text,
            "result_time": result_time,
            "player_bets": player_bets,
            "waiting_for_action": waiting_for_action,
            "actions_this_round": actions_this_round,
            "last_actions": last_actions,
            "pot": pot,
            "players": players,
            "bots": bots,
            "big_blind_player": big_blind_player,
            "small_blind_player": small_blind_player,
            "current_player": current_player,
            "acted_this_round": acted_this_round,
            "bet": bet,
            "big_blind_amount": big_blind_amount,
            "last_raise_amount": last_raise_amount,
            "player_positions": player_positions,
            "bot_action_pending": bot_action_pending,
            "bot_action_time": bot_action_time,
            "bot_action_result": bot_action_result,
        }

    @staticmethod
    def reset_game(deck, players, Chips, big_blind_player, big_blind_amount, bots):
        deck = Deck()
        deck.shuffle()
        hands = deck.deal_player_hands(num_players=NUM_PLAYERS, cards_per_player=2)
        community_cards = []
        deal_index = 0
        game_stage = GameStage.PREFLOP
        showed_result = False
        showed_hands = False
        winner_text = ""
        result_time = None
        showdown_time = None
        pot_given = False
        pot_give_time = None

        for player in players:
            player.is_folded = False

        # 輪替小盲與大盲：都往下移動一位
        small_blind_player = (big_blind_player) % NUM_PLAYERS
        big_blind_player = (big_blind_player + 1) % NUM_PLAYERS
        for i, player in enumerate(players):
            player.set_big_blind(i == big_blind_player)

        # Preflop 第一位行動玩家為大盲左手邊一位
        current_player = (big_blind_player + 1) % NUM_PLAYERS

        big_blind_amount = 10
        player_bets = [0 for _ in range(NUM_PLAYERS)]
        acted_this_round = [False for _ in range(NUM_PLAYERS)]
        bet = 0
        for player in players:
            if player.chips == 0:
                player.chips = Chips.chips
        # 扣除大盲、小盲籌碼
        if players[big_blind_player].chips >= big_blind_amount:
            players[big_blind_player].chips -= big_blind_amount
            player_bets[big_blind_player] = big_blind_amount
            bet = big_blind_amount
        small_blind_amount = big_blind_amount // 2
        if players[small_blind_player].chips >= small_blind_amount:
            players[small_blind_player].chips -= small_blind_amount
            player_bets[small_blind_player] = small_blind_amount

        last_raise_amount = big_blind_amount
        last_actions = ["" for _ in range(NUM_PLAYERS)]
        bot_action_pending = False  # 新增
        # 重設所有 bot 的 bluff 狀態
        for bot in bots:
            if bot is not None:
                bot.is_bluffing = False
                bot.last_bluff_street = None
        dealer_index = (big_blind_player - 2) % NUM_PLAYERS
        return (
            deck,
            hands,
            community_cards,
            deal_index,
            game_stage,
            showed_result,
            showed_hands,
            winner_text,
            result_time,
            showdown_time,
            pot_given,
            pot_give_time,
            big_blind_player,
            big_blind_amount,
            player_bets,
            acted_this_round,
            bet,
            current_player,
            last_raise_amount,
            last_actions,
            bot_action_pending,
            dealer_index,
        )
