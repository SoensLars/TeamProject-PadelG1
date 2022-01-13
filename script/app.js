'use strict'

const lanIP = `${window.location.hostname}:5000`;
const socketio = io(`http://${lanIP}`);

var pointsTeam1, currentGames1, gamesSet1Team1, gamesSet2Team1, gamesSet3Team1, setsTeam1
var pointsTeam2, currentGames2, gamesSet1Team2, gamesSet2Team2, gamesSet3Team2, setsTeam2

var sets
var points1, currentGames1, games1Set1, games1Set2, games1Set3
var points2, currentGames2, games2Set1, games2Set2, games2Set3

const yellow = "#FEDF2D";

function listenToSocket () {
    socketio.on('B2F_points_team1', function (payload) {
        points1 = payload['points']
        currentGames1 = payload['games']
        games1Set1 = payload['gamesSet1']
        games1Set2 = payload['gamesSet2']
        games1Set3 = payload['gamesSet3']
        sets = payload['sets']
        pointsTeam1.innerHTML = points1
        gamesSet1Team1.innerHTML = games1Set1
        gamesSet2Team1.innerHTML = games1Set2
        gamesSet3Team1.innerHTML = games1Set3

        console.log(sets)
        if (sets == 1)   {
            gamesSet2Team1.style.visibility  = "visible"
            gamesSet2Team2.style.visibility  = "visible"
            if (games1Set1 > games2Set1) {
                gamesSet1Team1.style.color  = yellow;
            }
            else {
                gamesSet1Team2.style.color  = yellow
            }
        }   

        if (sets == 2)   {
            gamesSet3Team1.style.visibility  = "visible"
            gamesSet3Team2.style.visibility  = "visible"
            if (games1Set2 > games2Set2) {
                gamesSet2Team1.style.color  = yellow
            }
            else {
                gamesSet2Team2.style.color  = yellow
            }
        }

        if (sets == 3)   {
            if (games1Set3 > games2Set3) {
                gamesSet3Team1.style.color  = yellow
            }
            else {
                gamesSet3Team2.style.color  = yellow
            }
        }
    });
    socketio.on('B2F_points_team2', function (payload) {
        points2 = payload['points']
        currentGames1 = payload['games']
        games2Set1 = payload['gamesSet1']
        games2Set2 = payload['gamesSet2']
        games2Set3 = payload['gamesSet3']
        sets = payload['sets']
        pointsTeam2.innerHTML = points2
        gamesSet1Team2.innerHTML = games2Set1
        gamesSet2Team2.innerHTML = games2Set2
        gamesSet3Team2.innerHTML = games2Set3


        if (sets == 1)   {
            gamesSet2Team1.style.visibility  = "visible"
            gamesSet2Team2.style.visibility  = "visible"
            if (games1Set1 > games2Set1) {
                gamesSet1Team1.style.color  = "#FEDF2D"
            }
            else {
                gamesSet1Team2.style.color  = "#FEDF2D"
            }
        }   
    });
}

function init () {
    pointsTeam1 = document.querySelector('.js-points-1')
    currentGames1 = document.querySelector('.js-games-1')
    gamesSet1Team1 = document.querySelector('.js-games-set1-1')
    gamesSet2Team1 = document.querySelector('.js-games-set2-1')
    gamesSet3Team1 = document.querySelector('.js-games-set3-1')

    pointsTeam2 = document.querySelector('.js-points-2')
    currentGames2 = document.querySelector('.js-games-2')
    gamesSet1Team2 = document.querySelector('.js-games-set1-2')
    gamesSet2Team2 = document.querySelector('.js-games-set2-2')
    gamesSet3Team2 = document.querySelector('.js-games-set3-2')

    console.log(window.location.hostname)
    listenToSocket()
     
}

document.addEventListener('DOMContentLoaded', function () {
    init();
})