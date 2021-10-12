import chess
import pandas as pd
import time
import xlwt

from ChessThinker import ChessThinker
from Opponents import FishPlayer, RandomPlayer


class BoardManager:

    def __init__(self, opponent_type: str):
        opponent_type = opponent_type.lower()
        valid_opponents = ["random", "stockfish"]

        if opponent_type not in valid_opponents:
            raise Exception("Invalid Opponent: " + str(opponent_type))

        self.chessboard = chess.Board()
        if opponent_type == "stockfish":
            self.opponent = FishPlayer(self.chessboard)
        elif opponent_type == "random":
            self.opponent = RandomPlayer(self.chessboard)
        self.chess_thinker = ChessThinker(self.chessboard)
        self.opponent_type = opponent_type

        # initialize counts for each player's win
        self.thinker_wins = 0
        self.opponent_wins = 0
        self.stalemates = 0

    def reset_board(self):
        """
        resets both the chess.Board board and the Stockfish's board
        :return:
        """
        self.chessboard.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")  # set the chess.Board
        if self.opponent_type == " stockfish":
            self.opponent.reset_board()

    def play_game(self, show_board: bool):
        # reset the board to the start position
        self.reset_board()  # reset the board before playing

        is_white_player_turn = True

        turn_count = 0
        start = time.time()
        if show_board:
            while not self.chessboard.is_game_over():
                if is_white_player_turn:
                    # white move
                    self.thinker_move()
                else:
                    # black move
                    self.opponent.figure_move()
                turn_count += 1
                print("Turn count:", str(turn_count), "\n")
                print(self.chessboard, "\n\n")
                is_white_player_turn = not is_white_player_turn
        else:
            while not self.chessboard.is_game_over():
                if is_white_player_turn:
                    # white move
                    self.thinker_move()
                else:
                    # black move
                    self.opponent.figure_move()
                turn_count += 1
                is_white_player_turn = not is_white_player_turn
        elapsed = round(time.time() - start, 2)
        print(self.chessboard, "\n")
        outcome = self.chessboard.outcome()

        # count who wins the game
        if outcome.winner is True:
            outcome_string = "Thinker Win"
            self.thinker_wins += 1
        elif outcome.winner is False:
            outcome_string = "Opponent Win"
            self.opponent_wins += 1
        else:
            outcome_string = outcome.termination.name
            self.stalemates += 1

        print("SCOREBOARD:")
        print("Thinker wins:", self.thinker_wins)
        print(self.opponent_type, " wins:   ", self.opponent_wins)
        print("Stalemates:", str(self.stalemates), "\n\n\n")
        return outcome_string, turn_count, elapsed, self.chess_thinker.get_depth()

    def thinker_move(self):
        move = self.chess_thinker.generate_move()  # generate a move to make from the chess_thinker
        self.opponent.move(move)  # apply the move to the opponent's board

    def random_bench_test(self, filepath: str, games_to_play: int, depth: int, show_board=False):

        self.chess_thinker.set_depth(depth)

        df = pd.DataFrame(columns=["Game", "Turns to finish", "runtime", "depth", "outcome"])
        start = time.time()
        for game_num in range(1, games_to_play + 1):
            outcome, turns, elapsed, depth = self.play_game(show_board=show_board)
            df.loc[len(df.index)] = [game_num, turns, elapsed, depth, outcome]
        total_elapsed = time.time() - start

        # wew
        # save results to an excel workbook
        book = xlwt.Workbook()
        sheet = book.add_sheet(sheetname="Results")
        # expand column widths
        sheet.col(0).width = 256 * 16
        sheet.col(1).width = 256 * 16
        sheet.col(2).width = 256 * 16
        sheet.col(4).width = 256 * 16
        sheet.col(6).width = 256 * 16
        sheet.col(7).width = 256 * 16
        sheet.col(8).width = 256 * 16
        sheet.col(9).width = 256 * 16
        sheet.col(10).width = 256 * 16

        bold_style = xlwt.easyxf("font: bold 1")

        sheet.write(0, 1, "Thinker Wins:", bold_style)
        sheet.write(0, 2, "Random Player Wins:", bold_style)
        sheet.write(0, 4, "Total Runtime: (s)", bold_style)
        sheet.write(1, 1, self.thinker_wins)
        sheet.write(1, 2, self.opponent_wins)
        sheet.write(1, 4, round(total_elapsed, 2))  # write elapsed time

        sheet.write(0, 6, "Game Number:", bold_style)
        sheet.write(0, 7, "Turns to endgame:", bold_style)
        sheet.write(0, 8, "Elapsed Time (s):", bold_style)
        sheet.write(0, 9, "Depth:", bold_style)
        sheet.write(0, 10, "Outcome:", bold_style)

        row_num = 1
        for row in df.iterrows():
            row = pd.Series.to_list(row[1])
            sheet.write(row_num, 6, row[0])   # write the game number
            sheet.write(row_num, 7, row[1])   # write the turns it took to complete the game
            sheet.write(row_num, 8, row[2])   # write the elapsed time
            sheet.write(row_num, 9, row[3])   # write the depth
            sheet.write(row_num, 10, row[4])  # write the outcome
            row_num += 1
        book.save(filepath)
        return df

    def fish_bench_test(self, filepath, games_per_difficulty=5, min_difficulty=0, max_difficulty=6) -> pd.DataFrame:
        """
        Runs a bench test to evaluate the Thinker against the fish player at various difficulties
        :param filepath: filepath to save the excel document to
        :param games_per_difficulty: how many games to play at a given difficulty
        :param min_difficulty: minimum difficulty to begin at
        :param max_difficulty: maximum difficulty to iterate to
        :return: pd.Dataframe containing the scores of each game
        """
        df = pd.DataFrame(columns=['Difficulty', 'Thinker Wins', 'Fish Wins'])
        start = time.time()
        # run the tests
        for i in range(min_difficulty, max_difficulty):
            elo = i * 250
            print("ELO:", elo)
            self.opponent.set_elo(elo)
            # run game games_per_difficulty times
            for _ in range(0, games_per_difficulty):
                self.play_game(show_board=False)
            df.loc[len(df.index)] = [elo, self.thinker_wins, self.opponent_wins]
            self.thinker_wins = 0
            self.opponent_wins = 0
        elapsed = time.time() - start
        print("Test ran for", elapsed, "seconds.")

        # save results to an excel workbook
        book = xlwt.Workbook()
        sheet = book.add_sheet(sheetname="Results")
        sheet.col(0).width = 256 * 16
        sheet.col(1).width = 256 * 16
        sheet.col(2).width = 256 * 16
        sheet.col(4).width = 256 * 16
        bold_style = xlwt.easyxf("font: bold 1")

        sheet.write(0, 0, "ELO:", bold_style)
        sheet.write(0, 1, "Thinker Wins:", bold_style)
        sheet.write(0, 2, "Fish Wins:", bold_style)
        sheet.write(0, 4, "Runtime: (s)", bold_style)
        sheet.write(1, 4, round(elapsed, 2))  # write elapsed time

        row_num = 1
        # iterate over all rows of the dataframe and print the values to excel
        for row in df.iterrows():
            values = row[1].values  # get the values of the df
            sheet.write(row_num, 0, values[0])  # write difficulty
            sheet.write(row_num, 1, values[1])  # write thinker score
            sheet.write(row_num, 2, values[2])  # write fish score
            row_num += 1  # iterate row number
        book.save(filepath)

        return df
