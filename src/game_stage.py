from enum import Enum, auto


class GameStage(Enum):
    PREFLOP = auto()
    FLOP = auto()
    TURN = auto()
    RIVER = auto()
    SHOWDOWN = auto()

    @staticmethod
    def next_stage(game_stage):
        if game_stage == GameStage.PREFLOP:
            return GameStage.FLOP
        elif game_stage == GameStage.FLOP:
            return GameStage.TURN
        elif game_stage == GameStage.TURN:
            return GameStage.RIVER
        elif game_stage == GameStage.RIVER:
            return GameStage.SHOWDOWN
        return None

    @staticmethod
    def advance_stage(game_stage, deck, community_cards, big_blind_player, players=None):
        NUM_PLAYERS = len(players) if players else 6

        def find_next_active_player(start_idx):
            # 從start_idx開始，依序找未棄牌且有籌碼的玩家
            for offset in range(NUM_PLAYERS):
                idx = (start_idx + offset) % NUM_PLAYERS
                if players is None:
                    return idx
                if players[idx].chips > 0 and not getattr(players[idx], "is_folded", False):
                    return idx
            return start_idx

        # 小盲玩家
        small_blind_player = (big_blind_player - 1) % NUM_PLAYERS

        if game_stage == GameStage.PREFLOP:
            acted_this_round = [False] * len(players)
            # 發三張公牌
            for _ in range(3):
                community_cards.append(deck.cards.pop(0))
            # 翻牌後由小盲開始，依序找未棄牌玩家
            next_player = find_next_active_player(small_blind_player)
            return GameStage.FLOP, community_cards, next_player
        elif game_stage == GameStage.FLOP:
            acted_this_round = [False] * len(players)
            community_cards.append(deck.cards.pop(0))
            next_player = find_next_active_player(small_blind_player)
            return GameStage.TURN, community_cards, next_player
        elif game_stage == GameStage.TURN:
            acted_this_round = [False] * len(players)
            community_cards.append(deck.cards.pop(0))
            next_player = find_next_active_player(small_blind_player)
            return GameStage.RIVER, community_cards, next_player
        elif game_stage == GameStage.RIVER:
            return GameStage.SHOWDOWN, community_cards, big_blind_player
        return game_stage, community_cards, big_blind_player
