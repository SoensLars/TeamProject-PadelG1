# from concurrent.futures import thread
from socket import socket
from RPi import GPIO
from subprocess import check_output, call 
import time
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit, send
from flask_cors import CORS
import threading
import serial
from bluetooth import *
import subprocess as sp
import pygame

knopReset = 26
knopPower = 19

# knop2up = 21
# knop2down = 2

# Punten en games in de huidige set
PointsTeam1 = 0
PointsTeam2 = 0

GamesTeam1 = 0
GamesTeam2 = 0

# Aantal games van voorbije sets bijohouden
GamesTeam1Set1 = 0
GamesTeam1Set2 = 0
GamesTeam1Set3 = 0

GamesTeam2Set1 = 0
GamesTeam2Set2 = 0
GamesTeam2Set3 = 0

Set = 0

# Previous points
# prevPoints1 = 0
# prevPoints2 = 0

# prevGames1 = 0
# prevGames2 = 0

# prevGames1Set1 = 0
# prevGames1Set2 = 0
# prevGames1Set3 = 0

# prevGames2Set1 = 0
# prevGames2Set2 = 0
# prevGames2Set3 = 0

# prevSets = 0
lastScored = ""
prevPoint = 0
prevPoint1 = 0
prevPoint2 = 0
prevServe = 0

# Controleren of het eerste punt voor het echte spel al is gespeeld
stateServiceTeam1 = False
stateServiceTeam2 = False
stateServiceSide = True # True is rood, false is blauw
serviceStart = "" # Welk kleur is er gestart met serveren?
serviceStartConst = ""

winState = False
resetState = False

sponsorState = False
stateSponsorsSet1 = 0
stateSponsorsSet2 = 0

timerState = False
timerClubStart = 0

connectionEsp = False
stateConnection = 0

messageEsp = ""


GPIO.setmode(GPIO.BCM)
# GPIO.setup((knop1up, knop1down, knop2up, knop2down), GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup((knopReset, knopPower), GPIO.IN, pull_up_down=GPIO.PUD_UP)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False, ping_timeout=1)
CORS(app)

pygame.mixer.init()
#region -- Code ESP Connection   
addr = "C4:4F:33:77:00:13" # Draadloos
# addr = "24:62:AB:FD:24:9E" # Lars

# sock=BluetoothSocket(RFCOMM)
buf_size = 1024;

def input_and_send(sock):
    print("\nType something\n")
    while True:
        data = input()
        if len(data) == 0: break
        sock.send(data)
        sock.send("\n")
        
def rx_and_echo(sock):
    global messageEsp
    while True:
        messageEsp = sock.recv(buf_size)
        return messageEsp

def esp_connection(sock):
    global addr
    #MAC address of ESP32
    #uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    #service_matches = find_service( uuid = uuid, address = addr )
    service_matches = find_service( address = addr )

    while len(service_matches) == 0:
        service_matches = find_service( address = addr )
        print("couldn't find the SampleServer service =(")
        socketio.emit('B2F_esp_no_connection')    

    # if len(service_matches) == 0:
    #     print("couldn't find the SampleServer service =(")
    #     sys.exit(0)

    # for s in range(len(service_matches)):
    #     print("\nservice_matches: [" + str(s) + "]:")
    #     print(service_matches[s])
        
    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    # port=1
    # print("connecting to \"%s\" on %s, port %s" % (name, host, port))

    # Create the client socket
    sock.connect((host, port))

    sock.send("\nconnected\n")
    print("Connected to esp32")
    socketio.emit('B2F_esp_connection')
#endregion

# Textfiles
def read_file():
    with open('/home/lars/Project/files/club.txt') as f:
        clubMessage = f.read()
        return clubMessage

# Sound
def play_sound_up():
    pygame.mixer.music.load("/home/lars/Project/sounds/beep_up.mp3")
    pygame.mixer.music.play()

def play_sound_down():
    pygame.mixer.music.load("/home/lars/Project/sounds/beep_down.mp3")
    pygame.mixer.music.play()

