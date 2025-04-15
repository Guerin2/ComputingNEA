from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from config import ApplicationConfig
from models import db, User
from flask_session.__init__ import Session
import sqlite3
from uuid import uuid4
import bcrypt
import random
import re
import numpy as np


app=Flask(__name__)
app.config.from_object(ApplicationConfig)

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
server_session = Session(app)

dbPath = "../instance/db.sqlite3"

@app.route("/@me")
def get_current_user():
    id = session.get("user_id")

    if not id:
        return jsonify({"error":"unauthorised"}), 401
    
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT email FROM users WHERE id = '{id}'")
    ret = cursor.fetchall()
    email = ret[0][0]
    return jsonify({
        "id":id,
        "email": email
    })

@app.route("/register", methods =["POST"])
def register_user():
    email= request.json["email"]
    password = request.json["password"]
    userName = request.json["userName"]
    id = str(uuid4().hex)

    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()

    #return jsonify({"error": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    session["user_id"] = id
    cursor.execute(f"INSERT INTO users VALUES('{id}','{email}','{hashed_password}','{userName}',0)")
    conn.commit()
    conn.close()
    return jsonify({
        "id":id,
        "email":email
    })

@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"]

    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, password FROM users WHERE email = '{email}'")
    ret = cursor.fetchall()
    id = ret[0][0]
    passwordSto = ret[0][1]
    app.logger.info("---------------------------------------------------------------------",ret)
    if passwordSto is None:
        return jsonify({"error": "Unauthorised"}), 400
    
    if not bcrypt.check_password_hash(passwordSto, password):
        return jsonify({"error": "Unauthorised"}), 401
    
    session["user_id"] = id
    
    return jsonify({
        "id":id,
        "email":email
    }),200

@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return "200"

@app.route("/host/makeRoomCode")
def game_startup():
    app.logger.info("game startup")
    user_id = session.get("user_id")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT roomCode FROM games")
    ret = cursor.fetchall()
    roomCode = 1
    for i in ret:
        if int(i[0])>roomCode:
            roomCode = int(i[0])
    roomCode+=1
    print(roomCode)
    tblName = "room"+str(roomCode)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {tblName} (id varchar(32) REFERENCES users(id) PRIMARY KEY UNIQUE,gameSeed varChar(32), score INTEGER)")
    numberSeq = makeNumberSequence()
    app.logger.info("game startup")
    try:
        cursor.execute(f"INSERT INTO {tblName} VALUES('{user_id}','Owner',0)")
    except:
        app.logger.info("Failed To Add Owner")
    try:
        cursor.execute(f"INSERT INTO games VALUES('{roomCode}','{numberSeq}',0,0,'l','')")
    except():
        app.logger.info("Failed To Add To Games") 
    conn.commit()
    conn.close()
    return jsonify({
        "roomCode":roomCode
    })

def makeNumberSequence():
    arr = np.arange(1,91,1)
    random.shuffle(arr)
    stri = ""
    for num in arr:
        if num <10:
            stri+= "0"
        stri+=str(num)
    return stri
        
@app.route("/player/game/<roomCode>",methods = ["POST"])
def joinLobby(roomCode):
    id = session.get("user_id")
    gameSeed = makeBingoCard()
    tblName = "room"+roomCode
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = 'table' AND name = '{tblName}')")
    exists = cursor.fetchall()
    
    if exists[0][0] == 0:
        return "0",201
    
    
    try:
        cursor.execute(f"INSERT INTO {tblName} VALUES('{id}','{gameSeed}',0)")
    except:
        app.logger.info("Join Game In DB failed")

    cursor.execute(f"SELECT gameseed FROM {tblName} WHERE id = '{id}'")
    ret = cursor.fetchone()
    conn.commit()
    conn.close()
    return jsonify({"card":ret[0]}),200

@app.route("/host/game/<roomCode>/begin",methods = ["POST"])
def beginGame(roomCode):
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE GAMES SET began = 1 WHERE roomCode = '{roomCode}'")
    conn.commit()
    conn.close()
    return "",200

@app.route("/host/lobby/<roomCode>/getPlayers", methods=["POST"])
def getPlayers(roomCode):
    tblName = "room"+roomCode
    conn =sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT userName FROM {tblName} FULL JOIN users USING(id) WHERE gameSeed != 'Owner' ")
    playerNames = cursor.fetchall()
    conn.commit()
    conn.close()
    str= ""
    for names in playerNames:
         str += names[0]+" "
    return jsonify({"names":str}),200

