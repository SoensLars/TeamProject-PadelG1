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
    while True:
        messageEsp = sock.recv(buf_size)
        return messageEsp
            
#MAC address of ESP32
# addr = "08:3A:F2:AC:2A:DE" # Thomas
addr = "24:62:AB:FD:24:9E" # Lars
#uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
#service_matches = find_service( uuid = uuid, address = addr )
service_matches = find_service( address = addr )

buf_size = 1024;

while len(service_matches) == 0:
    service_matches = find_service( address = addr )
    print("couldn't find the SampleServer service =(")
    socketio.emit('B2F_esp_no_connection')    

# if len(service_matches) == 0:
#     print("couldn't find the SampleServer service =(")
#     sys.exit(0)

for s in range(len(service_matches)):
    print("\nservice_matches: [" + str(s) + "]:")
    print(service_matches[s])
    
first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

port=1
# print("connecting to \"%s\" on %s, port %s" % (name, host, port))

# Create the client socket
sock=BluetoothSocket(RFCOMM)
sock.connect((host, port))

sock.send("\nconnected\n")
print("Connected to esp32")
socketio.emit('B2F_esp_connection') 
#endregion

def points_team1_up():
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, GamesTeam1Set1, GamesTeam1Set2, GamesTeam1Set3, GamesTeam2Set1, GamesTeam2Set2, GamesTeam2Set3, Set

    # Punten verhogen voor 1 game als het aantal games lager is dan 5
    if GamesTeam1 < 5:
        if PointsTeam1 == 0:
            PointsTeam1 = 15
        elif PointsTeam1 == 15:
            PointsTeam1 = 30
        elif PointsTeam1 == 30:
            PointsTeam1 = 40
        elif PointsTeam1 == 40:
            if PointsTeam2 != 40:
                GamesTeam1 += 1
                PointsTeam1 = 0
                PointsTeam2 = 0
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
            GamesTeam1 += 1
            PointsTeam1 = 0
            PointsTeam2 = 0
            if Set == 0:
                GamesTeam1Set1 += 1
            elif Set == 1:
                GamesTeam1Set2 += 1
            elif Set == 2:
                GamesTeam1Set3 += 1
    # Als het aantal gewonnen games 5 is en het aantal gewonnen games van team 2 lager dan 5, set verhogen   
    elif GamesTeam1 == 5 and GamesTeam2 <= 4:
        if PointsTeam1 == 0:
            PointsTeam1 = 15
        elif PointsTeam1 == 15:
            PointsTeam1 = 30
        elif PointsTeam1 == 30:
            PointsTeam1 = 40
        elif PointsTeam1 == 40:
            if PointsTeam2 != 40:
                GamesTeam1 = 0
                GamesTeam2 = 0
                PointsTeam1 = 0
                PointsTeam2 = 0
                if Set == 0:
                    GamesTeam1Set1 += 1
                elif Set == 1:
                    GamesTeam1Set2 += 1
                elif Set == 2:
                    GamesTeam1Set3 += 1
                Set += 1
            else:
                PointsTeam1 = "AD"
                PointsTeam2 = "-"
        elif PointsTeam1 == "AD":
            GamesTeam1 = 0
            GamesTeam2 = 0
            PointsTeam1 = 0
            PointsTeam2 = 0
            if Set == 0:
                GamesTeam1Set1 += 1
            elif Set == 1:
                GamesTeam1Set2 += 1
            elif Set == 2:
                GamesTeam1Set3 += 1
            Set += 1    
    elif GamesTeam1 >= 5 and GamesTeam2 > 4:
        if ((GamesTeam1 - GamesTeam2) < 1): # Geen verschil van 2, dus doorspelen
            if PointsTeam1 == 0:
                PointsTeam1 = 15
            elif PointsTeam1 == 15:
                PointsTeam1 = 30
            elif PointsTeam1 == 30:
                PointsTeam1 = 40
            elif PointsTeam1 == 40:
                if PointsTeam2 != 40:
                    GamesTeam1 += 1
                    PointsTeam1 = 0
                    PointsTeam2 = 0
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
                GamesTeam1 += 1
                PointsTeam1 = 0
                PointsTeam2 = 0
                if Set == 0:
                    GamesTeam1Set1 += 1
                elif Set == 1:
                    GamesTeam1Set2 += 1
                elif Set == 2:
                    GamesTeam1Set3 += 1    
        else: # Wel een verschil van 2 dus set verhogen
            if PointsTeam1 == 0:
                PointsTeam1 = 15
            elif PointsTeam1 == 15:
                PointsTeam1 = 30
            elif PointsTeam1 == 30:
                PointsTeam1 = 40
            elif PointsTeam1 == 40:
                if PointsTeam2 != 40:
                    GamesTeam1 = 0
                    GamesTeam2 = 0
                    PointsTeam1 = 0
                    PointsTeam2 = 0
                    if Set == 0:
                        GamesTeam1Set1 += 1
                    elif Set == 1:
                        GamesTeam1Set2 += 1
                    elif Set == 2:
                        GamesTeam1Set3 += 1
                    Set += 1
                else:
                    PointsTeam1 = "AD"
                    PointsTeam2 = "-"
            elif PointsTeam1 == "AD":
                GamesTeam1 = 0
                GamesTeam2 = 0
                PointsTeam1 = 0
                PointsTeam2 = 0
                if Set == 0:
                    GamesTeam1Set1 += 1
                elif Set == 1:
                    GamesTeam1Set2 += 1
                elif Set == 2:
                    GamesTeam1Set3 += 1
                Set += 1 
        

    socketio.emit('B2F_points_team1', {'sets': Set, 'currentGames': GamesTeam1, 'gamesSet1': GamesTeam1Set1, 'gamesSet2': GamesTeam1Set2, 'gamesSet3': GamesTeam1Set3 ,'points': PointsTeam1})    
    socketio.emit('B2F_points_team2', {'sets': Set, 'currentGames': GamesTeam2, 'gamesSet1': GamesTeam2Set1, 'gamesSet2': GamesTeam2Set2, 'gamesSet3': GamesTeam2Set3, 'points': PointsTeam2})
    # print(f"'sets': {SetsTeam1}, 'currentGames': {GamesTeam1}, 'gamesSet1': {GamesTeam1Set1}, 'gamesSet2': {GamesTeam1Set2}, 'gamesSet3': {GamesTeam1Set3} ,'points': {PointsTeam1}")
    print(f"Team1\t\tSets: {Set}\t\tGames: {GamesTeam1}\tPoints: {PointsTeam1}")
    print(f"Team2\t\tSets: {Set}\t\tGames: {GamesTeam2}\tPoints: {PointsTeam2}")  