# Functions points
def points_team1_up():
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, GamesTeam1Set1, GamesTeam1Set2, GamesTeam1Set3, GamesTeam2Set1, GamesTeam2Set2, GamesTeam2Set3, Set, stateServiceSide, serviceStart, lastScored, prevPoint, prevPoint1, prevPoint2, prevServe, serviceStartConst
    prevPoint1 = PointsTeam1
    prevPoint2 = PointsTeam2
    lastScored = "red"
    prevPoint = PointsTeam1
    prevServe = stateServiceSide
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
                stateServiceSide = not stateServiceSide
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
            stateServiceSide = not stateServiceSide
        elif PointsTeam1 == "-":
            PointsTeam1 = 40
            PointsTeam2 = 40
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
                stateServiceSide = not stateServiceSide
                Set += 1
                if Set == 1:
                    if serviceStartConst == 'red':
                        stateServiceSide = False
                    elif serviceStartConst == 'blue':
                        stateServiceSide = True
                elif Set == 2:
                    if serviceStartConst == 'red':
                        stateServiceSide = True
                    elif serviceStartConst == 'blue':
                        stateServiceSide = False
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
            stateServiceSide = not stateServiceSide
            Set += 1 
            if Set == 1:
                    if serviceStartConst == 'red':
                        stateServiceSide = False
                    elif serviceStartConst == 'blue':
                        stateServiceSide = True
            elif Set == 2:
                if serviceStartConst == 'red':
                        stateServiceSide = True
                elif serviceStartConst == 'blue':
                    stateServiceSide = False
        elif PointsTeam1 == "-":
            PointsTeam1 = 40
            PointsTeam2 = 40   
    elif (GamesTeam1 >= 5 and GamesTeam2 > 4):
        # Tiebreak spelen of niet
        if (GamesTeam1 == 6 and GamesTeam2 == 6):
            if serviceStart == 'red':
                stateServiceSide = True
                serviceStart = ''
            elif serviceStart == 'blue':
                stateServiceSide = False
                serviceStart = ''
            if (PointsTeam1 + PointsTeam2) % 2 == 0:
                pass
            else:
                stateServiceSide = not stateServiceSide
            if (PointsTeam1 == 6 and PointsTeam2 <= 5):
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
                if Set == 1:
                    if serviceStartConst == 'red':
                        stateServiceSide = False
                    elif serviceStartConst == 'blue':
                        stateServiceSide = True
                elif Set == 2:
                    if serviceStartConst == 'red':
                        stateServiceSide = True
                    elif serviceStartConst == 'blue':
                        stateServiceSide = False
            elif (PointsTeam1 >= 6 and PointsTeam2 > 5) :
                if ((PointsTeam1 - PointsTeam2) < 1):
                    PointsTeam1 += 1
                else:  
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
                    if Set == 1:
                        if serviceStartConst == 'red':
                            stateServiceSide = False
                        elif serviceStartConst == 'blue':
                            stateServiceSide = True
                    elif Set == 2:
                        if serviceStartConst == 'red':
                            stateServiceSide = True
                        elif serviceStartConst == 'blue':
                            stateServiceSide = False
            else:
                PointsTeam1 += 1
        else:
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
                        stateServiceSide = not stateServiceSide
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
                    stateServiceSide = not stateServiceSide 
                elif PointsTeam1 == "-":
                    PointsTeam1 = 40
                    PointsTeam2 = 40
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
                        stateServiceSide = not stateServiceSide
                        Set += 1
                        if Set == 1:
                            if serviceStartConst == 'red':
                                stateServiceSide = False
                            elif serviceStartConst == 'blue':
                                stateServiceSide = True
                        elif Set == 2:
                            if serviceStartConst == 'red':
                                stateServiceSide = True
                            elif serviceStartConst == 'blue':
                                stateServiceSide = False
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
                    stateServiceSide = not stateServiceSide
                    Set += 1 
                    if Set == 1:
                        if serviceStartConst == 'red':
                            stateServiceSide = False
                        elif serviceStartConst == 'blue':
                            stateServiceSide = True
                    elif Set == 2:
                        if serviceStartConst == 'red':
                            stateServiceSide = True
                        elif serviceStartConst == 'blue':
                            stateServiceSide = False
                elif PointsTeam1 == "-":
                    PointsTeam1 = 40
                    PointsTeam2 = 40
        

    socketio.emit('B2F_points_team1', {'sets': Set, 'currentGames': GamesTeam1, 'gamesSet1': GamesTeam1Set1, 'gamesSet2': GamesTeam1Set2, 'gamesSet3': GamesTeam1Set3,'points': PointsTeam1, 'stateService': stateServiceSide})    
    socketio.emit('B2F_points_team2', {'sets': Set, 'currentGames': GamesTeam2, 'gamesSet1': GamesTeam2Set1, 'gamesSet2': GamesTeam2Set2, 'gamesSet3': GamesTeam2Set3, 'points': PointsTeam2, 'stateService': stateServiceSide})
    # print(f"'sets': {SetsTeam1}, 'currentGames': {GamesTeam1}, 'gamesSet1': {GamesTeam1Set1}, 'gamesSet2': {GamesTeam1Set2}, 'gamesSet3': {GamesTeam1Set3} ,'points': {PointsTeam1}")
    print(f"Team1\t\tSets: {Set}\t\tGames: {GamesTeam1}\tPoints: {PointsTeam1}")
    print(f"Team2\t\tSets: {Set}\t\tGames: {GamesTeam2}\tPoints: {PointsTeam2}")  

