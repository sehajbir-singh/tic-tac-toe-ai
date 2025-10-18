# game_logic.py
"""
Pure game logic for Tic-Tac-Toe.
This module contains only functions that operate on a board list.
Board representation: a list of length 9, indices 0..8 map left-to-right, top-to-bottom.
Empty cell is '' (empty string). Marks are 'X' or 'O'.
"""

from typing import List, Optional, Tuple
import math
import random

# All 8 winning lines expressed as tuples of indices
WIN_LINES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6)              # diagonals
)

def new_board() -> List[str]:
    """Return a fresh empty board (9 empty strings)."""
    return [''] * 9

def copy_board(board: List[str]) -> List[str]:
    """Return a shallow copy of board (useful during simulations)."""
    return board.copy()

def available_moves(board: List[str]) -> List[int]:
    """Return list of indices that are empty."""
    return [i for i, v in enumerate(board) if v == '']

def make_move(board: List[str], index: int, mark: str) -> None:
    """
    Place mark ('X' or 'O') at index on the board.
    NOTE: This mutates the board in place and does not validate the move.
    """
    board[index] = mark

def check_winner(board: List[str], mark: str) -> bool:
    """Return True if mark wins on the provided board."""
    for a, b, c in WIN_LINES:
        if board[a] == mark and board[b] == mark and board[c] == mark:
            return True
    return False

def is_board_full(board: List[str]) -> bool:
    """Return True if there are no empty cells."""
    return all(cell != '' for cell in board)

def game_result(board: List[str]) -> Optional[str]:
    """
    Return 'X' or 'O' if either has won, 'D' for draw, or None if game ongoing.
    Useful for terminal detection.
    """
    if check_winner(board, 'X'):
        return 'X'
    if check_winner(board, 'O'):
        return 'O'
    if is_board_full(board):
        return 'D'
    return None

# ---------- Minimax AI with alpha-beta pruning ----------
def minimax(board: List[str],
            human: str,
            ai: str,
            depth: int,
            maximizing: bool,
            alpha: float,
            beta: float) -> int:
    """
    Minimax evaluation.
    Returns integer score: positive favors AI, negative favors human.
    Depth is used to prefer faster wins and delay losses.
    maximizing True when evaluating moves for AI's turn; False for human.
    """
    # Terminal checks
    if check_winner(board, ai):
        return 10 - depth        # faster win -> higher score
    if check_winner(board, human):
        return depth - 10        # quicker loss -> lower score (more negative)
    if is_board_full(board):
        return 0                 # draw

    if maximizing:
        max_eval = -math.inf
        for i in available_moves(board):
            board[i] = ai
            eval_score = minimax(board, human, ai, depth + 1, False, alpha, beta)
            board[i] = ''
            if eval_score > max_eval:
                max_eval = eval_score
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # beta cut-off
        return int(max_eval)
    else:
        min_eval = math.inf
        for i in available_moves(board):
            board[i] = human
            eval_score = minimax(board, human, ai, depth + 1, True, alpha, beta)
            board[i] = ''
            if eval_score < min_eval:
                min_eval = eval_score
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # alpha cut-off
        return int(min_eval)

def best_move(board: List[str],
              human: str,
              ai: str,
              difficulty: str = 'hard') -> Optional[int]:
    """
    Compute the best move index for ai on board.
    difficulty: 'easy' -> random, 'medium' -> small heuristic (depth-limited), 'hard' -> full minimax.
    Returns None if no moves available.
    """
    moves = available_moves(board)
    if not moves:
        return None

    # EASY: random move
    if difficulty == 'easy':
        return random.choice(moves)

    best_score = -math.inf
    best_moves: List[int] = []

    for mv in moves:
        board[mv] = ai
        if difficulty == 'medium':
            # medium: restrict deeper search by limiting effective depth via a lighter evaluation
            score = minimax(board, human, ai, depth=0, maximizing=False, alpha=-math.inf, beta=math.inf)
        else:
            # hard: full depth minimax
            score = minimax(board, human, ai, depth=0, maximizing=False, alpha=-math.inf, beta=math.inf)
        board[mv] = ''

        if score > best_score:
            best_score = score
            best_moves = [mv]
        elif score == best_score:
            best_moves.append(mv)

    # tie-breaking randomly to make AI less deterministic
    chosen = random.choice(best_moves) if best_moves else random.choice(moves)
    return chosen
