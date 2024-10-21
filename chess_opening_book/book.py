import pickle
from .zobrist_hash import ZobristHash
from .position import ChessPosition
from .pgn import PgnCreator

class OpeningBook:

    INITIAL_POS = "xxx"

    def __init__(self, max_moves = 40):
        self.max_moves = max_moves
        self.positions = {}
        self.transpositions = {}
        self.stats = {}
        self.stats["nr_games"] = 0
        self.stats["nr_moves"] = 0
        self.stats["max_eval"] = 0.0
        self.zh = ZobristHash()
        self.init_pos = ChessPosition(eval = 0.0, winning = 0, success = 0)
        self.init_hash = self.zh.get_init_hash()
        self.positions[self.init_hash] = self.init_pos

    def save(self, filename):
        # Open the file in binary write mode and serialize the data
        print(f'Book is based on {self.stats["nr_games"]} Games and {self.stats["nr_moves"]} Moves (unique Positions: {len(self.positions)}) Max-Eval: {self.stats["max_eval"]}')
        with open(filename, 'wb') as file:
            pickle.dump({'positions': self.positions, 'transpositions': self.transpositions, 'stats': self.stats}, file)

    def load(self, filename):
        # Open the file in binary read mode and deserialize the data
        with open(filename, 'rb') as file:
            data = pickle.load(file)
            self.positions = data['positions']
            self.transpositions = data['transpositions']
            self.stats = data['stats']

    def new_game(self, game):
        self.move_str = ""
        self.stats["nr_games"] += 1
        self.curr_pos = self.INITIAL_POS
        self.game = game
        self.board = game.board()
        self.hash = self.init_hash
        self.half_move_counter = 0
        try:
            self.rating_diff = int(game.headers["WhiteRatingDiff"])
        except Exception as e:
            self.rating_diff = 0
            print(f"Bad Rating diff")
        if game.headers["Result"] == "1-0":
            self.result = +1
        elif game.headers["Result"] == "0-1":
            self.result = -1
        else:
            self.result = 0
        self.akt_pos = self.init_pos

    def push_move(self, move, eval):
        self.half_move_counter += 1
        if self.half_move_counter > self.max_moves:
            return False
        self.stats["nr_moves"] += 1
        if eval > self.stats["max_eval"]:
            self.stats["max_eval"] = eval
        if self.half_move_counter % 2 == 1:
            self.move_str += str((self.half_move_counter+1)/2) + "."
        self.move_str += str(move) + " "
        old_hash = self.hash
        self.board, self.hash = self.zh.execute_move_update_hash(old_hash=old_hash, move=move, board=self.board)
        self.positions[old_hash].add_move(move=move, new_hash=self.hash)
        self.process_pos(eval)
        return True
    
    def process_pos(self, eval):
        if self.hash not in self.positions:
            self.positions[self.hash] = ChessPosition(eval, self.result, self.rating_diff)
        else:
            self.positions[self.hash].update_position(eval, self.result, self.rating_diff)

    def pos2str(self, pos, visited={}):
        output = ""
        if pos in visited:
            return visited, f"Position {pos} is reached by Transposition!"
        else:
            visited[pos] = True
        index = 0
        for move, new_pos in self.positions[pos].get_moves():
            index += 1
            output += f"{pos} {index} Move: {move} {new_pos}\n"
            visited, new_output = self.pos2str(new_pos)
            output += f"{new_output}"
        return visited, output
    
    def __str__(self):
        visited, output = self.pos2str(self.init_hash)
        if len(visited) != len(self.positions):
            print(f"Error! Visited: {len(visited)} Positions: {len(self.positions)}")
        return output
    
    def pos2pgn(self, pos, visited=None):
        if visited is None:
            visited = {}
        if pos in visited:
            self.pc.mark_as_transposition()
            return visited
        visited[pos] = True
        first = True
        for move, new_pos in self.positions[pos].get_moves():
            self.pc.add_move(move, str(self.positions[new_pos]), is_main = first)
            first = False
            visited = self.pos2pgn(new_pos, visited)
            self.pc.take_move_back()            
        return visited
    
    def book2pgn(self, pgn_structure = None):
        #
        # pgn_structure is a python game object
        #
        self.pc = PgnCreator(pgn_structure)
        if pgn_structure:
            self.pc.set_header("White", pgn_structure.headers["White"])
            self.pc.set_header("Black", pgn_structure.headers["Black"])
            current_hash = self.zh.hash_board(self.pc.current_node.board())
            if current_hash not in self.positions:
                raise Exception("Template Position not found in Book")
        else:
            self.pc.set_header("White", "My")
            self.pc.set_header("Black", "Book")
            current_hash = self.init_hash
        _ = self.pos2pgn(current_hash)
        
        return str(self.pc)



#
# Later
#
    def store_transposition(self, position, move_string):
        try:
            transpos = self.transpositions[position]
            self.transpositions[position].append(move_string)
        except KeyError:
            self.transpositions[position] = [move_string]
