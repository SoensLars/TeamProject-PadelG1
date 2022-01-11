from RPi import GPIO
from subprocess import check_output, call 
import time
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit, send
from flask_cors import CORS
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False, ping_timeout=1)
CORS(app)

knop1up = 26
knop1down = 19

knop2up = 21
knop2down = 20

PointsTeam1 = 0
PointsTeam2 = 0

GamesTeam1 = 0
GamesTeam2 = 0

GamesTeam1Set1 = 0
GamesTeam1Set2 = 0
GamesTeam1Set3 = 0

GamesTeam2Set1 = 0
GamesTeam2Set2 = 0
GamesTeam2Set3 = 0

Set = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup((knop1up, knop1down, knop2up, knop2down), GPIO.IN, pull_up_down=GPIO.PUD_UP)

def points_team1_up():
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, GamesTeam1Set1, GamesTeam1Set2, GamesTeam1Set3, GamesTeam2Set1, GamesTeam2Set2, GamesTeam2Set3, Set
    if GamesTeam1 < 6:
        if PointsTeam1 == 0 or PointsTeam1 == 15:
                PointsTeam1 += 15
        elif PointsTeam1 == 30:
                PointsTeam1 += 10
        elif PointsTeam1 == 40:
            if PointsTeam2 != 40:
                PointsTeam1 = 0
                PointsTeam2 = 0
                GamesTeam1 += 1
                if Set == 0:
                    GamesTeam1Set1 += 1
                elif Set == 1:
                    GamesTeam1Set2 += 1
                elif Set == 2:
                    GamesTeam1Set3 += 1                
            else:
                PointsTeam1 = "AD"
                PointsTeam2 = "-"
        elif PointsTeam1 == "AD":
            PointsTeam1 = 0
            PointsTeam2 = 0
            GamesTeam1 += 1
            if Set == 0:
                GamesTeam1Set1 += 1
            elif Set == 1:
                GamesTeam1Set2 += 1
            elif Set == 2:
                GamesTeam1Set3 += 1  
        elif PointsTeam2 == "AD":
            PointsTeam1 = 40
            PointsTeam2 = 40
    elif GamesTeam1 == 6 and GamesTeam2 <= 4:
        if PointsTeam1 == 0 or PointsTeam1 == 15:
                PointsTeam1 += 15
        elif PointsTeam1 == 30:
                PointsTeam1 += 10
        elif PointsTeam1 == 40:
            if PointsTeam2 != 40:
                PointsTeam1 = 0
                PointsTeam2 = 0
                GamesTeam1 = 0
                GamesTeam2 = 0
                Set += 1
                if Set == 0:
                    GamesTeam1Set1 += 1
                elif Set == 1:
                    GamesTeam1Set2 += 1
                elif Set == 2:
                    GamesTeam1Set3 += 1 
            else:
                PointsTeam1 = "AD"
                PointsTeam2 = "-"
        elif PointsTeam1 == "AD":
            PointsTeam1 = 0
            PointsTeam2 = 0
            GamesTeam1  = 0
            GamesTeam2 = 0
            Set += 1
            if Set == 0:
                GamesTeam1Set1 += 1
            elif Set == 1:
                GamesTeam1Set2 += 1
            elif Set == 2:
                GamesTeam1Set3 += 1 
        elif PointsTeam2 == "AD":
            PointsTeam1 = 40
            PointsTeam2 = 40

    socketio.emit('B2F_points_team1', {'sets': Set, 'currentGames': GamesTeam1, 'gamesSet1': GamesTeam1Set1, 'gamesSet2': GamesTeam1Set2, 'gamesSet3': GamesTeam1Set3 ,'points': PointsTeam1})    
    socketio.emit('B2F_points_team2', {'sets': Set, 'currentGames': GamesTeam2, 'gamesSet1': GamesTeam2Set1, 'gamesSet2': GamesTeam2Set2, 'gamesSet3': GamesTeam2Set3, 'points': PointsTeam2})
    # print(f"'sets': {SetsTeam1}, 'currentGames': {GamesTeam1}, 'gamesSet1': {GamesTeam1Set1}, 'gamesSet2': {GamesTeam1Set2}, 'gamesSet3': {GamesTeam1Set3} ,'points': {PointsTeam1}")
    print(f"Team1\t\tSets: {Set}\t\tGames: {GamesTeam1}\tPoints: {PointsTeam1}")
    print(f"Team2\t\tSets: {Set}\t\tGames: {GamesTeam2}\tPoints: {PointsTeam2}")  
    print(f"") 