def points_team2_up():
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, GamesTeam1Set1, GamesTeam1Set2, GamesTeam1Set3, GamesTeam2Set1, GamesTeam2Set2, GamesTeam2Set3, Set
    
    if GamesTeam2 < 5:
        if PointsTeam2 == 0:
            PointsTeam2 = 15
        elif PointsTeam2 == 15:
            PointsTeam2 = 30
        elif PointsTeam2 == 30:
            PointsTeam2 = 40
        elif PointsTeam2 == 40:
            if PointsTeam1 != 40:
                GamesTeam2 += 1
                PointsTeam2 = 0
                PointsTeam1 = 0
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
            GamesTeam2 += 1
            PointsTeam1 = 0
            PointsTeam2 = 0
            if Set == 0:
                GamesTeam2Set1 += 1
            elif Set == 1:
                GamesTeam2Set2 += 1
            elif Set == 2:
                GamesTeam2Set3 += 1
    # Als het aantal gewonnen games 5 is en het aantal gewonnen games van team 1 lager dan 5, set verhogen   
    elif GamesTeam2 == 5 and GamesTeam1 <= 4:
        if PointsTeam2 == 0:
            PointsTeam2 = 15
        elif PointsTeam2 == 15:
            PointsTeam2 = 30
        elif PointsTeam2 == 30:
            PointsTeam2 = 40
        elif PointsTeam2 == 40:
            if PointsTeam1 != 40:
                GamesTeam1 = 0
                GamesTeam2 = 0
                PointsTeam1 = 0
                PointsTeam2 = 0
                if Set == 0:
                    GamesTeam2Set1 += 1
                elif Set == 1:
                    GamesTeam2Set2 += 1
                elif Set == 2:
                    GamesTeam2Set3 += 1
                Set += 1
            else:
                PointsTeam2 = "AD"
                PointsTeam1 = "-"
        elif PointsTeam2 == "AD":
            GamesTeam1 = 0
            GamesTeam2 = 0
            PointsTeam1 = 0
            PointsTeam2 = 0
            if Set == 0:
                GamesTeam2Set1 += 1
            elif Set == 1:
                GamesTeam2Set2 += 1
            elif Set == 2:
                GamesTeam2Set3 += 1
            Set += 1    
    elif GamesTeam2 >= 5 and GamesTeam1 > 4:
        if ((GamesTeam2 - GamesTeam1) < 1): # Geen verschil van 2, dus doorspelen
            if PointsTeam2 == 0:
                PointsTeam2 = 15
            elif PointsTeam2 == 15:
                PointsTeam2 = 30
            elif PointsTeam2 == 30:
                PointsTeam2 = 40
            elif PointsTeam2 == 40:
                if PointsTeam1 != 40:
                    GamesTeam2 += 1
                    PointsTeam1 = 0
                    PointsTeam2 = 0
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
                GamesTeam2 += 1
                PointsTeam1 = 0
                PointsTeam2 = 0
                if Set == 0:
                    GamesTeam2Set1 += 1
                elif Set == 1:
                    GamesTeam2Set2 += 1
                elif Set == 2:
                    GamesTeam2Set3 += 1    
        else: # Wel een verschil van 2 dus set verhogen
            if PointsTeam2 == 0:
                PointsTeam2 = 15
            elif PointsTeam2 == 15:
                PointsTeam2 = 30
            elif PointsTeam2 == 30:
                PointsTeam2 = 40
            elif PointsTeam2 == 40:
                if PointsTeam1 != 40:
                    GamesTeam1 = 0
                    GamesTeam2 = 0
                    PointsTeam1 = 0
                    PointsTeam2 = 0
                    if Set == 0:
                        GamesTeam2Set1 += 1
                    elif Set == 1:
                        GamesTeam2Set2 += 1
                    elif Set == 2:
                        GamesTeam2Set3 += 1
                    Set += 1
                else:
                    PointsTeam2 = "AD"
                    PointsTeam1 = "-"
            elif PointsTeam2 == "AD":
                GamesTeam1 = 0
                GamesTeam2 = 0
                PointsTeam1 = 0
                PointsTeam2 = 0
                if Set == 0:
                    GamesTeam2Set1 += 1
                elif Set == 1:
                    GamesTeam2Set2 += 1
                elif Set == 2:
                    GamesTeam2Set3 += 1
                Set += 1 

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
    while True:

        message = rx_and_echo()
        # print((message))

        # if GPIO.input(knop1up) == 0:
        if message == b'teamRoodUp':
            points_team1_up()

        # elif GPIO.input(knop2up) == 0:
        elif message == b'teamBlauwUp':
            points_team2_up()

        # elif GPIO.input(knop1down) == 0:
        elif message == b'teamRoodDown':
            points_team1_down()

        # elif GPIO.input(knop2down) == 0:
        elif message == b'teamBlauwDown':
            points_team2_down()

        time.sleep(0.1)


thread1 = threading.Timer(0.1, score)
thread1.start()

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')