def points_team2_up():
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, GamesTeam1Set1, GamesTeam1Set2, GamesTeam1Set3, GamesTeam2Set1, GamesTeam2Set2, GamesTeam2Set3, Set, stateServiceSide, serviceStart, lastScored, prevPoint, prevPoint1, prevPoint2, prevServe
    prevPoint1 = PointsTeam1
    prevPoint2 = PointsTeam2
    lastScored = "blue"
    prevPoint = PointsTeam2
    prevServe = stateServiceSide
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
                stateServiceSide = not stateServiceSide
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
            stateServiceSide = not stateServiceSide
        elif PointsTeam2 == "-":
            PointsTeam1 = 40
            PointsTeam2 = 40
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
                stateServiceSide = not stateServiceSide
                Set += 1
                if Set == 1:
                    if serviceStartConst == 'red':
                        stateServiceSide = False
                    elif serviceStartConst == 'blue':
                        stateServiceSide = True
                elif Set == 2:
                    if serviceStartConst == 'red':
                        stateServiceSide = True
                    elif serviceStartConst == 'blue':
                        stateServiceSide = False
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
            stateServiceSide = not stateServiceSide
            Set += 1    
            if Set == 1:
                if serviceStartConst == 'red':
                    stateServiceSide = False
                elif serviceStartConst == 'blue':
                    stateServiceSide = True
            elif Set == 2:
                if serviceStartConst == 'red':
                    stateServiceSide = True
                elif serviceStartConst == 'blue':
                    stateServiceSide = False
        elif PointsTeam2 == "-":
            PointsTeam1 = 40
            PointsTeam2 = 40
    elif GamesTeam2 >= 5 and GamesTeam1 > 4:
        # Tiebreak spelen
        if (GamesTeam2 == 6 and GamesTeam1 == 6):
            if serviceStart == 'red':
                stateServiceSide = True
                serviceStart = ''
            elif serviceStart == 'blue':
                stateServiceSide = False
                serviceStart = ''
            if (PointsTeam1 + PointsTeam2) % 2 == 0:
                pass
            else:
                stateServiceSide = not stateServiceSide
            if (PointsTeam2 == 6 and PointsTeam1 <= 5):
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
                if Set == 1:
                    if serviceStartConst == 'red':
                        stateServiceSide = False
                    elif serviceStartConst == 'blue':
                        stateServiceSide = True
                elif Set == 2:
                    if serviceStartConst == 'red':
                        stateServiceSide = True
                    elif serviceStartConst == 'blue':
                        stateServiceSide = False
            elif (PointsTeam2 >= 6 and PointsTeam1 > 5) :
                if ((PointsTeam2 - PointsTeam1) < 1):
                    PointsTeam2 += 1
                else:
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
                    if Set == 1:
                        if serviceStartConst == 'red':
                            stateServiceSide = False
                        elif serviceStartConst == 'blue':
                            stateServiceSide = True
                    elif Set == 2:
                        if serviceStartConst == 'red':
                            stateServiceSide = True
                        elif serviceStartConst == 'blue':
                            stateServiceSide = False
            else:
                PointsTeam2 += 1
        else:
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
                        stateServiceSide = not stateServiceSide
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
                    stateServiceSide = not stateServiceSide 
                elif PointsTeam2 == "-":
                    PointsTeam1 = 40
                    PointsTeam2 = 40
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
                        stateServiceSide = not stateServiceSide
                        Set += 1
                        if Set == 1:
                            if serviceStartConst == 'red':
                                stateServiceSide = False
                            elif serviceStartConst == 'blue':
                                stateServiceSide = True
                        elif Set == 2:
                            if serviceStartConst == 'red':
                                stateServiceSide = True
                            elif serviceStartConst == 'blue':
                                stateServiceSide = False
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
                    stateServiceSide = not stateServiceSide
                    Set += 1 
                    if Set == 1:
                        if serviceStartConst == 'red':
                            stateServiceSide = False
                        elif serviceStartConst == 'blue':
                            stateServiceSide = True
                    elif Set == 2:
                        if serviceStartConst == 'red':
                            stateServiceSide = True
                        elif serviceStartConst == 'blue':
                            stateServiceSide = False
                elif PointsTeam2 == "-":
                    PointsTeam1 = 40
                    PointsTeam2 = 40

    socketio.emit('B2F_points_team1', {'sets': Set, 'currentGames': GamesTeam1, 'gamesSet1': GamesTeam1Set1, 'gamesSet2': GamesTeam1Set2, 'gamesSet3': GamesTeam1Set3, 'points': PointsTeam1, 'stateService': stateServiceSide})    
    socketio.emit('B2F_points_team2', {'sets': Set, 'currentGames': GamesTeam2, 'gamesSet1': GamesTeam2Set1, 'gamesSet2': GamesTeam2Set2, 'gamesSet3': GamesTeam2Set3, 'points': PointsTeam2, 'stateService': stateServiceSide})
    # print(f"'sets': {SetsTeam1}, 'currentGames': {GamesTeam1}, 'gamesSet1': {GamesTeam1Set1}, 'gamesSet2': {GamesTeam1Set2}, 'gamesSet3': {GamesTeam1Set3} ,'points': {PointsTeam1}")
    print(f"Team1\t\tSets: {Set}\t\tGames: {GamesTeam1}\tPoints: {PointsTeam1}")
    print(f"Team2\t\tSets: {Set}\t\tGames: {GamesTeam2}\tPoints: {PointsTeam2}")  
    print(f"") 