def points_team2_up():
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, GamesTeam1Set1, GamesTeam1Set2, GamesTeam1Set3, GamesTeam2Set1, GamesTeam2Set2, GamesTeam2Set3, Set
    print("Score team 2, punt omhoog")
    if GamesTeam2 < 6:
        if PointsTeam2 == 0 or PointsTeam2 == 15:
            PointsTeam2 += 15
        elif PointsTeam2 == 30:
            PointsTeam2 += 10
        elif PointsTeam2 == 40:
            if PointsTeam1 != 40:
                PointsTeam1 = 0
                PointsTeam2 = 0
                GamesTeam2 += 1
                if Set == 0:
                    GamesTeam2Set1 += 1
                elif Set == 1:
                    GamesTeam2Set2 += 1
                elif Set == 2:
                    GamesTeam2Set3 += 1 
            else:
                PointsTeam2 = "AD"
                PointsTeam1 = "-"
        elif PointsTeam2 == "AD":
            PointsTeam1 = 0
            PointsTeam2 = 0
            GamesTeam2 += 1
            if Set == 0:
                GamesTeam2Set1 += 1
            elif Set == 1:
                GamesTeam2Set2 += 1
            elif Set == 2:
                GamesTeam2Set3 += 1 
        elif PointsTeam1 == "AD":
            PointsTeam1 = 40
            PointsTeam2 = 40
    elif GamesTeam2 == 6 and GamesTeam1 <= 4:
        if PointsTeam2 == 0 or PointsTeam2 == 15:
            PointsTeam2 += 15
        elif PointsTeam2 == 30:
            PointsTeam2 += 10
        elif PointsTeam2 == 40:
            if PointsTeam1 != 40:
                PointsTeam1 = 0
                PointsTeam2 = 0
                GamesTeam1 = 0
                GamesTeam2 = 0
                Set += 1
                if Set == 0:
                    GamesTeam2Set1 += 1
                elif Set == 1:
                    GamesTeam2Set2 += 1
                elif Set == 2:
                    GamesTeam2Set3 += 1 
            else:
                PointsTeam2 = "AD"
                PointsTeam1 = "-"
        elif PointsTeam2 == "AD":
            PointsTeam1 = 0
            PointsTeam2 = 0
            GamesTeam1 = 0
            GamesTeam2 = 0
            Set += 1
            if Set == 0:
                GamesTeam2Set1 += 1
            elif Set == 1:
                GamesTeam2Set2 += 1
            elif Set == 2:
                GamesTeam2Set3 += 1 
        elif PointsTeam1 == "AD":
            PointsTeam1 = 40
            PointsTeam2 = 40
    elif GamesTeam1 == 6 and GamesTeam2 == 6:
        PointsTeam1 += 1

    socketio.emit('B2F_points_team1', {'sets': Set, 'currentGames': GamesTeam1, 'gamesSet1': GamesTeam1Set1, 'gamesSet2': GamesTeam1Set2, 'gamesSet3': GamesTeam1Set3 ,'points': PointsTeam1})    
    socketio.emit('B2F_points_team2', {'sets': Set, 'currentGames': GamesTeam2, 'gamesSet1': GamesTeam2Set1, 'gamesSet2': GamesTeam2Set2, 'gamesSet3': GamesTeam2Set3, 'points': PointsTeam2})
    # print(f"'sets': {SetsTeam1}, 'currentGames': {GamesTeam1}, 'gamesSet1': {GamesTeam1Set1}, 'gamesSet2': {GamesTeam1Set2}, 'gamesSet3': {GamesTeam1Set3} ,'points': {PointsTeam1}")
    print(f"Team1\t\tSets: {Set}\t\tGames: {GamesTeam1}\tPoints: {PointsTeam1}")
    print(f"Team2\t\tSets: {Set}\t\tGames: {GamesTeam2}\tPoints: {PointsTeam2}")  
    print(f"") 

