import math
import random
import copy
from src.board import Board


class AI:
    DEPTH = 5

    def __init__(self, symbol, opponent_symbol):
        self.symbol = symbol
        self.opponent_symbol = opponent_symbol

    def get_move(self, board):
        # Convert the Board object into a plain 2D list for simulation
        grid = [
            [board.get_cell(r, c).value for c in range(Board.COLS)]
            for r in range(Board.ROWS)
        ]
        col, _ = self._minimax(grid, self.DEPTH, -math.inf, math.inf, True)
        return col

    # --- Grid helpers (work on plain 2D lists, not Board objects) ---

    def _drop(self, grid, col, symbol):
        for row in range(Board.ROWS - 1, -1, -1):
            if grid[row][col] is None:
                grid[row][col] = symbol
                return row
        return None

    def _col_full(self, grid, col):
        return grid[0][col] is not None

    def _board_full(self, grid):
        return all(grid[0][c] is not None for c in range(Board.COLS))

    def _check_win(self, grid, row, col, symbol):
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            count = 1
            for d in (1, -1):
                r, c = row + dr * d, col + dc * d
                while (
                    0 <= r < Board.ROWS
                    and 0 <= c < Board.COLS
                    and grid[r][c] == symbol
                ):
                    count += 1
                    r += dr * d
                    c += dc * d
            if count >= Board.WIN_LENGTH:
                return True
        return False

    # --- Scoring ---

    def _score_window(self, window):
        sym = self.symbol
        opp = self.opponent_symbol
        s = window.count(sym)
        e = window.count(None)
        o = window.count(opp)
        score = 0
        if s == 4:
            score += 100
        elif s == 3 and e == 1:
            score += 5
        elif s == 2 and e == 2:
            score += 2
        if o == 3 and e == 1:
            score -= 4
        return score

    def _score_board(self, grid):
        score = 0
        sym = self.symbol
        center = Board.COLS // 2

        # Prefer center column
        score += [grid[r][center] for r in range(Board.ROWS)].count(sym) * 3

        # Horizontal
        for r in range(Board.ROWS):
            for c in range(Board.COLS - 3):
                score += self._score_window([grid[r][c + i] for i in range(4)])

        # Vertical
        for c in range(Board.COLS):
            for r in range(Board.ROWS - 3):
                score += self._score_window([grid[r + i][c] for i in range(4)])

        # Diagonal down-right
        for r in range(Board.ROWS - 3):
            for c in range(Board.COLS - 3):
                score += self._score_window([grid[r + i][c + i] for i in range(4)])

        # Diagonal down-left
        for r in range(Board.ROWS - 3):
            for c in range(3, Board.COLS):
                score += self._score_window([grid[r + i][c - i] for i in range(4)])

        return score

    # --- Minimax with alpha-beta pruning ---

    def _minimax(self, grid, depth, alpha, beta, maximizing):
        valid = [c for c in range(Board.COLS) if not self._col_full(grid, c)]

        if not valid or self._board_full(grid) or depth == 0:
            return None, self._score_board(grid)

        best_col = random.choice(valid)

        if maximizing:
            best_score = -math.inf
            for col in valid:
                g = copy.deepcopy(grid)
                row = self._drop(g, col, self.symbol)
                if self._check_win(g, row, col, self.symbol):
                    return col, 100000 + depth
                _, score = self._minimax(g, depth - 1, alpha, beta, False)
                if score > best_score:
                    best_score, best_col = score, col
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            return best_col, best_score
        else:
            best_score = math.inf
            for col in valid:
                g = copy.deepcopy(grid)
                row = self._drop(g, col, self.opponent_symbol)
                if self._check_win(g, row, col, self.opponent_symbol):
                    return col, -(100000 + depth)
                _, score = self._minimax(g, depth - 1, alpha, beta, True)
                if score < best_score:
                    best_score, best_col = score, col
                beta = min(beta, score)
                if alpha >= beta:
                    break
            return best_col, best_score