def points_down():
    global PointsTeam1, PointsTeam2, Set, prevPoint, prevPoint1, prevPoint2, lastScored, GamesTeam1, GamesTeam2, GamesTeam1Set1, GamesTeam2Set1, GamesTeam1Set2, GamesTeam2Set2, GamesTeam1Set3, GamesTeam2Set3, stateServiceSide, prevServe
    if lastScored == "red":
        if Set == 0:
            if PointsTeam1 == 0 and PointsTeam2 == 0:
                if GamesTeam1 == 0:
                    pass
                else:
                    GamesTeam1Set1 -= 1
                    GamesTeam1 -= 1
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = not stateServiceSide
            else:
                # Punten team rood terugzetten, blauw ongewijzigd
                PointsTeam1 = prevPoint
        if Set == 1:
            if PointsTeam1 == 0 and PointsTeam2 == 0:
                if GamesTeam1 == 0 and GamesTeam2 == 0:
                    Set = 0
                    GamesTeam1Set1 -= 1
                    # GamesTeam1 -= 1
                    GamesTeam1 = GamesTeam1Set1
                    GamesTeam2 = GamesTeam2Set1
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = prevServe # niet helemaal zeker
                else:
                    GamesTeam1Set2 -= 1
                    GamesTeam1 -= 1
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = not stateServiceSide
            else:
                # Punten team rood terugzetten, blauw ongewijzigd
                PointsTeam1 = prevPoint
        elif Set == 2:
            if PointsTeam1 == 0 and PointsTeam2 == 0:
                if GamesTeam1 == 0 and GamesTeam2 == 0:
                    Set = 1
                    GamesTeam1Set2 -= 1
                    # GamesTeam2 -= 1
                    GamesTeam1 = GamesTeam1Set2
                    GamesTeam2 = GamesTeam2Set2
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = prevServe # niet helemaal zeker
                else:
                    GamesTeam1Set3 -= 1
                    GamesTeam1 -= 1
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = not stateServiceSide
            else:
                # Punten team rood terugzetten, blauw ongewijzigd
                PointsTeam1 = prevPoint
        elif Set == 3:
            if PointsTeam1 == 0 and PointsTeam2 == 0:
                if GamesTeam1 == 0 and GamesTeam2 == 0:
                    Set = 2
                    GamesTeam1Set3 -= 1
                    # GamesTeam1 -= 1
                    GamesTeam1 = GamesTeam1Set3
                    GamesTeam2 = GamesTeam2Set3
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = prevServe # niet helemaal zeker
    elif lastScored == "blue":
        if Set == 0:
            if PointsTeam1 == 0 and PointsTeam2 == 0:
                if GamesTeam2 == 0:
                    pass
                else:
                    GamesTeam2Set1 -= 1
                    GamesTeam2 -= 1
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = not stateServiceSide
            else:
                # Punten team blauw terugzetten, rood ongewijzigd
                PointsTeam2 = prevPoint
        elif Set == 1:
            if PointsTeam1 == 0 and PointsTeam2 == 0:
                if GamesTeam1 == 0 and GamesTeam2 == 0:
                    Set = 0
                    GamesTeam2Set1 -= 1
                    # GamesTeam2 -= 1
                    GamesTeam1 = GamesTeam1Set1
                    GamesTeam2 = GamesTeam2Set1
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = prevServe # niet helemaal zeker
                else:
                    GamesTeam2Set2 -= 1
                    GamesTeam2 -= 1
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = not stateServiceSide
            else:
                # Punten team rood terugzetten, blauw ongewijzigd
                PointsTeam1 = prevPoint
        elif Set == 2:
            if PointsTeam1 == 0 and PointsTeam2 == 0:
                if GamesTeam1 == 0 and GamesTeam2 == 0:
                    Set = 1
                    GamesTeam2Set2 -= 1
                    # GamesTeam2 -= 1
                    GamesTeam1 = GamesTeam1Set2
                    GamesTeam2 = GamesTeam2Set2
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = prevServe # niet helemaal zeker
                else:
                    GamesTeam2Set3 -= 1
                    GamesTeam2 -= 1
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = not stateServiceSide
        elif Set == 3:
            if PointsTeam1 == 0 and PointsTeam2 == 0:
                if GamesTeam1 == 0 and GamesTeam2 == 0:
                    Set = 2
                    GamesTeam2Set3 -= 1
                    # GamesTeam2 -= 1
                    GamesTeam1 = GamesTeam1Set3
                    GamesTeam2 = GamesTeam2Set3
                    PointsTeam1 = prevPoint1
                    PointsTeam2 = prevPoint2
                    stateServiceSide = prevServe # niet helemaal zeker


    socketio.emit('B2F_points_team1', {'sets': Set, 'currentGames': GamesTeam1, 'gamesSet1': GamesTeam1Set1, 'gamesSet2': GamesTeam1Set2, 'gamesSet3': GamesTeam1Set3 ,'points': PointsTeam1, 'stateService': stateServiceSide})    
    socketio.emit('B2F_points_team2', {'sets': Set, 'currentGames': GamesTeam2, 'gamesSet1': GamesTeam2Set1, 'gamesSet2': GamesTeam2Set2, 'gamesSet3': GamesTeam2Set3, 'points': PointsTeam2, 'stateService': stateServiceSide})
    # print(f"'sets': {SetsTeam1}, 'currentGames': {GamesTeam1}, 'gamesSet1': {GamesTeam1Set1}, 'gamesSet2': {GamesTeam1Set2}, 'gamesSet3': {GamesTeam1Set3} ,'points': {PointsTeam1}")
    # print(f"Team1\t\tSets: {Set}\t\tGames: {GamesTeam1}\tPoints: {PointsTeam1}")
    # print(f"Team2\t\tSets: {Set}\t\tGames: {GamesTeam2}\tPoints: {PointsTeam2}")  
    print(f"") 

