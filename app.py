from flask import Flask, request, redirect, session, render_template
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import apology, login_required, duplicateUsernameCheck

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///users.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    person = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])
    return render_template("index.html", accountname = person[0]['username'])

@app.route("/signin", methods=["GET", "POST"])
def login():
    session.clear()
    rows = db.execute("SELECT * FROM users")
    if request.method == "GET":
        return render_template("signin.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "" or password == "":
            return apology("Please type in your username and password", 400)
        if duplicateUsernameCheck(username, rows) == False:
            return apology("Username not in database", 400)
        person = db.execute("SELECT * FROM users WHERE username = ?", username)
        if check_password_hash(person[0]['hash'], password) == False:
            return apology("Incorrect Password", 400)
        session['user_id'] = person[0]['id']
        return render_template("message.html", message = "Welcome back ", message2=person[0]['username'], accountname = person[0]['username'])
        

@app.route("/signup", methods=["GET", "POST"])
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
            return apology("Username already taken", 400)
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
