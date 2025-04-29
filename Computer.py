import math
from Board import Board
from ChessPiece import *
from functools import wraps
from Logger import Logger, BoardRepr
import random


logger = Logger()


class MinimaxResult:
    def __init__(self):
        self.moves = []
        self.score = -math.inf

    def update(self, piece, move, score):
        if score > self.score:
            self.score = score
            self.moves = [[piece, move, score]]
        elif score == self.score:
            self.moves.append([piece, move, score])
            
def log_tree(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        board: Board = args[0]
        if board.log:
            depth = args[1]
            write_to_file(board, depth)
        return func(*args, **kwargs)
    return wrapper


def write_to_file(board: Board, current_depth):
    global logger
    if board.depth == current_depth:
        logger.clear()
    board_repr = BoardRepr(board.unicode_array_repr(), current_depth, board.evaluate())
    logger.append(board_repr)


@log_tree
def minimax(board, depth, alpha, beta, max_player, save_move, result=None, ai_color=None):
    if result is None:
        result = MinimaxResult()
    if ai_color is None:
        ai_color = 'black'  # Lưu màu AI tại gốc cây

    if depth == 0 or board.is_terminal():
        result.score = board.evaluate()
        return result

    if max_player:
        max_eval = -math.inf
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if isinstance(piece, ChessPiece) and piece.color == ai_color:
                    moves = piece.filter_moves(piece.get_moves(board), board)
                    for move in moves:
                        board.make_move(piece, move[0], move[1], keep_history=True)
                        evaluation = minimax(board, depth - 1, alpha, beta, False, False, None, ai_color).score
                        board.unmake_move(piece)

                        if save_move:
                            result.update(piece, move, evaluation)

                        max_eval = max(max_eval, evaluation)
                        alpha = max(alpha, evaluation)
                        if beta <= alpha:
                            break
        result.score = max_eval
    else:
        min_eval = math.inf
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if isinstance(piece, ChessPiece) and piece.color != ai_color:
                    moves = piece.filter_moves(piece.get_moves(board), board)
                    for move in moves:
                        board.make_move(piece, move[0], move[1], keep_history=True)
                        evaluation = minimax(board, depth - 1, alpha, beta, True, False, None, ai_color).score
                        board.unmake_move(piece)

                        min_eval = min(min_eval, evaluation)
                        beta = min(beta, evaluation)
                        if beta <= alpha:
                            break
        result.score = min_eval

    return result


def get_ai_move(board):
    result = minimax(board, board.depth, -math.inf, math.inf, True, True)
    if board.log:
        logger.write()

    if not result.moves:
        return False

    best_score = result.score
    candidates = [m for m in result.moves if m[2] == best_score]
    piece, move, _ = random.choice(candidates)

    board.make_move(piece, move[0], move[1])
    return True


def get_random_move(board):
    pieces = []
    moves = []
    for i in range(8):
        for j in range(8):
            if isinstance(board[i][j], ChessPiece) and board[i][j].color != board.get_player_color():
                pieces.append(board[i][j])
    for piece in pieces[:]:
        piece_moves = piece.filter_moves(piece.get_moves(board), board)
        if len(piece_moves) == 0:
            pieces.remove(piece)
        else:
            moves.append(piece_moves)
    if len(pieces) == 0:
        return
    piece = random.choice(pieces)
    move = random.choice(moves[pieces.index(piece)])
    if isinstance(piece, ChessPiece) and len(move) > 0:
        board.make_move(piece, move[0], move[1])
