class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.value = None

    def mark(self, symbol):
        if not self.is_empty():
            return False
        self.value = symbol
        return True

    def is_empty(self):
        return self.value is None

    def reset(self):
        self.value = None