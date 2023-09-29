import threading
from helper import analyze_position,random_fen_from_pgn

pgn = 'ct-2750-2864-2023.5.9.pgn'
fen = random_fen_from_pgn(pgn)
fen = fen[0]
def thread_func():
    data = analyze_position(fen, 20, 3)
    print(data)

thread = threading.Thread(target=thread_func)
thread.start()

print("waiting")

before_data = analyze_position(fen, 15, 1)
print(f"before data {before_data}")