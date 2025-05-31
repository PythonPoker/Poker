class Chips:
    def __init__(self, player, amount=1000):
        self.player = player
        self.amount = amount

    def add(self, value):
        self.amount += value

    def subtract(self, value):
        self.amount -= value

    def get_amount(self):
        return self.amount