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
