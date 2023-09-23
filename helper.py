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

from flask import redirect, render_template, session
from functools import wraps

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


def analyze_position(fen_position, depth=20):
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
        engine.configure({"Debug Log File": ""})
        board = chess.Board(fen_position)

        # Perform the analysis
        analysis = engine.analyse(board, chess.engine.Limit(depth=20))
        # Get the analysis results
        eval = analysis["score"].relative.score() / 100
        best_move = analysis["pv"][0]
        best_move_san = board.san(chess.Move.from_uci(str(best_move)))
        info = {}
        info["best_move"] = best_move_san
        info["evaluation"] = eval
        print(info)
        return info


    




