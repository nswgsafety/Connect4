from src.board import Board
from src.player import Player


class Game:
    DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]

    def __init__(self):
        self.board = Board()
        self.players = [
            Player("Player 1", "X", "red"),
            Player("Player 2", "O", "yellow"),
        ]
        self.current_index = 0
        self.state = "playing"
        self.win_cells = []

    @property
    def current(self):
        return self.players[self.current_index]

    def move(self, col):
        if self.state != "playing":
            return False
        if self.board.is_column_full(col):
            return False

        row = self.board.drop(col, self.current.symbol)

        win = self.check_win(row, col)
        if win:
            self.state = "won"
            self.win_cells = win
            self.current.win()
            return True

        if self.board.is_full():
            self.state = "draw"
            return True

        self.switch_player()
        return True

    def check_win(self, row, col):
        symbol = self.current.symbol
        for dr, dc in self.DIRECTIONS:
            line = self._collect_line(row, col, dr, dc, symbol)
            if len(line) >= Board.WIN_LENGTH:
                return line
        return None

    def _collect_line(self, row, col, dr, dc, symbol):
        cells = [(row, col)]
        for direction in [1, -1]:
            r, c = row + dr * direction, col + dc * direction
            while (
                0 <= r < Board.ROWS
                and 0 <= c < Board.COLS
                and self.board.get_cell(r, c).value == symbol
            ):
                cells.append((r, c))
                r += dr * direction
                c += dc * direction
        return cells

    def switch_player(self):
        self.current_index = 1 if self.current_index == 0 else 0

    def reset(self):
        self.board.reset()
        self.state = "playing"
        self.win_cells = []
        self.current_index = 0