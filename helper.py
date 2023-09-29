import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import chess
import chess.engine
import os
import sys
import io
import random
import chess.pgn
from flask import redirect, render_template, session
from functools import wraps
from pgn_parser import pgn, parser

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/signin")
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", message=escape(message)), code

def duplicateUsernameCheck(username, rows):
    for user in rows:
        if user['username'] == username:
            return True
    return False


def analyze_position(fen_position, depth = 20, lines = 3):
    """
    Analyze a chess position using the Stockfish engine.

    Args:
        fen_position (str): FEN (Forsyth-Edwards Notation) string representing the chess position.
        depth (int): The depth to which Stockfish should analyze the position.

    Returns:
        dict: A dictionary containing the analysis information.
    """

    # Redirect stdout to an in-memory buffer

    with chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-modern.exe") as engine:
        board = chess.Board(fen_position)
        # Perform the analysis
        analysis = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=lines)
        # Get the analysis results

        best_move = analysis[0]["pv"][0]
        
        best_move_san = board.san(chess.Move.from_uci(str(best_move)))
        info = {}
        info["best_move"] = best_move_san
        info["evaluation"] = float(analysis[0]["score"].relative.score()) / 100
        if board.turn == chess.BLACK:
            info["evaluation"] = (float(analysis[0]["score"].relative.score()) / 100) * -1
        try:
            info["second_best"] = analysis[1]["pv"][0]
            info["second_best"] = board.san(chess.Move.from_uci(str(info["second_best"])))
            info["second_eval"] = float(analysis[1]["score"].relative.score()) / 100
            if board.turn == chess.BLACK:
                info["second_eval"] = (float(analysis[1]["score"].relative.score()) / 100) * -1
            try:
                info["third_best"] = analysis[2]["pv"][0]
                info["third_best"] = board.san(chess.Move.from_uci(str(info["third_best"])))
                info["third_eval"] = float(analysis[2]["score"].relative.score()) / 100
                if board.turn == chess.BLACK:
                    info["third_eval"] = (float(analysis[2]["score"].relative.score()) / 100) * -1
            except IndexError:
                pass
        except IndexError:
            pass
        return info


def random_fen_from_pgn(pgnfile):
    with open(pgnfile) as pgn_file:
        pgn_game = chess.pgn.read_game(pgn_file)
        board = pgn_game.board()
        move_count = 0
        for _ in pgn_game.mainline_moves():
            move_count += 0.5
        desired_move_number = random.randint(5, move_count) 
        desired_move_number -= 0.5
        if random.randint(1,2) == 1:
             desired_move_number -= 0.5
        desired_move_number *= 2
        for move in pgn_game.mainline_moves():
            if board.ply() == desired_move_number:
                fen = board.fen()
                color = "White"
                if fen.split(' ')[1] == 'b':
                    color = "Black"
                grandmove = move
                grandmove = board.san(chess.Move.from_uci(str(grandmove))) 
                board.push(move)
                gmfen = board.fen()
                break
            board.push(move)
        gmmove_eval = analyze_position(gmfen, 20, 1)
        gmmove = {}
        gmmove["grandmaster_move"] = grandmove
        gmmove["evaluation"] = gmmove_eval['evaluation']
        return fen, gmmove, color

import chess

def user_input_to_uci(move_input, fen):
    board = chess.Board(fen)

    # Try to convert the user-friendly input to UCI for standard moves
    try:
        move = board.parse_san(move_input)
        return move.uci()
    except ValueError:
        # Try again with the input converted to title case
        move_input = str(move_input).capitalize()
        try:
            move = board.parse_san(move_input)
            return move.uci()
        except ValueError:
            pass

    # Handle promotion moves (e.g., "e8=Q", "e8+")
    if "=" in move_input or "+" in move_input:
        # Check if the move ends with a promotion piece (Q, R, B, N)
        if move_input[-1] in ['Q', 'R', 'B', 'N']:
            # Extract the destination square
            dest_square = move_input[-3:-1]

            # Find the piece to move based on its destination square
            for move in board.legal_moves:
                if move.to_square == chess.parse_square(dest_square):
                    promotion = move_input[-1].upper()
                    from_square = move.from_square
                    move = chess.Move(from_square, chess.parse_square(dest_square), promotion=chess.Piece.from_symbol(promotion))
                    return move.uci()

    # Handle invalid input
    return None



def game_info(pgn_file):
    # Create a PGN database to read games from the file
    with open(pgn_file) as pgn:
        pgn_game = chess.pgn.read_game(pgn)

        while pgn_game:
            # Access the game headers to extract player information
            headers = pgn_game.headers

            # Extract player names and Elo ratings (if available)
            white_player = headers.get("White", "Unknown White Player")
            black_player = headers.get("Black", "Unknown Black Player")
            white_elo = headers.get("WhiteElo", "Unknown")
            black_elo = headers.get("BlackElo", "Unknown")
            gameinfo = {}
            gameinfo['date'] = headers.get("Date", "Unknown Date")
            gameinfo['result'] = headers.get("Result", "Unknown Result")
            gameinfo['event'] = headers.get("Event", "Unknown Event")
            gameinfo['white'] = f"White: {white_player}: {white_elo} Elo"
            gameinfo['black'] = f"Black: {black_player}: {black_elo} Elo" 
            
            
            return gameinfo
        

    




