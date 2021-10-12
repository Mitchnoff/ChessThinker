
##
# Chess Tester
##


from BoardManager import BoardManager
from WindowsInhibitor import inhibit, uninhibit


def main():
    manager = BoardManager(opponent_type="Random")
    filepath = "C:\\users\\allenm\\desktop\\21-22 year\\fall\\chessler\\outputs\\" + input("Enter filename:\n") + ".xls"
    #manager.bench_test(filepath)
    # manager.play_game(show_board=True)
    inhibit()  # stops computer from going to sleep
    manager.random_bench_test(filepath=filepath, games_to_play=10, depth=5, show_board=True)
    uninhibit()  # allows computer to go to sleep


if __name__ == "__main__":
    main()
