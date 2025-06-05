from action import PlayerAction
import pygame


class Chips:
    chips = 1000

    def __init__(self, player, chips):
        self.player = player
        self.chips = chips

    def add(self, value):
        self.chips += value

    def subtract(self, value):
        self.chips -= value

    def get_amount(self):
        return self.chips

    def get_min_raise_amount(game_stage, big_blind_amount, last_raise_amount):
        # PREFLOP 時最小加注為大盲，其餘為上一輪加注額
        stage = game_stage.name if hasattr(game_stage, "name") else str(game_stage)
        if stage == "PREFLOP":
            return big_blind_amount
        else:
            return last_raise_amount

    def get_min_total_bet(max_bet, min_raise_amount):
        # 若有下注，最小總下注為最大下注+最小加注，否則為最小加注
        return max_bet + min_raise_amount if max_bet > 0 else min_raise_amount
