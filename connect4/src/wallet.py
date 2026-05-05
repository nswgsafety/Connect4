class Wallet:
    STARTING = 500

    def __init__(self):
        self.balance = self.STARTING

    def can_bet(self, amount):
        return amount <= self.balance

    def place_bet(self, amount):
        if not self.can_bet(amount):
            return False
        self.balance -= amount
        return True

    def payout(self, amount):
        self.balance += amount

    def is_broke(self):
        return self.balance <= 0

    def reset(self):
        self.balance = self.STARTING