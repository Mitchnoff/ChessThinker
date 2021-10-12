import random

import chess


def score_chessboard(board: chess.Board, k_val=9000, q_val=1000, r_val=550, b_val=350, n_val=350, p_val=100):

    score = 0
    board_str = str(board)

    for ch in board_str:
        if ch != '\n' and ch != '.':
            if ch == 'p':  # enemy pawn
                score -= p_val
            elif ch == 'P':  # friendly pawn
                score += p_val
            elif ch == 'r':  # enemy rook
                score -= r_val
            elif ch == 'R':  # friendly rook
                score += r_val
            elif ch == 'b':  # enemy bishop
                score -= b_val
            elif ch == 'B':  # friendly bishop
                score += b_val
            elif ch == 'n':  # enemy knight
                score -= n_val
            elif ch == 'N':  # friendly knight
                score += n_val
            elif ch == 'q':  # enemy queen
                score -= q_val
            elif ch == 'Q':  # friendly queen
                score += q_val
            elif ch == 'k':  # enemy king
                score -= k_val
            elif ch == 'K':  # friendly king
                score += k_val
    return score


def random_move(moves: list):
    """
    generates a random move from the legal possible moves
    ":param moves: list of valid moves for a given game state
    :return: move
    """
    idx = random.randint(0, len(moves) - 1)
    return moves[idx]


class BoardTree:

    def __init__(self, board: chess.Board, max_depth=3, scoring_style="average"):
        self.start_board = board
        self.start_node = BoardNode(self.start_board, 0, move_made="NONE")  # get starting node of the tree
        self.layer_nodes = list()
        self.create_tree(max_depth=max_depth, scoring_style=scoring_style)

    def create_tree(self, max_depth=3, scoring_style="average"):
        depth = 0
        nodes_to_populate = [self.start_node]

        while depth < max_depth:  # iterate until max_depth is reached
            new_nodes_to_populate = list()
            current_layer_nodes = list()
            for node in nodes_to_populate:
                current_layer_nodes.append(node)
                new_nodes = node.populate_node()
                new_nodes_to_populate.extend(new_nodes)
            self.layer_nodes.append(current_layer_nodes)
            depth += 1  # increment depth
            nodes_to_populate.clear()  # clear nodes to populate
            nodes_to_populate.extend(new_nodes_to_populate)  # fill nodes to populate with new nodes
        # append the last layer of nodes to the list of layer nodes
        self.layer_nodes.append(new_nodes_to_populate)

        # score the tree based on the scoring style
        if scoring_style == "average":
            while depth != 0:
                for node in self.layer_nodes[depth]:
                    node.score_to_average_of_children()
                depth -= 1

        elif scoring_style == "minimax":
            while depth != 0:
                is_white_turn = bool(depth % 2)
                for node in self.layer_nodes[depth]:
                    node.score_node(is_white_turn)
                depth -= 1
        else:
            raise Exception("Invalid scoring style: " + scoring_style)

    def choose_best_scoring_move(self):
        best_score = -999999
        possible_best_moves = list()

        for node in self.layer_nodes[1]:
            if node.get_score() > best_score:
                possible_best_moves.clear()
                possible_best_moves.append(node.get_move())
                best_score = node.get_score()
            elif node.get_score() == best_score:
                possible_best_moves.append(node.get_move())

        # DEBUG
        if len(possible_best_moves) == 0:
            print('wew')
        return possible_best_moves

    def figure_move(self, depth=3):
        move = random_move(self.choose_best_scoring_move())
        return move


class BoardNode:

    def __init__(self, board: chess.Board, depth: int, move_made: str):
        self.board = board
        self.depth = depth
        self.move_made = move_made
        self.score = None
        self.children = list()

        self.is_populated = False

    def __add__(self, other):
        return other + self.score

    def __str__(self):
        return "Score: " + str(self.score)

    def __gt__(self, other):
        if type(other) is not BoardNode:
            raise Exception("Invalid comparison between BoardNode and " + str(type(other)))
        else:
            return self.score > other.get_score()

    def __lt__(self, other):
        if type(other) is not BoardNode:
            raise Exception("Invalid comparison between BoardNode and " + str(type(other)))
        else:
            return self.score < other.get_score()

    def score_to_average_of_children(self):

        if len(self.children) == 0:
            self.score = score_chessboard(self.board)
        else:
            score = 0
            for node in self.children:
                score += node.get_score()
            self.score = score/len(self.children)

    def get_children(self):
        return self.children

    def set_score(self, score):
        self.score = score

    def get_score(self):
        return self.score

    def get_move(self):
        return self.move_made

    def populate_node(self):
        if self.is_populated:
            raise Exception("Populating a node twice is ILLEGAL")

        for mv in self.board.legal_moves:
            move = str(mv)
            new_board = self.board.copy()  # make a copy of the game board
            new_board.push_uci(move)  # apply move to the board
            self.children.append(BoardNode(new_board, self.depth + 1, move_made=move))  # make new boardNode
        self.is_populated = True
        return self.children

    def score_node(self, is_white_turn: bool):
        if len(self.children) == 0:    # case 1: leaf node, node has no children
            self.score = score_chessboard(self.board)
        elif is_white_turn:  # case 2: white turn, assume white chooses highest move
            self.score = max(self.children).get_score()
        else:                # case 3: black turn, assume black chooses lowest move
            self.score = min(self.children).get_score()