@app.route("/host/game/<roomCode>/call", methods=["POST"])
def callNumber(roomCode):
    tblName = "room"+roomCode
    callNum = []
    conn =sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT gameSequence,depth FROM games WHERE roomCode=='{roomCode}'")
    ret = cursor.fetchone()
    callSeq = str(ret[0])
    depth = int(ret[1])
    for i in range (0,5):
        if depth - i >0:
            callNum.append(callSeq[(depth-i)*2:(depth-i)*2+2])
    cursor.execute(f"UPDATE games SET depth = {depth+1}, winnerID = '' WHERE roomCode=={roomCode}")

    cursor.execute(f"SELECT users.userName, {tblName}.score FROM users INNER JOIN {tblName} ON users.id = {tblName}.id  WHERE {tblName}.gameSeed != 'Owner' ORDER BY {tblName}.score DESC")
    leaderBoard = cursor.fetchall()

    
    conn.commit()
    conn.close()
    return jsonify({"numbers":callNum , "leaderboard":leaderBoard}),200

@app.route("/host/game/<roomCode>/endGame", methods=["POST"])
def endGame(roomCode):
    tblName = "room"+roomCode
    conn =sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE {tblName}")
    cursor.execute(f"DELETE FROM games WHERE roomCode = '{roomCode}'")
    conn.commit()
    conn.close()
    return "0",200

