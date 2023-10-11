from flask import Flask, request, redirect, session, render_template, jsonify
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import apology, login_required, duplicateUsernameCheck, analyze_position, random_fen_from_pgn, game_info, user_input_to_uci, listoflines, getfirstword, uci_to_algebraic
from flask_limiter import Limiter
from datetime import datetime
import ast
import chess
import random

app = Flask(__name__)
app.static_folder = 'static'

limiter = Limiter(
    key_func=lambda: request.remote_addr,
    storage_uri="memory://",
    app=app, default_limits=["300 per day", "120 per hour"])

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
Session(app)

db = SQL("sqlite:///users.db")
gamesdb = SQL("sqlite:///pgn.db")

@limiter.request_filter
def custom_message():
    # Custom response when rate limit is exceeded
    return "Rate limit exceeded. Please try again later.", 429

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    person = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    names = listoflines("GmNames.txt", "")
    #namesnospaces is for the query parameter so that there's no space which would make the link invalid
    namesnospaces = listoflines("GmNames.txt", "letteronly")
    namesdict =  {}
    i = 0
    for name in names:
        namesdict[name] = namesnospaces[i]
        i += 1
    if request.method == "GET":
        return render_template("index.html", accountname = person[0]['username'], namesdict = namesdict)

@app.route("/games")
@login_required
def games():
    player = request.args.get("player")
    if player == "PickRandomGM":
        list = listoflines("GmNames.txt", "letteronly")
        player = list[random.randint(0, len(list) - 1)]
    player = getfirstword(player)
    player = f"%{player}%"
    rows = gamesdb.execute("SELECT *,CASE WHEN white LIKE ? THEN 'white' WHEN black LIKE ? THEN 'black' ELSE 'unknown' END AS matched_color FROM games WHERE white LIKE ? OR black LIKE ?", player, player, player, player)
    rand = random.randint(0, len(rows) - 1)
    id = rows[rand]['id']
    color = rows[rand]['matched_color']
    id = str(id)
    link = f"/play?id={id}&color={color}"
    return redirect(link)


@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    person = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    if request.method == "GET":
        id = int(request.args.get("id"))
        color = request.args.get("color")
        rows = gamesdb.execute("SELECT * FROM games WHERE id = ?", id)
        pgn = rows[0]['game']
        gameinfo = game_info(pgn, type = "text")
        data = random_fen_from_pgn(pgn, color,type = "text")
        fen = data[0]
        best_moves = analyze_position(fen, 20, 3)
        gmmove = data[1]['grandmaster_move']
        gmeval = data[1]['eval']
        color = data[2]
        date = gameinfo['date']
        white = gameinfo['white']
        black = gameinfo['black']
        result = gameinfo['result']
        event = gameinfo['event']
        whiteElo = gameinfo['whiteElo']
        blackElo = gameinfo['blackElo']
        date= date.replace('??', '01')
        date = datetime.strptime(date, "%Y.%m.%d")
        date = date.strftime("%Y %B %-d")
        return render_template("play.html", color = color,date = date,event = event, white = white, whiteElo = whiteElo, blackElo = blackElo, black = black, result = result, gmmove = gmmove, gmeval = gmeval, best_moves = best_moves, accountname = person[0]['username'], fen = fen, pgn = pgn)
    fen = request.form.get("fen")
    white = request.form.get("white")
    black = request.form.get("black")
    move = request.form.get("move")
    move = uci_to_algebraic(move, fen)
    gmmove = request.form.get("gmmove")
    gmeval = request.form.get("gmeval")
    best_moves = request.form.get("best_moves")
    best_moves = ast.literal_eval(best_moves)
    best_move = best_moves["best_move"]
    best_eval = best_moves["eval"]
    if len(best_moves) > 2:
        second_best = best_moves["second_best"]
        second_eval = best_moves["second_eval"]
    if len(best_moves) > 4:
        third_best = best_moves["third_best"]
        third_eval = best_moves["third_eval"]
    if gmmove == best_move:
        gmeval = best_eval
    if gmmove == second_best:
        gmeval = second_eval
    if gmmove == third_best:
        gmeval = third_eval
    evaldone = False
    if move == best_move:
        your_eval = best_eval
        evaldone = True
    if move == second_best:
        your_eval = second_eval
        evaldone = True
    if move == third_best:
        your_eval = third_eval
        evaldone = True
    if not evaldone == True:
        moveuci = user_input_to_uci(move, fen)
        board = chess.Board(fen)
        movetoplay = chess.Move.from_uci(moveuci)
        try:
            board.push(movetoplay)
        except AssertionError:
            return 
        fen_after_playermove = board.fen()
        playermovedata = analyze_position(fen_after_playermove, 20, 1)
        your_eval = playermovedata["eval"]
    isBlacksTurn = fen.split(' ')[1] == 'b'
    if isBlacksTurn == True:
        gm = black
    else:
        gm = white
    diff = float(best_eval) - float(your_eval)
    if diff < 0.20 and diff > -0.20:
        bgcolor = "#23A80D"
    elif diff < 0.40 and diff > -0.40:
        bgcolor = "#36EA19"
    elif diff < 0.60 and diff > -0.60:
        bgcolor = "#C6FF21" 
    elif diff < 1.00 and diff > -1.00:
        bgcolor = "#FCFF3E" 
    elif diff < 2.00 and diff > -2.00:
        bgcolor = "#FFAA00"  
    else:
        bgcolor = "#FF3200 "  
    return render_template("answer.html", accountname = person[0]['username'], move = move, your_eval = your_eval, gmmove = gmmove, gmeval = gmeval, gm = gm, best_move = best_move, best_eval = best_eval, second_best = second_best, second_eval = second_eval, third_best = third_best, third_eval = third_eval, fen = fen, bgcolor= bgcolor )

