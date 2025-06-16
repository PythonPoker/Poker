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
        """
        根據目前階段自動進入下一階段，並處理公牌發牌與 current_player。
        回傳 (新階段, updated_community_cards, 新current_player)
        players: 傳入玩家列表以跳過已棄牌或all-in玩家
        """
        NUM_PLAYERS = len(players) if players else 6

        def find_next_active_player(start_idx):
            for offset in range(NUM_PLAYERS):
                idx = (start_idx + offset) % NUM_PLAYERS
                if players is None or (players[idx].chips > 0):
                    return idx
            return start_idx

        # 小盲玩家
        small_blind_player = (big_blind_player + 1) % NUM_PLAYERS

        if game_stage == GameStage.PREFLOP:
            # 發三張公牌
            for _ in range(3):
                community_cards.append(deck.cards.pop(0))
            # 翻牌後由小盲開始
            next_player = find_next_active_player(small_blind_player)
            return GameStage.FLOP, community_cards, next_player
        elif game_stage == GameStage.FLOP:
            community_cards.append(deck.cards.pop(0))
            next_player = find_next_active_player(small_blind_player)
            return GameStage.TURN, community_cards, next_player
        elif game_stage == GameStage.TURN:
            community_cards.append(deck.cards.pop(0))
            next_player = find_next_active_player(small_blind_player)
            return GameStage.RIVER, community_cards, next_player
        elif game_stage == GameStage.RIVER:
            return GameStage.SHOWDOWN, community_cards, big_blind_player
        return game_stage, community_cards, big_blind_player
