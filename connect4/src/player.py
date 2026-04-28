class Player:
    def __init__(self, name, symbol, color):
        self.name = name
        self.symbol = symbol
        self.color = color
        self.score = 0

    def win(self):
        self.score += 1