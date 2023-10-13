# GrandmasterMoves

## Video Demo: Url

## Table of Contents 

- [Introduction](#1-introduction)
- [Description](#2-description)
- [Usage](#3-usage)
- [Future of the project](#4-future-of-the-project)
- [License](#5-license)
- [Credits](#6-credits)

## 1. Introduction

Hello, world! This is a relatively new programmer's first real project. I made this web app because I think it fills a space. Unfortunately While it is completely functional, it is not ready to deploy (for reasons why go to [Future of the project](#4-future-of-the-project)). Nevertheless, I'm Incredibly proud of myself both for finishing my online computer science course (CS50x) and for finishing this project. 

## 2. Description
Video demo: url
### Main
![the index page, a list of grandmasters and a link to an import page](https://github.com/dahat64/GMmoves/static/readmeimages/index.jpg?raw=true)
This is a flask web app. It's a chess trainer by showing the user positions of grandmaster games and the user guessing the best move of the position.

The home page of the website is a list of grandmasters dynamically loaded from a txt file so that more grandmasters can be added to it at any time. There's also an import function for the user to be able to import a game themself.

After choosing a grandmaster or importing a game the user will be redirected to a random position from the game using a function I coded called (random_fen_from_pgn). 

In that page The user can copy the FEN(a representation of a chess position). They can also copy the PGN(a whole game of chess including info about the players and the event etc).

After making your move, You will be shown:<br>
1- How your move evaluates.<br>
2- What the grandmaster played and How their move evaluates.<br>
3- The best move according to the engine(stockfish).<br>

From this answers page the user can go to a different game by the same grandmaster or go back to the list of grandmasters.

### Account and Session
The app uses  the Flask-Session library for session features.
There is also an account page where the user can do these three things:<br>
1- Change their Username<br>
2- Change their Password<br>
3- Delete their Account

## 3. Usage
1- Download the source code at: https://github.com/dahat64/GMmoves<br>
2- IMPORTANT! Download these two files manually: "users.db" and "pgn.db" from the repository and add them to the same folder to replace the old ones!<br>
3- Open the folder using a code editor like VSCODE.<br>
4- Install python.<br>
5- Use the commands to install the necessary packages:<br>
```
pip install flask
pip install flask_session
pip install cs50
pip install chess
pip install flask_limiter
```
6- Run the app using one of these commands:<br>
```
python app.py

flask --app app run
```



## 4. Future of the project

The app needs more work before being ready to deploy mainly:

### The chess evaluation to be done by JS
This is the most important step left in the project.<br>right now the chess evaluation is done in the backend so the user has to wait 5-10 seconds before they can see the position.<br> If the chess evaluation was done in Javascript the user can be shows the position while the evaluation is being done. I am not at all proficient in Javascript and it would take months for me to implement this. I will come back in the future when i'm more comfortable in Javascript.<br>

Note: this problem can probably be fixed even without transfering the chess evaluation to Javascript. I just don't know any way to do it. And to be honest I've already worked way too long on this project and I have to move on at somepoint.

### A search feature
I've already loaded ≈90,000 games to the database.<br>
A search feature for this database would take the app to the next level.

### Responsiveness
The web app is not responsive And only works on desktop due to my lacking skills in web development.

## 5. License
Feel free to take any part of the code you need. 

## 6. Credits
### CS50x
First and foremost, the amazing CS50x staff, for teaching me all I know so far about programming. Thanks professor David J. Malan for being awesome. Thanks Harvard for providing an amazing course for free.

### pgnmentor.com
### Chess.js

### Chessboard.js

### Stockfish chess engine
### ChatGpt