def send_points_to_frontend(message):
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, GamesTeam1Set1, GamesTeam1Set2, GamesTeam1Set3, GamesTeam2Set1, GamesTeam2Set2, GamesTeam2Set3, Set, stateServiceTeam1, stateServiceTeam2, stateServiceSide, serviceStart, winState, timerClubStart, sponsorState, serviceStartConst

    if sponsorState == True:
        pass
    else:
        if message == b'teamRoodUp':
            # Als state False is --> Bepalen wie mag serveren, Als state True is --> Punten gaan bijtellen
            if stateServiceTeam1 == False:
                stateServiceTeam1 = True
                stateServiceTeam2 = True
                stateServiceSide = True
                serviceStart = "red"
                serviceStartConst = serviceStart
                socketio.emit('B2F_serve', stateServiceSide)
            else:
                if Set == 2:
                    # Controleren of er een eventuele derde set moet worden gespeeld
                    if (GamesTeam1Set1 > GamesTeam2Set1 and GamesTeam1Set2 > GamesTeam2Set2) or (GamesTeam2Set1 > GamesTeam1Set1 and GamesTeam2Set2 > GamesTeam1Set2):
                        print("Spel gedaan")
                        # winState = True
                        # timerClubStart = time.time()
                    else:
                        points_team1_up()
                        play_sound_up()
                elif Set == 3:
                    print("Spel gedaan")
                    # winState = True
                    # timerClubStart = time.time()
                else:
                    points_team1_up()
                    play_sound_up()

        # elif GPIO.input(knop2up) == 0:
        elif message == b'teamBlauwUp':
            # Als state False is --> Bepalen wie mag serveren, Als state True is --> Punten gaan bijtellen
            if stateServiceTeam2 == False:
                stateServiceTeam1 = True
                stateServiceTeam2 = True
                stateServiceSide = False
                serviceStart = "blue"
                serviceStartConst = serviceStart
                socketio.emit('B2F_serve', stateServiceSide)
            else:
                if Set == 2:
                    # Controleren of er een eventuele derde set moet worden gespeeld
                    if (GamesTeam2Set1 > GamesTeam1Set1 and GamesTeam2Set2 > GamesTeam1Set2) or (GamesTeam1Set1 > GamesTeam2Set1 and GamesTeam1Set2 > GamesTeam2Set2):
                        print("Spel gedaan")
                        # winState = True
                        # timerClubStart = time.time()
                    else:
                        points_team2_up()
                        play_sound_up()
                elif Set == 3:
                    print("Spel gedaan")
                    # winState = True
                    # timerClubStart = time.time()
                else:
                    points_team2_up()
                    play_sound_up()

        # elif GPIO.input(knop1down) == 0:
        elif message == b'teamRoodDown':
            # points_team1_down()
            points_down()
            play_sound_down()

        # elif GPIO.input(knop2down) == 0:
        elif message == b'teamBlauwDown':
            # points_team2_down()
            points_down()
            play_sound_down()

        if Set == 2:
            if (GamesTeam1Set1 > GamesTeam2Set1 and GamesTeam1Set2 > GamesTeam2Set2) or (GamesTeam2Set1 > GamesTeam1Set1 and GamesTeam2Set2 > GamesTeam1Set2):
                winState = True
                timerClubStart = time.time()
            else:
                pass

        elif Set == 3:
            winState = True
            timerClubStart = time.time()

