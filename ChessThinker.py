
##
#
# 9/10/21
##
import random
import chess
from BoardTree import BoardTree

from operator import itemgetter


EMPTY = "_"


def random_move(moves: list):
    """
    generates a random move from the legal possible moves
    ":param moves: list of valid moves for a given game state
    :return: move
    """
    idx = random.randint(0, len(moves) - 1)
    return moves[idx]


class ChessThinker:

    def __init__(self, chessboard: chess.Board):
        self.board = chessboard
        self.is_random = True
        self.depth = 3
        self.game_state = ""

    def set_depth(self, depth: int):
        self.depth = depth

    def get_depth(self):
        return self.depth

    def read_fen(self, fen: str):
        """
        reads a fen position
        :param fen: fen string representation
        :return:
        """
        iteration = 0

        # initialize lists for the board representation
        board = list()
        row_contents = list()

        board_str_len = 0

        while fen[board_str_len] != " ":
            board_str_len += 1

        # read in data from the first fen string representing the board
        for i in range(board_str_len):
            ch = fen[i]
            if ch == "/":  # skip every forward slash
                iteration += 1
                board.append(row_contents)
                row_contents = list()
            else:
                if ch.isnumeric():  # check for numeric fen values, indicating empty spaces
                    for _ in range(int(ch)):
                        row_contents.append(EMPTY)
                else:
                    row_contents.append(ch)
        board.append(row_contents)  # append last to the board
        board_str_len += 1  # skip the space between the initial string and the red of the FEN notation

    def generate_move(self):
        legal_moves = list()
        legal_moves.extend(self.board.legal_moves)

        move = self.adversarial_search()

        return str(move)

    def best_apparent_move(self, moves: list, debug=False):
        current_fen = self.board.fen()
        test_board = chess.Board(fen=current_fen)
        if debug:
            print(test_board, "\n")
        scores_and_moves = list()
        for mv in moves:
            move = str(mv)
            test_board.push_uci(move)  # do the move on the board
            score = score_chessboard(test_board)  # evaluate the new board
            scores_and_moves.append((score, move))  # save score and move
            test_board.set_fen(current_fen)  # reset board

        # TODO: use score used by stockfish/chess board

        # initialize max score
        max_score = -900000
        possible_moves = list()
        # get the highest scores
        for tup in scores_and_moves:
            if tup[0] > max_score:
                possible_moves.clear()  # clear the list as better moves were found
                possible_moves.append(tup[1])  # append the new best move
                max_score = tup[0]  # set new max score
            elif tup[0] == max_score:
                possible_moves.append(tup[1])  # append possible new best move

        return random_move(possible_moves)

    def adversarial_search_old(self, moves: list):

        current_fen = self.board.fen()
        test_board = chess.Board(fen=current_fen)
        scores_and_moves = list()

        for mv in moves:
            move = str(mv)
            test_board.push_uci(move)
            scores_and_moves.append((self.adversarial_likely_opponent_score(test_board), move))
            test_board.set_fen(current_fen)  # reset board after testing possible move
        # initialize max score
        max_score = -900000
        possible_moves = list()
        # get the highest scores
        for tup in scores_and_moves:
            if tup[0] > max_score:
                possible_moves.clear()  # clear the list as better moves were found
                possible_moves.append(tup[1])  # append the new best move
                max_score = tup[0]  # set new max score
            elif tup[0] == max_score:
                possible_moves.append(tup[1])  # append possible new best move
        return random_move(possible_moves)

    def adversarial_likely_opponent_score(self, board: chess.Board):

        current_fen = board.fen()
        legal_moves = list()
        legal_moves.extend(board.legal_moves)
        scores = list()

        for mv in legal_moves:
            move = str(mv)
            board.push_uci(move)
            score = score_chessboard(board)
            scores.append(score)
            board.set_fen(current_fen)  # reset board

        return min(scores)

    def adversarial_search(self):

        tree = BoardTree(self.board, max_depth=self.depth, scoring_style="average")
        move = tree.figure_move()
        return move

