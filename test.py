import chess.pgn
import os


global i
i = 0
def pgn_parse(file_path):
    with open(file_path) as pgnfile:
        while True:
            game = chess.pgn.read_game(pgnfile)
            if game is None:
                break
            global i
            i = i + 1
            print(i)
            

filenum = 0
for file in os.listdir("PGN/Carlsen, Magnus"):
    if file.endswith(".pgn"):
        file_path = os.path.join("PGN/Carlsen, Magnus", file)
        filenum += 1
        print(f"filenum: {filenum}")
        pgn_parse(file_path)



