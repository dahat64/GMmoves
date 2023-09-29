from flask import Flask, request, redirect, session, render_template, jsonify
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import apology, login_required, duplicateUsernameCheck, analyze_position, random_fen_from_pgn, game_info, user_input_to_uci
from flask_limiter import Limiter
from datetime import datetime
import threading

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
    if request.method == "GET":
        return render_template("index.html")


@app.route("/play", methods=["GET", "POST"])
@login_required
def play():
    if request.method == "GET":
        person = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
        pgn = 'ct-2750-2864-2023.5.9.pgn'
        data = random_fen_from_pgn(pgn)
        fen = data[0]
        best_move = analyze_position(fen, 20, 3)
        gmmove = data[1]
        color = data[2]
        gameinfo = game_info(pgn)
        date = gameinfo['date']
        white = gameinfo['white']
        black = gameinfo['black']
        result = gameinfo['result']
        event = gameinfo['event']
        date = datetime.strptime(date, "%Y.%m.%d")
        date = date.strftime("%Y %B %-d" + "th")
        return render_template("play.html", color = color,date = date,event = event, white = white, black = black, result = result, accountname = person[0]['username'], fen = fen)
    fen = request.form.get("fen")
    move = request.form.get("move")
    move = user_input_to_uci(move, fen)
    print(f"move is {move} aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaskldjf")
    return str(move)

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


if __name__ == '__main__':
    app.run()