# Threads
def score():
    sock=BluetoothSocket(RFCOMM)
    esp_connection(sock)
    while True:
        message = ""
        try:
            message = rx_and_echo(sock)
            send_points_to_frontend(message)
        except:
            # Exception voor de connectie met esp die wegvalt
            print("Connectie opnieuw leggen")
            socketio.emit('B2F_esp_no_connection')   
            while True:
                # Deze while blijven overlopen om te reconnecten
                try:
                    sock=BluetoothSocket(RFCOMM)
                    esp_connection(sock)
                    message = rx_and_echo(sock)
                    send_points_to_frontend(message)
                except:
                    print("Connectie opnieuw leggen")
                    socketio.emit('B2F_esp_no_connection')   
                break

        time.sleep(0.1)

def sponsors():
    global GamesTeam1, GamesTeam2, PointsTeam1, PointsTeam2, Set, stateSponsorsSet1, stateSponsorsSet2, sponsorState
    while True:
        if Set == 0:
            pass
        elif Set == 1:
            time.sleep(5)
            if stateSponsorsSet1 == 0:
                if GamesTeam1 == 0 and GamesTeam2 == 0 and PointsTeam1 == 0 and PointsTeam2 == 0:
                    print('Show sponsors')
                    socketio.emit('B2F_show_sponsors')
                    sponsorState = True
                    time.sleep(30)
                    print('Hide sponsors')
                    socketio.emit('B2F_hide_sponsors')
                    sponsorState = False
                    stateSponsorsSet1 = 1
                else:
                    pass
            else:
                pass
        elif Set == 2:
            if (GamesTeam1Set1 > GamesTeam2Set1 and GamesTeam1Set2 > GamesTeam2Set2) or (GamesTeam2Set1 > GamesTeam1Set1 and GamesTeam2Set2 > GamesTeam1Set2):
                pass
            else:
                time.sleep(5)
                if stateSponsorsSet2 == 0:
                    if GamesTeam1 == 0 and GamesTeam2 == 0 and PointsTeam1 == 0 and PointsTeam2 == 0:
                        print('Show sponsors')
                        socketio.emit('B2F_show_sponsors')
                        sponsorState = True
                        time.sleep(30)
                        print('Hide sponsors')
                        socketio.emit('B2F_hide_sponsors')
                        sponsorState = False
                        stateSponsorsSet2 = 1
                else:
                    pass
        
        time.sleep(1)

