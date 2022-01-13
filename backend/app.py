from RPi import GPIO
from subprocess import check_output, call 
import time
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit, send
from flask_cors import CORS
import threading
import serial
from bluetooth import *

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

messageEsp = ""

GPIO.setmode(GPIO.BCM)
GPIO.setup((knop1up, knop1down, knop2up, knop2down), GPIO.IN, pull_up_down=GPIO.PUD_UP)
# ser = serial.Serial('/dev/rfcomm0')
# ser.isOpen()

#region -- Code ESP Connection    
def input_and_send():
    print("\nType something\n")
    while True:
        data = input()
        if len(data) == 0: break
        sock.send(data)
        sock.send("\n")
        
def rx_and_echo():
    global messageEsp
    sock.send("\nconnected\n")
    while True:
        messageEsp = sock.recv(buf_size)
        return messageEsp
            
#MAC address of ESP32
addr = "08:3A:F2:AC:2A:DE"
#uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
#service_matches = find_service( uuid = uuid, address = addr )
service_matches = find_service( address = addr )

buf_size = 1024;

if len(service_matches) == 0:
    print("couldn't find the SampleServer service =(")
    sys.exit(0)

for s in range(len(service_matches)):
    print("\nservice_matches: [" + str(s) + "]:")
    print(service_matches[s])
    
first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

port=1
print("connecting to \"%s\" on %s, port %s" % (name, host, port))

# Create the client socket
sock=BluetoothSocket(RFCOMM)
sock.connect((host, port))

print("connected")
#endregion

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

    # if Set == 2:
    #     if GamesTeam1Set1 > GamesTeam2Set1 and GamesTeam1Set2 > GamesTeam2Set2:
    #         print('Geen 3e set')
    #     elif GamesTeam2Set1 > GamesTeam1Set1 and GamesTeam2Set2 > GamesTeam1Set2:
    #         print('Geen 3e set')
    #     else:
    #         print('Speel 3e set')

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

    # if Set == 2:
    #     if GamesTeam1Set1 > GamesTeam2Set1 and GamesTeam1Set2 > GamesTeam2Set2:
    #         print('Geen 3e set')
    #     elif GamesTeam2Set1 > GamesTeam1Set1 and GamesTeam2Set2 > GamesTeam1Set2:
    #         print('Geen 3e set')
    #     else:
    #         print('Speel 3e set')

    socketio.emit('B2F_points_team1', {'sets': Set, 'currentGames': GamesTeam1, 'gamesSet1': GamesTeam1Set1, 'gamesSet2': GamesTeam1Set2, 'gamesSet3': GamesTeam1Set3 ,'points': PointsTeam1})    
    socketio.emit('B2F_points_team2', {'sets': Set, 'currentGames': GamesTeam2, 'gamesSet1': GamesTeam2Set1, 'gamesSet2': GamesTeam2Set2, 'gamesSet3': GamesTeam2Set3, 'points': PointsTeam2})
    # print(f"'sets': {SetsTeam1}, 'currentGames': {GamesTeam1}, 'gamesSet1': {GamesTeam1Set1}, 'gamesSet2': {GamesTeam1Set2}, 'gamesSet3': {GamesTeam1Set3} ,'points': {PointsTeam1}")
    print(f"Team1\t\tSets: {Set}\t\tGames: {GamesTeam1}\tPoints: {PointsTeam1}")
    print(f"Team2\t\tSets: {Set}\t\tGames: {GamesTeam2}\tPoints: {PointsTeam2}")  
    print(f"") 

def points_team1_down():
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, GamesTeam1Set1, GamesTeam1Set2, GamesTeam1Set3, GamesTeam2Set1, GamesTeam2Set2, GamesTeam2Set3, Set
    print("Score team 1, punt omlaag")
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

    socketio.emit('B2F_points_team1', {'sets': Set, 'currentGames': GamesTeam1, 'gamesSet1': GamesTeam1Set1, 'gamesSet2': GamesTeam1Set2, 'gamesSet3': GamesTeam1Set3 ,'points': PointsTeam1})    
    socketio.emit('B2F_points_team2', {'sets': Set, 'currentGames': GamesTeam2, 'gamesSet1': GamesTeam2Set1, 'gamesSet2': GamesTeam2Set2, 'gamesSet3': GamesTeam2Set3, 'points': PointsTeam2})
    # print(f"'sets': {SetsTeam1}, 'currentGames': {GamesTeam1}, 'gamesSet1': {GamesTeam1Set1}, 'gamesSet2': {GamesTeam1Set2}, 'gamesSet3': {GamesTeam1Set3} ,'points': {PointsTeam1}")
    print(f"Team1\t\tSets: {Set}\t\tGames: {GamesTeam1}\tPoints: {PointsTeam1}")
    print(f"Team2\t\tSets: {Set}\t\tGames: {GamesTeam2}\tPoints: {PointsTeam2}")  
    print(f"") 

def points_team2_down():
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, GamesTeam1Set1, GamesTeam1Set2, GamesTeam1Set3, GamesTeam2Set1, GamesTeam2Set2, GamesTeam2Set3, Set
    print("Score team 1, punt omlaag")
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

    socketio.emit('B2F_points_team1', {'sets': Set, 'currentGames': GamesTeam1, 'gamesSet1': GamesTeam1Set1, 'gamesSet2': GamesTeam1Set2, 'gamesSet3': GamesTeam1Set3 ,'points': PointsTeam1})    
    socketio.emit('B2F_points_team2', {'sets': Set, 'currentGames': GamesTeam2, 'gamesSet1': GamesTeam2Set1, 'gamesSet2': GamesTeam2Set2, 'gamesSet3': GamesTeam2Set3, 'points': PointsTeam2})
    # print(f"'sets': {SetsTeam1}, 'currentGames': {GamesTeam1}, 'gamesSet1': {GamesTeam1Set1}, 'gamesSet2': {GamesTeam1Set2}, 'gamesSet3': {GamesTeam1Set3} ,'points': {PointsTeam1}")
    print(f"Team1\t\tSets: {Set}\t\tGames: {GamesTeam1}\tPoints: {PointsTeam1}")
    print(f"Team2\t\tSets: {Set}\t\tGames: {GamesTeam2}\tPoints: {PointsTeam2}")  
    print(f"") 

def score():
    # hallo = rx_and_echo()
    while True:

        message = rx_and_echo()
        # tekst = ser.readline()
        print(len(message))

        # if GPIO.input(knop1up) == 0:
        if len(message) == 12:
            points_team1_up()
            time.sleep(0.2)

        # elif GPIO.input(knop2up) == 0:
        elif len(message) == 13:
            points_team2_up()
            time.sleep(0.2)

        # elif GPIO.input(knop1down) == 0:
        elif len(message) == 14:
            points_team1_down()
            time.sleep(0.2)

        # elif GPIO.input(knop2down) == 0:
        elif len(message) == 15:
            points_team2_down()
            time.sleep(0.2)
        # if len(tekst) == 12:
        #     points_team1_up()
        # elif len(tekst) == 13:
        #     points_team2_up()

        time.sleep(0.1)


thread1 = threading.Timer(0.1, score)
thread1.start()

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')