def points_team1_down():
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, SetsTeam1, SetsTeam2
    print("Score team 1, punt omlaag")
    if GamesTeam1 != 0:
        if PointsTeam1 == 0:
            GamesTeam1 -= 1
        elif PointsTeam1 == 15:
            PointsTeam1 = 0
        elif PointsTeam1 == 30:
            PointsTeam1 = 15
        elif PointsTeam1 == 40:
            PointsTeam1 = 30
        elif PointsTeam1 == "AD":
            PointsTeam1 = 40
            PointsTeam2 = 40
    else:
        if PointsTeam1 == 0:
            pass
        elif PointsTeam1 == 15:
            PointsTeam1 = 0
        elif PointsTeam1 == 30:
            PointsTeam1 = 15
        elif PointsTeam1 == 40:
            PointsTeam1 = 30
        elif PointsTeam1 == "AD":
            PointsTeam1 = 40
            PointsTeam2 = 40

    socketio.emit('B2F_points_team1', {'sets': SetsTeam1, 'games': GamesTeam1, 'points': PointsTeam1})    
    socketio.emit('B2F_points_team2', {'sets': SetsTeam2, 'games': GamesTeam2, 'points': PointsTeam2})
    print(f"Team1\t\tSets: {SetsTeam1}\t\tGames: {GamesTeam1}\tPoints: {PointsTeam1}")
    print(f"Team2\t\tSets: {SetsTeam2}\t\tGames: {GamesTeam2}\tPoints: {PointsTeam2}")  
    print(f"")

def points_team2_down():
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, SetsTeam1, SetsTeam2
    print("Score team 1, punt omlaag")
    if GamesTeam2 != 0:
        if PointsTeam2 == 0:
            GamesTeam2 -= 1
        elif PointsTeam2 == 15:
            PointsTeam2 = 0
        elif PointsTeam2 == 30:
            PointsTeam2 = 15
        elif PointsTeam2 == 40:
            PointsTeam2 = 30
        elif PointsTeam2 == "AD":
            PointsTeam1 = 40
            PointsTeam2 = 40
    else:
        if PointsTeam2 == 0:
            pass
        elif PointsTeam2 == 15:
            PointsTeam2 = 0
        elif PointsTeam2 == 30:
            PointsTeam2 = 15
        elif PointsTeam2 == 40:
            PointsTeam2 = 30
        elif PointsTeam2 == "AD":
            PointsTeam1 = 40
            PointsTeam2 = 40

    socketio.emit('B2F_points_team1', {'sets': SetsTeam1, 'games': GamesTeam1, 'points': PointsTeam1})    
    socketio.emit('B2F_points_team2', {'sets': SetsTeam2, 'games': GamesTeam2, 'points': PointsTeam2})
    print(f"Team1\t\tSets: {SetsTeam1}\t\tGames: {GamesTeam1}\tPoints: {PointsTeam1}")
    print(f"Team2\t\tSets: {SetsTeam2}\t\tGames: {GamesTeam2}\tPoints: {PointsTeam2}")  
    print(f"")

def score():
    while True:
        if GPIO.input(knop1up) == 0:
            points_team1_up()
            time.sleep(0.2)

        elif GPIO.input(knop2up) == 0:
            points_team2_up()
            time.sleep(0.2)

        elif GPIO.input(knop1down) == 0:
            points_team1_down()
            time.sleep(0.2)

        elif GPIO.input(knop2down) == 0:
            points_team2_down()
            time.sleep(0.2)

thread1 = threading.Timer(0.1, score)
thread1.start()

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')