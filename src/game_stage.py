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

    def advance_stage(game_stage, deck, community_cards, big_blind_player):
        """
        根據目前階段自動進入下一階段，並處理公牌發牌與 current_player。
        回傳 (新階段, updated_community_cards, 新current_player)
        """
        if game_stage == GameStage.PREFLOP:
            # 發三張公牌
            for _ in range(3):
                community_cards.append(deck.cards.pop(0))
            return GameStage.FLOP, community_cards, big_blind_player
        elif game_stage == GameStage.FLOP:
            community_cards.append(deck.cards.pop(0))
            return GameStage.TURN, community_cards, big_blind_player
        elif game_stage == GameStage.TURN:
            community_cards.append(deck.cards.pop(0))
            return GameStage.RIVER, community_cards, big_blind_player
        elif game_stage == GameStage.RIVER:
            return GameStage.SHOWDOWN, community_cards, big_blind_player
        return game_stage, community_cards, big_blind_player
