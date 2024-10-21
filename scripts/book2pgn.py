import chess.pgn
import os
import sys
from chess_opening_book.chess_opening_book.book import OpeningBook
            
if __name__ == "__main__":
    # Get the PGN file path and output folder from the command line arguments
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_input_folder>")
        sys.exit(1)
    input_folder = sys.argv[1]
    book_input_path = os.path.join(input_folder, "book.cob")
    template_input_path = os.path.join(input_folder, "template.pgn")
    book = OpeningBook()
    book.load(book_input_path)
    template_path = os.path.join(input_folder, "template.pgn")
    if os.path.isfile(template_input_path):
        try:
            with open(template_path, 'r', encoding='UTF-8') as pgn_file:
                # Read the first game from the PGN file
                template = chess.pgn.read_game(pgn_file)
        except Exception as e:
            print(f"Invalid PGN File {e}")
            raise Exception(e)
    else:
        template = None
    pgn_output_path = os.path.join(input_folder, "book.pgn")
    with open(pgn_output_path , "w") as file:
        file.write(book.book2pgn(template))
