import chess.pgn
import os
import io
import sys
import re
from datetime import datetime
from chess_opening_book.chess_opening_book.book import OpeningBook

def get_eval(comment):
    pattern = r"\[%eval ([+-]?\d+(?:\.\d+)?)\]"    
    # Find all matches in the string
    matches = re.findall(pattern, comment)
    # Convert matched values to float
    if matches:
        evals = [float(match) for match in matches]
        for eval in evals:
            return float(eval)
    else:
        pattern = r"\[%eval #([+-]?\d+)\]"
        matches = re.findall(pattern, comment)
        evals = [int(match) for match in matches]
        for eval in evals:
            if eval > 0:
                return 100.0 - eval
            return -100.0 - eval
    return 0.0

def process_move(move, comment, book):
    eval = get_eval(comment)
    return book.push_move(move, eval)

def process_game(game, book):
    book.new_game(game)
    node = game
    while node.variations:
        next_node = node.variation(0)  # Get the mainline move
        move = next_node.move
        comment = next_node.comment
        if not process_move(move, comment, book):
            break
        node = next_node  # Move to the next node

def str2game(pgn_string):
    pgn_stream = io.StringIO(pgn_string)
    return chess.pgn.read_game(pgn_stream)

def read_pgns(pgn_file):
    with open(pgn_file, 'r', encoding='UTF-8') as pgn:
        pgn_string = ""
        for line in pgn:
            if line.startswith("[Event"):  # Start of a new game
                if pgn_string:  # If a previous game exists, yield it
                    yield str2game(pgn_string)
                    pgn_string = ""  # Reset for the new game
            pgn_string += line  # Append the current line to the PGN string

        if pgn_string:  # Yield the last game after the loop ends
            yield str2game(pgn_string)


def process_pgn(pgn_file, output_folder, book):
    # Ensure the output folder exists
    start = datetime.now()
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    game_number = 1
    try:
        for game in read_pgns(pgn_file):
            if game_number % 5000 == 0:
                now = datetime.now()
                elapsed_time = now - start
                print(f"Processed {game_number} games. Time now: {now}. Elapsed time: {elapsed_time}")
            if game is None:
                break  # No more games to read
            process_game(game, book)
            game_number += 1
    except Exception as e:
        print(f"Game Number: {game_number}, Exception: {e}")
        return
    
    print(f"Processed {game_number} games. Time now: {datetime.now()}. Elapsed time: {datetime.now()-start}")
    print(str(book))
    book_output_path = os.path.join(output_folder, "book.cob")
    book.save(book_output_path)
            
if __name__ == "__main__":
    # Get the PGN file path and output folder from the command line arguments
    if len(sys.argv) != 3:
        print("Usage: python script.py <path_to_pgn_file> <path_to_output_folder>")
        sys.exit(1)

    book = OpeningBook()

    pgn_file = sys.argv[1]
    output_folder = sys.argv[2]

    process_pgn(pgn_file, output_folder, book)