@app.route("/signin", methods=["GET", "POST"])
@limiter.limit("12 per day")
def signin():
    session.clear()
    if request.method == "GET":
        return render_template("signin.html")
    else:
        rows = db.execute("SELECT * FROM users")
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "" or password == "":
            return apology("Please type in your username and password", 400)
        if duplicateUsernameCheck(username, rows) == False:
            return apology("Invalid username or password", 400)
        person = db.execute("SELECT * FROM users WHERE username = ?", username)
        if check_password_hash(person[0]['hash'], password) == False:
            return apology("Invalid username or password", 400)
        session['user_id'] = person[0]['id']
        return render_template("message.html", message = "Welcome back (" + person[0]['username'] + ")!"
  , accountname = person[0]['username'])
        

@app.route("/signup", methods=["GET", "POST"])
@limiter.limit("10 per day")
def signup():
    session.clear()
    if request.method == "GET":
        return render_template("signup.html")
    else:
        username = request.form.get("newUsername")
        password = request.form.get("newPassword")
        confirm = request.form.get("confirm")
        if username == "" or password == "" or confirm == "":
            return apology("please fill in the form", 400)
        rows = db.execute("SELECT * FROM users")
        if duplicateUsernameCheck(username, rows) == True:
            return apology("Username unavailable", 400)
        if len(password) < 8:
            return apology("password too short")
        if password != confirm: 
            return apology("password did not match", 400)
        
        db.execute("INSERT INTO users(username, hash) VALUES(?,?)", username, generate_password_hash(password))
        person = db.execute("SELECT * FROM users WHERE username = ?", username)
        session['user_id'] = person[0]['id']
        return render_template("message.html", message = "Account successfully made!", accountname = person[0]['username'])
        
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/account")
@login_required
def account():
    person = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    return render_template("account.html", accountname = person[0]['username'])

@app.route("/changeusername", methods=["GET", "POST"])
@login_required
def changeusername():
    person = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    if request.method == "GET":
        return render_template("changeusername.html", accountname = person[0]['username'])
    else:
        newUsername = request.form.get("username")
        password = request.form.get("password")
        if newUsername == "" or password == "":
            return apology("Please Fill in the form", 400)
        rows = db.execute("SELECT * FROM users")
        if duplicateUsernameCheck(newUsername, rows) == True:
            return apology("Invalid username", 400)
        if check_password_hash(person[0]['hash'], password) == False:
            return apology("Incorrect Password", 400)
        db.execute("UPDATE users SET username = ? WHERE id = ?", newUsername, session['user_id'])
        message = "Username successfully changed to (" + newUsername + ")!"
        return render_template("message.html", message = message, accountname = person[0]['username'])

@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    person = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    if request.method == "GET":
        return render_template("changepassword.html", accountname = person[0]['username'])
    else:
        oldpassword = request.form.get("oldpassword")
        newpassword = request.form.get("newpassword")
        confirm = request.form.get("confirm")
        if oldpassword == "" or newpassword == "" or confirm == "":
            return apology("Please Fill in the form", 400)
        rows = db.execute("SELECT * FROM users")
        if newpassword != confirm:
            return apology("New password did not match Re-write", 400)
        if check_password_hash(person[0]['hash'], oldpassword) == False:
            return apology("Incorrect Password", 400)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(newpassword), session['user_id'])
        message = "Password successfully changed"
        return render_template("message.html", message = message, accountname = person[0]['username'])

@app.route("/deleteaccount", methods=["get", "post"])
@login_required
def deleteaccount():
    person = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    if request.method == "GET":
        return render_template("deleteaccount.html", accountname = person[0]['username'])
    else:
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if password == "" or confirm == "":
            return apology("Please fill in the form", 400)
        if password != confirm:
            return apology("Password did not match re-write", 400)
        if check_password_hash(person[0]['hash'], password) == False:
            return apology("Incorrect Password", 400)
        db.execute("DELETE FROM users WHERE id = ?", session['user_id'])
        session.clear()
        return render_template("message.html", message="Account successfuly deleted!")
            
@app.route("/about")
@login_required
def about():
    person = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    return render_template("about.html", accountname = person[0]['username'])

@app.route("/import", methods=["GET", "POST"])
@login_required
def importPGN():
    person = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    if request.method == "GET":
        return render_template("import.html", accountname = person[0]['username'] )
    pgn = request.form.get("import")
    color = request.form.get("color")
    if color == None:
        color = "white"

    gameinfo = game_info(pgn, type = "text")
    white = gameinfo['white']
    black = gameinfo['black']
    if white == "?" or black == "?":
        return apology("Invalid pgn")
    rows = gamesdb.execute("SELECT * FROM games WHERE game = ?", pgn)
    if len(rows) == 0:
        gamesdb.execute("INSERT INTO games(game,white,black) VALUES (?,?,?)", pgn, white, black)
        rows = gamesdb.execute("SELECT * FROM games WHERE game = ?", pgn)
    id = rows[0]["id"]
    link = f"/play?id={id}&color={color}"
    return redirect(link)

if __name__ == '__main__':
    app.run()