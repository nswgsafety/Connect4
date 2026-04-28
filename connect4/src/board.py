from src.cell import Cell


class Board:
    ROWS = 6
    COLS = 7
    WIN_LENGTH = 4

    def __init__(self):
        self.grid = [
            [Cell(r, c) for c in range(self.COLS)]
            for r in range(self.ROWS)
        ]

    def get_cell(self, row, col):
        return self.grid[row][col]

    def drop(self, col, symbol):
        for row in range(self.ROWS - 1, -1, -1):
            cell = self.grid[row][col]
            if cell.is_empty():
                cell.mark(symbol)
                return row
        return None

    def is_column_full(self, col):
        return not self.grid[0][col].is_empty()

    def is_full(self):
        return all(not self.grid[0][c].is_empty() for c in range(self.COLS))

    def reset(self):
        for row in self.grid:
            for cell in row:
                cell.reset()