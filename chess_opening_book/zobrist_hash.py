import chess, chess.polyglot
from collections import namedtuple
import typing

class ZobristHash:
    WCK_INDEX = 8*8*12
    WCQ_INDEX = WCK_INDEX + 1
    BCK_INDEX = WCQ_INDEX + 1
    BCQ_INDEX = BCK_INDEX + 1
    EP_INDEX = BCQ_INDEX + 1
    TURN_INDEX = EP_INDEX + 8

    # Define a named tuple for the chessboard state
    PieceMoveState = namedtuple("PieceMoveState", [
        "ep_square",
        "turn",
        "wck",
        "wcq",
        "bck",
        "bcq",
        "move_from",
        "move_to",
        "ep_move",
        "piece_moved",
        "piece_captured",
        "piece_promoted"
    ])

    def __init__(self, random_array = None):
        if random_array is None:
            self.random_array = chess.polyglot.POLYGLOT_RANDOM_ARRAY
        else:
            self.random_array = random_array

    def get_square_piece_index(self, piece, color, square):
        piece_index = self.get_piece_index(piece, color)
        square_piece_index = 64 * piece_index + square
        if square_piece_index < 0 or square_piece_index >= len(chess.polyglot.POLYGLOT_RANDOM_ARRAY):
            exit()
        return square_piece_index

    def get_piece_index(self, piece, color):
        return (piece-1) * 2 + int(color)

    def get_ep_index(self, ep, turn):
        if turn == chess.BLACK:
            index = ep-chess.A3
        else:
            index = ep-chess.A6
        return index + ZobristHash.EP_INDEX

    def update_hash(self, hash, array_index):
        hash ^= self.random_array[array_index]
        return hash

    def get_board_move_state(self, board, move):
        if board.is_en_passant(move):
            ep_move = True
        else:
            ep_move = False
        return self.PieceMoveState(ep_square=board.ep_square,
                                turn=board.turn,
                                wck=board.has_kingside_castling_rights(chess.WHITE),
                                wcq=board.has_queenside_castling_rights(chess.WHITE),
                                bck=board.has_kingside_castling_rights(chess.BLACK),
                                bcq=board.has_queenside_castling_rights(chess.BLACK),
                                move_from = move.from_square,
                                move_to = move.to_square,
                                piece_moved = board.piece_type_at(move.from_square),
                                ep_move = ep_move,
                                piece_captured = board.piece_type_at(move.to_square),
                                piece_promoted = move.promotion)

    def hash_position(self, board) -> int:
        zobrist_hash = 0
        for color, squares in enumerate(board.occupied_co):
                for square in chess.scan_reversed(squares):
                    index = self.get_square_piece_index(board.piece_type_at(square), color, square)
                    zobrist_hash = self.update_hash(zobrist_hash, index)
        return zobrist_hash
    
    def hash_board(self, board) -> int:
            zobrist_hash = self.hash_position(board)
            #
            # Hash the rest
            #
            if board.turn:
                zobrist_hash = self.update_hash(zobrist_hash, ZobristHash.TURN_INDEX)
            if board.has_kingside_castling_rights(chess.WHITE):
                zobrist_hash = self.update_hash(zobrist_hash, ZobristHash.WCK_INDEX)
            if board.has_queenside_castling_rights(chess.WHITE):
                zobrist_hash = self.update_hash(zobrist_hash, ZobristHash.WCQ_INDEX)
            if board.has_kingside_castling_rights(chess.BLACK):
                zobrist_hash = self.update_hash(zobrist_hash, ZobristHash.BCK_INDEX)
            if board.has_queenside_castling_rights(chess.BLACK):
                zobrist_hash = self.update_hash(zobrist_hash, ZobristHash.BCQ_INDEX)
            if board.ep_square is not None:
                index = self.get_ep_index(board.ep_square, board.turn)
                zobrist_hash ^= chess.polyglot.POLYGLOT_RANDOM_ARRAY[index]
            return zobrist_hash

    def get_init_hash(self):
        board = chess.Board()
        return self.get_zobrist_hash(board)
    
    def get_zobrist_hash(self, board):
        hash = self.hash_board(board)
        return hash

    def execute_move_update_hash(self, old_hash, move, board):
        move = chess.Move.from_uci(str(move))
        old_board_move_state = self.get_board_move_state(board, move)
        board.push(move)
        return board, self.increment_hash(board, old_board_move_state, old_hash)

    def increment_hash(self, board, old_board_move_state, old_hash):
        # Turn has changed
        new_hash = self.update_hash(old_hash, ZobristHash.TURN_INDEX)
        # OLD EP must be deleted
        if old_board_move_state.ep_square is not None:
            ep_index = self.get_ep_index(old_board_move_state.ep_square, old_board_move_state.turn)
            new_hash = self.update_hash(new_hash, ep_index)
        # Check the new non Move State Variables
        if board.ep_square is not None:
            ep_index = self.get_ep_index(board.ep_square, board.turn)
            new_hash = self.update_hash(new_hash, ep_index)
        if old_board_move_state.wck != board.has_kingside_castling_rights(chess.WHITE):
            new_hash = self.update_hash(new_hash, ZobristHash.WCQ_INDEX)
        if old_board_move_state.wcq != board.has_queenside_castling_rights(chess.WHITE):
            new_hash = self.update_hash(new_hash, ZobristHash.WCK_INDEX)
        if old_board_move_state.bcq != board.has_queenside_castling_rights(chess.BLACK):
            new_hash = self.update_hash(new_hash, ZobristHash.BCQ_INDEX)
        if old_board_move_state.bck != board.has_kingside_castling_rights(chess.BLACK):
            new_hash = self.update_hash(new_hash, ZobristHash.BCK_INDEX)
        # Update according to move
        return self.update_hash_move(old_board_move_state, new_hash)
    
    def is_castling(self, move_from, move_to):
        if move_from == chess.E1 and move_to == chess.G1:
            castling = True
            from_sq = chess.H1
            to_sq = chess.F1
            color = chess.WHITE
        elif move_from == chess.E1 and move_to == chess.C1:
            castling = True
            from_sq = chess.A1
            to_sq = chess.D1
            color = chess.WHITE
        elif move_from == chess.E8 and move_to == chess.G8:
            castling = True
            from_sq = chess.H8
            to_sq = chess.F8
            color = chess.WHITE
        elif move_from == chess.E8 and move_to == chess.C8:
            castling = True
            from_sq = chess.A8
            to_sq = chess.D8
            color = chess.BLACK
        else:
            castling = False
            from_sq = to_sq = color = None
        return castling, from_sq, to_sq, color

    def update_hash_move(self, state, hash):
        # Execute the current move (from, to); check for promotion and capture
        # Clear the old square
        from_index = self.get_square_piece_index(piece = state.piece_moved, color = state.turn, square = state.move_from)
        hash = self.update_hash(hash, from_index)
        # Set new square
        if state.piece_promoted is None:
            piece = state.piece_moved
        else:
            piece = state.piece_promoted
        to_index = self.get_square_piece_index(piece = piece, color = state.turn, square = state.move_to)
        hash = self.update_hash(hash, to_index)
        # If current move is capture, then remove captured piece
        if state.piece_captured is not None:
            capture_index = self.get_square_piece_index(piece = state.piece_captured, color = not state.turn, square = state.move_to)
            hash = self.update_hash(hash, capture_index)
        # Is the current move EP?
        if state.ep_move:
            if state.turn == chess.BLACK:
                enemy_pawn_square = state.move_to + 8
            else:
                enemy_pawn_square = state.move_to - 8
            capture_index = self.get_square_piece_index(piece = chess.PAWN, color = not state.turn, square = enemy_pawn_square)
            hash = self.update_hash(hash, capture_index)
        # Check Castling
        castling, rook_from_sq, rook_to_sq, color = self.is_castling(state.move_from, state.move_to)
        if castling:
            from_index = self.get_square_piece_index(chess.ROOK, color, rook_from_sq)
            hash = self.update_hash(hash, from_index)
            to_index = self.get_square_piece_index(chess.ROOK, color, rook_to_sq)
            hash = self.update_hash(hash, to_index)
        return hash
