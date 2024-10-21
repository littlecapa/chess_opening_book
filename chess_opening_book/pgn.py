import chess
import chess.pgn
from io import StringIO
from .stack import Stack

class PgnCreator:

    def __init__(self, game = None):
        self.stack = Stack()
        if game:
            self.game = game
            self.current_node = game.end()
        else:
            self.game = chess.pgn.Game()
            self.current_node = self.game

    def set_header(self, header, value):
        self.game.headers[header] = value

    def add_move(self, move, comment, is_main = False):
        self.stack.push(self.current_node)
        if is_main:
            self.current_node = self.current_node.add_main_variation(move)
        else:
            self.current_node = self.current_node.add_variation(move)
        self.current_node.comment = comment

    def mark_as_transposition(self):
        self.current_node.comment += " TRANSPOSITION!"

    def take_move_back(self):
        if self.stack.is_empty():
            raise Exception("Empty Stack")
        self.current_node = self.stack.pop()

    def print_status(self):
        print(self.game)
        print(str(self.stack))

    def is_valid_pgn(self):
        pgn_io = StringIO(str(self.game))
        try:
            _ = chess.pgn.read_game(pgn_io)
            return True
        except Exception as e:
            print(f"Wrong PGN, Error: {e}")
            return False

    def __str__(self):
        return str(self.game)