def reset():
    global PointsTeam1, PointsTeam2, GamesTeam1, GamesTeam2, GamesTeam1Set1, GamesTeam1Set2, GamesTeam1Set3, GamesTeam2Set1, GamesTeam2Set2, GamesTeam2Set3, Set, stateServiceTeam1, stateServiceTeam2, resetState, stateSponsorsSet1, stateSponsorsSet2
    while True:
        if GPIO.input(knopReset) == 0:
            # print("Reset")
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
            stateSponsorsSet1 = 0
            stateSponsorsSet2 = 0
            stateServiceTeam1 = False
            stateServiceTeam2 = False
            resetState = True
            print('Reset')
            
            socketio.emit('B2F_reset')
            socketio.emit('B2F_points_team1', {'sets': Set, 'currentGames': GamesTeam1, 'gamesSet1': GamesTeam1Set1, 'gamesSet2': GamesTeam1Set2, 'gamesSet3': GamesTeam1Set3 ,'points': PointsTeam1, 'stateService': stateServiceSide})    
            socketio.emit('B2F_points_team2', {'sets': Set, 'currentGames': GamesTeam2, 'gamesSet1': GamesTeam2Set1, 'gamesSet2': GamesTeam2Set2, 'gamesSet3': GamesTeam2Set3, 'points': PointsTeam2, 'stateService': stateServiceSide})
            socketio.emit('B2F_club_message', {'message': read_file()})
        
        if GPIO.input(knopPower) == 0:
            print("Shut down")
            call("sudo poweroff", shell=True)

        time.sleep(0.1)

def timer_club():
    global resetState, winState, timerClubStart, timerState
    while True:
        if winState == True and resetState == False:
            timerClubCurrent = time.time()
            timerClub = timerClubCurrent - timerClubStart
            print(timerClub)
            if timerClub > 10:
                if timerState == False:
                    print("Show clubpage")
                    socketio.emit('B2F_club_page')
                    timerState = True
                else: 
                    pass

        elif winState == True and resetState == True:
            # print("New Game")
            winState = False
            resetState = False
            timerState = False

        time.sleep(1)


thread1 = threading.Timer(0.1, score)
thread1.start()
thread2 = threading.Timer(0.1, reset)
thread2.start()
thread3 = threading.Timer(0.1, sponsors)
thread3.start()
thread4 = threading.Timer(0.1, timer_club)
thread4.start()

# @socketio.on('F2B_mac')
# def mac_address(payload):
#     print(payload['MAC'])

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')