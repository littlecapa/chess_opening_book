import pickle
from .zobrist_hash import ZobristHash
from .position import ChessPosition

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
        print("New Game")
        self.move_str = ""
        self.stats["nr_games"] += 1
        self.curr_pos = self.INITIAL_POS
        self.game = game
        self.board = game.board()
        self.hash = self.init_hash
        self.half_move_counter = 0
        self.rating_diff = int(game.headers["WhiteRatingDiff"])
        if game.headers["Result"] == "1-0":
            self.result = +1
        elif game.headers["Result"] == "0-1":
            self.result = +1
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
            return visited, output
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


#
# Later
#
    def store_transposition(self, position, move_string):
        try:
            transpos = self.transpositions[position]
            self.transpositions[position].append(move_string)
        except KeyError:
            self.transpositions[position] = [move_string]

    def store_position(self, position, move_string, white_to_move, result, white_elo, black_elo, white_rating_diff, black_rating_diff):
        pos = None
        pass