def makeBingoCard():
    cardArr = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
    for i in range(len(cardArr)): 
        weights = [0,0,0,0,1,1,1,1,1]
        if i==2:
            for k in range(len(cardArr[0])):
                count = 0
                for j in range(0,2):
                    count+= cardArr[j][k]
                if count ==0:
                    cardArr[2][k] = 1
                    weights.pop()

        random.shuffle(weights)

        for j in range(len(cardArr[i])):
            if cardArr[i][j]== 0:
                if weights.pop()==1:
                    cardArr[i][j] =1
        
        grid = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]] 
        for i in range(0,9):
            dup = []
            j= 0
            while j < 3:
                rand = random.randint(i*10+1,i*10+10)
                if dup.count((rand)) == 0:
                    dup.append((rand))
                    j+=1
            dup.sort()
            for k in range(0,3):
                grid[k][i] = dup[k]
    
    cardStr = ""
    for i in range(0,27):
        cardArr[i%3][i//3] = cardArr[i%3][i//3] * grid[i%3][i//3] 
        cardStr+= (cardArr[i%3][i//3].__str__()+"|")

    return cardStr

@app.route("/<roomCode>/checkBingo", methods=["POST"])
def checkBingo(roomCode):
    states = request.json["states"]
    id = session.get("user_id")
    tblName = "room"+roomCode
    row = -1

    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor() 
    cursor.execute(f"SELECT gameSequence, depth, winCon FROM games WHERE roomCode = '{roomCode}'")
    ret = cursor.fetchone()
    gameSequence = ret[0]
    depth = ret[1]
    winCon = ret[2]
    validNumbers = (re.findall('..',gameSequence))[:depth]
    validInts = []
    for x in validNumbers:
        validInts.append(int(x))

    for i in range(0,3):
        if states[i*9:(i+1)*9] == [True,True,True,True,True,True,True,True,True]:
            app.logger.info(states[i*9:(i+1)*9])
            row = i


    arr =[[],[],[]]
    cursor.execute(f"SELECT gameSeed FROM {tblName} WHERE id = '{id}'")
    cardStr = cursor.fetchone()[0]
    cardarr = cardStr.split("|")
    
    for i in range(0,26):
        if cardarr[i]!="0":
            arr[i%3].append(int(cardarr[i]))
    totalCard = arr[0]+arr[1]+arr[2]
    
    if winCon =='l':
        app.logger.info("hello")
        bingo = set(arr[row])<=set(validInts)
        app.logger.info(arr[row])
        if bingo:
            conn.execute(f"UPDATE games SET winCon ='h', winnerID = '{id}' WHERE roomCode = '{roomCode}'")
    else:
        bingo = set(totalCard)<=set(validInts)
        if bingo:
            conn.execute(f"UPDATE games SET winCon ='d', winnerID = '{id}' WHERE roomCode = '{roomCode}'")
    app.logger.info(winCon)
    app.logger.info(sorted(validNumbers))
    app.logger.info(bingo)
    conn.commit()
    conn.close()
    return "",200

@app.route("/<roomCode>/checkWinner",methods=["POST"])
def checkWinner(roomCode):
    id = session.get("user_id")
    tblName = "room"+roomCode
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT users.userName, users.id from users INNER JOIN games ON users.id=games.winnerID WHERE games.roomCode = '{roomCode}'") 
    w = cursor.fetchone()
    if w == None:
        return jsonify({"winner":""})
    winner = w[0]
    tid = w[1]

    cursor.execute(f"UPDATE users SET score=score+1 WHERE id = '{tid}'")
    conn.commit()
    conn.close()
    app.logger.info(winner)
    app.logger.info(tid)
    return jsonify({"winner":winner})

@app.route("/<roomCode>/backToGame",methods=["POST"])
def backToGame(roomCode):
    id = session.get("user_id")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE games SET winnerID='' WHERE roomCode='{roomCode}'")
    cursor.execute(f"SELECT winCon FROM games WHERE roomCode = '{roomCode}'")
    winCon = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    
    return "",200

@app.route("/createClub",methods = ["POST"])
def createClub():
    id = session.get("user_id")
    clubName = request.json["clubName"]
    clubDesc = request.json["clubDesc"]
    password = request.json["password"]

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT MAX(clubId) FROM clubs")
    newId = str(int(cursor.fetchone()[0])+1)
    cursor.execute(f"INSERT INTO clubs VALUES('{newId}', '{id}', '{clubName}','{clubDesc}','{hashed_password}')")
    cursor.execute(f"INSERT INTO userToClub VALUES('{id}','{newId}')")
    conn.commit()
    conn.close()
    return "balls",200

@app.route("/joinClub", methods = ["POST"])
def joinClub():
    id = session.get("user_id")
    clubId = request.json["clubId"]
    password = request.json["password"]

    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT password FROM clubs WHERE clubId = '{clubId}'")
    passwordSto = cursor.fetchone()[0]

    if not bcrypt.check_password_hash(passwordSto, password):
        return jsonify({"error": "Unauthorised"}), 401
    
    cursor.execute(f"INSERT INTO userToClub VALUES ('{id}','{clubId}')") # Make only unique values
    conn.commit()
    conn.close()
    return "balls",200


@app.route("/getClubs", methods = ["POST"])
def getPlayerClubs():
    id = session.get("user_id")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"""SELECT name, clubs.clubId 
                   FROM clubs 
                   FULL OUTER JOIN userToClub ON clubs.clubId = userToClub.clubId
                   WHERE userToClub.userId = '{id}'""")
    arr = cursor.fetchall()
    conn.commit()
    conn.close()

    app.logger.info(arr)
    return jsonify({"Clubs": arr}),200

@app.route("/clubLeaderboard/<clubId>",methods = ["POST"])
def getLeaderBoard(clubId):
    id = session.get("user_id")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"""SELECT users.username, users.score 
                   FROM users 
                   FULL OUTER JOIN userToClub ON users.id = userToClub.userId
                   WHERE userToClub.clubId = '{clubId}'
                   ORDER BY users.score DESC
                                      """)
    
    arr = cursor.fetchall()

    cursor.execute(f"SELECT name FROM clubs WHERE clubId = '{clubId}'")
    n = cursor.fetchone()
    conn.commit()
    conn.close()

    return jsonify({"Leaderboard":arr,"Name":n}),200


@app.route("/host/game/<roomCode>/checkHost", methods = ["POST"])
def checkHost(roomCode):
    tblName = "room"+roomCode
    id = session.get("user_id")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {tblName}  WHERE gameSeed = 'Owner'")
    properId = cursor.fetchone()
    conn.commit()
    conn.close()
    if properId[0] != id:
        return "Not Authed", 201
    return "",200
    
@app.route("/player/game/<roomCode>/checkScore",methods = ["POST"])
def checkScore(roomCode):
    score = request.json["states"].count(True) -12
    tblName = "room"+roomCode
    id = session.get("user_id")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {tblName} SET SCORE = {score} WHERE id = '{id}'")
    conn.commit()
    conn.close()
    return "",200




if __name__ == "__main__":
    app.run(debug=True)



