import random
from player import Player
from card import Deck
from chips import Chips
from game_stage import GameStage
from bot import PokerBot
from action import PlayerAction


class GameFlow:
    @staticmethod
    def init_game(game_setting):
        deck = Deck()
        deck.shuffle()
        hands = deck.deal_player_hands(num_players=2, cards_per_player=2)
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

        player_bets = [0, 0]
        waiting_for_action = False
        actions_this_round = 0
        last_actions = ["", ""]

        pot = 0

        players = [Player(0), Player(1)]
        bot = PokerBot(1)
        big_blind_player = random.randint(0, 1)
        current_player = 1 - big_blind_player
        players[big_blind_player].set_big_blind(True)
        players[1 - big_blind_player].set_big_blind(False)
        acted_this_round = [False, False]

        bet = 0
        big_blind_amount = 10
        last_raise_amount = big_blind_amount

        if players[big_blind_player].chips >= big_blind_amount:
            players[big_blind_player].chips -= big_blind_amount
            player_bets[big_blind_player] = big_blind_amount
            bet = big_blind_amount

        player_positions = [
            (
                game_setting["WIDTH"] // 2 - (len(hands[0]) * 80) // 2,
                game_setting["HEIGHT"] - game_setting["CARD_HEIGHT"] - 40,
            ),
            (game_setting["WIDTH"] // 2 - (len(hands[1]) * 80) // 2, 40),
        ]

        bot_action_pending = False
        bot_action_time = 0
        bot_action_result = None

        return {
            "deck": deck,
            "hands": hands,
            "card_images": card_images,
            "showed_hands": showed_hands,
            "showed_result": showed_result,
            "showdown_time": showdown_time,
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
            "bot": bot,
            "big_blind_player": big_blind_player,
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
