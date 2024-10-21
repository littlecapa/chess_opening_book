class ChessPosition:
    def __init__(self, eval=0.0, winning=0, success=0):
        self.eval_min = eval
        self.eval_max = eval
        self.winning = winning
        self.nr_games = 1
        self.sum_success = success
        self.moves={}

    def update_position(self, eval, winning, success):
        if eval < self.eval_min:
            self.eval_min = eval
        if eval > self.eval_max:
            self.eval_max = eval
        self.winning += winning
        self.nr_games += 1
        self.sum_success += success

    def add_move(self, move, new_hash):
        if move not in self.moves:
            self.moves[move] = new_hash

    def get_moves(self):
        for move, new_hash in self.moves.items():
            yield move, new_hash

    def __str__(self):
        #out = " EVAL:"
        if self.eval_min == self.eval_max:
            out = f"[{self.eval_min}] "
        else:
            out= f"[{self.eval_min}-{self.eval_max}] "
        out += f" / ELO: {self.sum_success} "
        #out += f" / Winning: {self.winning} "
        out += f"({self.nr_games})"
        #out += "}"
        return out