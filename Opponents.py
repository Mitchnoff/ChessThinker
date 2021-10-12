
#########################
# Opponents.py       #
# By: Mitchell Allen    #
# 9/10/21               #
#########################


import chess
import random
from stockfish import Stockfish


class RandomPlayer:

    def __init__(self, chessboard: chess.Board):
        self.moves_made = list()
        self.board = chessboard

    def figure_move(self):
        possible_moves = list()
        possible_moves.extend(self.board.legal_moves)
        idx = random.randint(0, len(possible_moves) - 1)
        move = possible_moves[idx]
        self.board.push_uci(str(move))
        return possible_moves[idx]

    def move(self, move: str):
        self.board.push_uci(move)


class FishPlayer:
    """
    Manages stockfish's moves
    """

    def __init__(self, chessboard: chess.Board):
        self.moves_made = list()
        self.path_to_exe = "C:\\Users\\allenm\\Desktop\\21-22 Year\\Fall\\Chessler\\stockfish_14_win_x64_avx2\\" \
                           "stockfish_14_x64_avx2.exe"
        self.fish = Stockfish(path=self.path_to_exe)
        self.board = chessboard

    def get_current_fen(self):
        return self.fish.get_fen_position()

    def set_elo(self, elo: int):
        self.fish.set_elo_rating(elo)

    def show_board(self):
        print(self.board)

    def reset_board(self):
        self.fish = Stockfish(path=self.path_to_exe)  # reset the stockfish object
        self.fish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")  # set up board using fen
        self.moves_made.clear()

    def move(self, move: str):
        # check first to see if the move is a valid move
        if not self.fish.is_move_correct(move_value=move):
            raise Exception("Invalid move:", move)
        else:
            self.moves_made.append(move)  # append move ot the list of made moves
            self.fish.set_position(self.moves_made)  # apply move to Stockfish
            self.board.push_uci(move)  # apply move to the chess.Board

    def figure_move(self, timeout=1000):
        # FIXME why is move none on second iteration?
        move = self.fish.get_best_move_time(timeout)  # get the best move possible in timeout ms
        self.move(move)  # apply the move
