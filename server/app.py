from flask import Flask, request, jsonify, session, send_from_directory
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from config import ApplicationConfig
import models
from flask_session.__init__ import Session
import sqlite3
from uuid import uuid4
import bcrypt
import random
import re
import numpy as np

#Startup for flask
app=Flask(__name__)
app.config.from_object(ApplicationConfig)

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
server_session = Session(app)


dbPath = "../instance/db.sqlite3" # path to use to access db


#Functions


def checkIfHost(id, tblName): #Makes sure user is host of game before api requests
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {tblName}  WHERE gameSeed = 'Owner'")
    properId = cursor.fetchone()
    conn.commit()
    conn.close()
    if properId[0] != id: # checks if user is the owner of the game to see the host view
        return False
    return True

def makeNumberSequence():
    arr = np.arange(1,91,1) # array of numbers 1-90
    random.shuffle(arr)# random order
    stri = ""
    for num in arr:
        if num <10: # makes all numbers 2 digits long
            stri+= "0"
        stri+=str(num)#add to string to be stored
    return stri

def makeBingoCard():
    cardArr = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
    for i in range(len(cardArr)): 
        weights = [0,0,0,0,1,1,1,1,1] # Only 5 numbers in every column
        if i==2: # make sure 1 number in every column
            for k in range(len(cardArr[0])): #check for number in column
                count = 0
                for j in range(0,2):
                    count+= cardArr[j][k]
                if count ==0: # add number to column
                    cardArr[2][k] = 1
                    weights.pop()

        random.shuffle(weights) # shuffles remaining weights

        for j in range(len(cardArr[i])): # adds weight to cell if doesnt already have one
            if cardArr[i][j]== 0:
                if weights.pop()==1:
                    cardArr[i][j] =1
        
        grid = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]] # new grid for numbers
        for i in range(0,9):
            dup = []
            j= 0
            while j < 3:
                if i==0: # Only allow certain numbers in each column
                    rand = random.randint(i*10+1,i*10+9) # 1-9
                elif i == 8:
                    rand = random.randint(i*10,i*10+10) # 80-90
                else:
                    rand = random.randint(i*10,i*10+9) #rest of columns
                if dup.count((rand)) == 0: # checks if number already exists in 
                    dup.append((rand))
                    j+=1
            dup.sort() # sorts so in order
            for k in range(0,3):
                grid[k][i] = dup[k] # adds to new grid
    
    cardStr = ""
    for i in range(0,27):
        cardArr[i%3][i//3] = cardArr[i%3][i//3] * grid[i%3][i//3] # multiplies the grid by the weights to remove values without a weight on 
        cardStr+= (cardArr[i%3][i//3].__str__()+"|") # adds to string in format to be stored by database

    return cardStr


#General features


@app.route("/@me")
def get_current_user(): # home page info to see which user
    id = session.get("user_id")

    if not id:
        return jsonify({"error":"unauthorised"}), 401
    
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT email, userName FROM users WHERE id = '{id}'")
    ret = cursor.fetchall()
    email = ret[0][0]
    userName = ret[0][1]
    return jsonify({
        "id":id,
        "email": email,
        "userName": userName
    })

@app.route("/register", methods =["POST"])
def register_user():
    email= request.json["email"]
    password = request.json["password"]
    userName = request.json["userName"]
    id = str(uuid4().hex)

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email): # checks if valid email
        return jsonify({"error": "Invalid Email"}),409
    
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM users WHERE email = '{email}'") 
    if cursor.fetchone() != None: # checks if user exists
        return jsonify({"error": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    session["user_id"] = id
    cursor.execute(f"INSERT INTO users VALUES('{id}','{email}','{hashed_password}','{userName}',0)")#adds new user to db
    conn.commit()
    conn.close()
    return jsonify({
        "id":id,
        "email":email
    })

@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"] #Get login info from user

    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, password FROM users WHERE email = '{email}'")
    ret = cursor.fetchall()
    id = ret[0][0]
    passwordSto = ret[0][1]
    if passwordSto is None: # stop crash in next hashing
        return jsonify({"error": "Unauthorised"}), 400
    
    if not bcrypt.check_password_hash(passwordSto, password): # checks if passwords are equal
        return jsonify({"error": "Unauthorised"}), 401
    
    session["user_id"] = id
    session.modified = True
    return jsonify({
        "id":id,
        "email":email
    }),200

@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return "200"


#Host Features


@app.route("/host/makeRoomCode")
def game_startup():
    user_id = session.get("user_id")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT roomCode FROM games")#room code is a string so cannot use max
    ret = cursor.fetchall()
    roomCode = 1
    for i in ret:
        if int(i[0])>roomCode: # convert room code to int
            roomCode = int(i[0])
    roomCode+=1 # new roomcode
    tblName = "room"+str(roomCode)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {tblName} (id varchar(32) REFERENCES users(id) PRIMARY KEY UNIQUE,gameSeed varChar(32), score INTEGER)")# new table for the game
    numberSeq = makeNumberSequence()
    try:
        cursor.execute(f"INSERT INTO {tblName} VALUES('{user_id}','Owner',0)") # adds owner
    except:
        app.logger.info("Failed To Add Owner")
    try:
        cursor.execute(f"INSERT INTO games VALUES('{roomCode}','{numberSeq}',0,0,'l','')") # adds values into games table
    except():
        app.logger.info("Failed To Add To Games") 
    conn.commit()
    conn.close()
    return jsonify({
        "roomCode":roomCode
    })

@app.route("/host/game/<roomCode>/begin",methods = ["POST"])
def beginGame(roomCode):
    id = session.get("user_id")
    tblName = "room"+roomCode
    if (not checkIfHost(id,tblName)):
        return "not authed",200
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE GAMES SET began = 1 WHERE roomCode = '{roomCode}'")
    conn.commit()
    conn.close()
    return "",200

@app.route("/host/lobby/<roomCode>/getPlayers", methods=["POST"])
def getPlayers(roomCode):
    id = session.get("user_id")
    tblName = "room"+roomCode
    if (not checkIfHost(id,tblName)):
        return "not authed",200
    conn =sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT userName FROM {tblName} FULL JOIN users USING(id) WHERE gameSeed != 'Owner' ") # gets all players for the lobby
    playerNames = cursor.fetchall()
    conn.commit()
    conn.close()
    str= ""
    for names in playerNames:
         str += names[0]+" "
    return jsonify({"names":str}),200

@app.route("/host/game/<roomCode>/call", methods=["POST"])
def callNumber(roomCode):
    id = session.get("user_id")
    tblName = "room"+roomCode
    if (not checkIfHost(id,tblName)):
        return "not authed",200
    callNum = []
    conn =sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT gameSequence,depth FROM games WHERE roomCode=='{roomCode}'")
    ret = cursor.fetchone()
    callSeq = str(ret[0])
    depth = int(ret[1])
    for i in range (0,5): # gets 5 previous numbers 
        if depth - i >0: # only looks allows positive values
            callNum.append(callSeq[(depth-i)*2:(depth-i)*2+2])
    cursor.execute(f"UPDATE games SET depth = {depth+1}, winnerID = '' WHERE roomCode=={roomCode}") # stores next number has been called

    cursor.execute(f"SELECT users.userName, {tblName}.score FROM users INNER JOIN {tblName} ON users.id = {tblName}.id  WHERE {tblName}.gameSeed != 'Owner' ORDER BY {tblName}.score DESC") # Leader board in order
    leaderBoard = cursor.fetchall()

    conn.commit()
    conn.close()
    return jsonify({"numbers":callNum , "leaderboard":leaderBoard}),200

@app.route("/host/game/<roomCode>/endGame", methods=["POST"])
def endGame(roomCode):
    id = session.get("user_id")
    tblName = "room"+roomCode
    if (not checkIfHost(id,tblName)):
        return "not authed",200
    conn =sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE {tblName}") # removes game table
    cursor.execute(f"DELETE FROM games WHERE roomCode = '{roomCode}'") # removes record from games
    conn.commit()
    conn.close()
    return "0",200

@app.route("/host/game/<roomCode>/checkWinner",methods=["POST"])
def checkWinner(roomCode):
    id = session.get("user_id")
    tblName = "room"+roomCode
    if (not checkIfHost(id,tblName)):
        return "not authed",200
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT users.userName, users.id from users INNER JOIN games ON users.id=games.winnerID WHERE games.roomCode = '{roomCode}'") 
    w = cursor.fetchone()
    if w == None or w == '': # checks if someone has won or not
        return jsonify({"winner":""})
    winner = w[0]
    tid = w[1]

    cursor.execute(f"UPDATE users SET score=score+1 WHERE id = '{tid}'") # updates players score
    conn.commit()
    conn.close()
    return jsonify({"winner":winner})

@app.route("/host/game/<roomCode>/backToGame",methods=["POST"])
def backToGame(roomCode):
    id = session.get("user_id")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE games SET winnerID='' WHERE roomCode='{roomCode}'") # refreshes winner id so empty
    conn.commit()
    conn.close()
    
    return "",200

@app.route("/host/game/<roomCode>/checkHost", methods = ["POST"])
def checkHost(roomCode):
    tblName = "room"+roomCode
    id = session.get("user_id")
    if not checkIfHost(id,tblName): # checks if user is the owner of the game to see the host view
        return "Not Authed", 201
    return "",200


#Player Features


@app.route("/player/game/<roomCode>/checkBingo", methods=["POST"])
def checkBingo(roomCode):
    states = request.json["states"]
    id = session.get("user_id")
    tblName = "room"+roomCode
    if (not checkIfHost(id,tblName)):
        return "not authed",200
    row = -1

    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor() 
    cursor.execute(f"SELECT gameSequence, depth, winCon FROM games WHERE roomCode = '{roomCode}'")
    ret = cursor.fetchone()
    gameSequence = ret[0]
    depth = ret[1]
    winCon = ret[2]
    validNumbers = (re.findall('..',gameSequence))[:depth] # seperates nubers into strings of 2
    validInts = []
    for x in validNumbers: # changes to integers
        validInts.append(int(x))

    for i in range(0,3): # finds the row that bingo has been called on
        if states[i*9:(i+1)*9] == [True,True,True,True,True,True,True,True,True]:
            row = i

    arr =[[],[],[]]
    cursor.execute(f"SELECT gameSeed FROM {tblName} WHERE id = '{id}'")
    cardStr = cursor.fetchone()[0]
    cardarr = cardStr.split("|") # parses gamesequence
    
    for i in range(0,26):
        if cardarr[i]!="0":
            arr[i%3].append(int(cardarr[i])) # only adds actual numbers
    totalCard = arr[0]+arr[1]+arr[2] # needed for house calls
    
    if winCon =='l' and set(arr[row])<=set(validInts): # checks if the numbers on the line is a subset of valid numbers
        conn.execute(f"UPDATE games SET winCon ='h', winnerID = '{id}' WHERE roomCode = '{roomCode}'") # updates table so no more lines can be called
    elif winCon == 'h' and set(totalCard)<=set(validInts) and all(states): # checks if the all numbers is a subset of valid numbers
        conn.execute(f"UPDATE games SET winCon ='d', winnerID = '{id}' WHERE roomCode = '{roomCode}'") # updates table so no more bingos can be called 
    
    conn.commit()
    conn.close()
    return "",200

@app.route("/player/game/<roomCode>",methods = ["POST"])
def joinLobby(roomCode):
    id = session.get("user_id")
    gameSeed = makeBingoCard()
    tblName = "room"+roomCode
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT EXISTS(SELECT name FROM sqlite_master WHERE type = 'table' AND name = '{tblName}')") #checks if game table exists
    exists = cursor.fetchall()
    
    if exists[0][0] == 0: # ends if doesnt exists
        return "0",201
    
    try:
        cursor.execute(f"INSERT INTO {tblName} VALUES('{id}','{gameSeed}',0)")
    except:
        app.logger.info("Join Game In DB failed")
    conn.commit()
    conn.close()
    return jsonify({"card":gameSeed}),200 # returns gameseed for card

@app.route("/player/game/<roomCode>/checkScore",methods = ["POST"])
def checkScore(roomCode):
    score = request.json["states"].count(True) -12
    tblName = "room"+roomCode
    id = session.get("user_id")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {tblName} SET SCORE = {score} WHERE id = '{id}'") # updates user scores on click for leaderboard 
    conn.commit()
    conn.close()
    return "",200


#Club Features


@app.route("/clubs/createClub",methods = ["POST"])
def createClub():
    id = session.get("user_id")
    clubName = request.json["clubName"]
    clubDesc = request.json["clubDesc"]
    password = request.json["password"]

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') # hashes password

    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT clubId FROM clubs")

    ret = cursor.fetchall()

    newId = 1
    for i in ret:
        if int(i[0])>newId: # convert club id to int
            newId = int(i[0])
    newId+=1 # new club id

    cursor.execute(f"INSERT INTO clubs VALUES('{newId}', '{id}', '{clubName}','{clubDesc}','{hashed_password}')")
    cursor.execute(f"INSERT INTO userToClub VALUES('{id}','{newId}')")
    conn.commit()
    conn.close()
    return "",200

@app.route("/clubs/joinClub", methods = ["POST"])
def joinClub():
    id = session.get("user_id")
    clubId = request.json["clubId"]
    password = request.json["password"]

    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT password FROM clubs WHERE clubId = '{clubId}'")
    passwordSto = cursor.fetchone()[0]

    if not bcrypt.check_password_hash(passwordSto, password): # check if correct password
        return jsonify({"error": "Unauthorised"}), 401 
    
    cursor.execute(f"""INSERT OR IGNORE INTO userToClub VALUES('{id}','{clubId}') """) # Make sure only unique values so no duplicate club joins
    conn.commit()
    conn.close()
    return "",200

@app.route("/clubs/getClubs", methods = ["POST"])
def getPlayerClubs():
    id = session.get("user_id")
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"""SELECT name, clubs.clubId 
                   FROM clubs 
                   INNER JOIN userToClub ON clubs.clubId = userToClub.clubId
                   WHERE userToClub.userId = '{id}'""")
    arr = cursor.fetchall()
    conn.commit()
    conn.close()
    return jsonify({"Clubs": arr}),200

@app.route("/clubs/clubLeaderboard",methods = ["POST"])
def getLeaderBoard():
    id = session.get("user_id")
    clubId = request.json["clubId"]
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"""SELECT users.username, users.score,users.id 
                   FROM users 
                   INNER JOIN userToClub ON users.id = userToClub.userId
                   WHERE userToClub.clubId = '{clubId}'
                   ORDER BY users.score DESC
                    """) # get all user info from club in order of score
    
    arr = cursor.fetchall()
    cursor.execute(f"SELECT name , desc FROM clubs WHERE clubId = '{clubId}'") #get club info
    n = cursor.fetchone()
    cursor.execute(f"SELECT owner FROM clubs WHERE clubId = '{clubId}'") # find owner of club
    perms = id == cursor.fetchone()[0] # check if user id is owner and set perms
    conn.commit()
    conn.close()

    return jsonify({"Leaderboard":arr,"Name":n[0],"Desc":n[1],"Perms":perms}),200

@app.route("/clubs/kickFromClub",methods = ["POST"])
def kickFromClub():
    id = session.get("user_id")
    clubId = request.json["clubId"]
    kickedId = request.json["userId"]
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT owner FROM clubs WHERE clubId = '{clubId}'")
    owner =cursor.fetchone()[0]
    if  owner != id or kickedId == owner: # checks if request is coming from the owner
        return "Not Authed",200
    cursor.execute(f"DELETE FROM userToClub WHERE userId = '{kickedId}' and clubId = '{clubId}'")
    conn.commit()
    conn.close()
    return "",200

@app.route("/clubs/deleteClub",methods = ["POST"])
def deleteClub():
    id = session.get("user_id")
    clubId = request.json["clubId"]
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    cursor.execute(f"SELECT owner FROM clubs WHERE clubId = '{clubId}'")
    owner =cursor.fetchone()[0]
    if  owner != id: # checks if request is coming from the owner
        return "Not Authed",200
    app.logger.info("Deleting "+clubId)
    cursor.execute(f"DELETE FROM clubs WHERE clubId ='{clubId}'")
    cursor.execute(f"DELETE FROM userToClub WHERE clubId = '{clubId}'")
    conn.commit()
    conn.close()
    return "",200


if __name__ == "__main__":
    app.run(host ='localhost',port=5000,debug=True)

