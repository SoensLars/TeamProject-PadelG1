'use strict'

const lanIP = `${window.location.hostname}:5000`;
const socketio = io(`http://${lanIP}`);

var pointsTeam1, currentGames1, gamesSet1Team1, gamesSet2Team1, gamesSet3Team1, setsTeam1
var pointsTeam2, currentGames2, gamesSet1Team2, gamesSet2Team2, gamesSet3Team2, setsTeam2

let set1ObjectTeam1, set2ObjectTeam1, set3ObjectTeam1
let set1ObjectTeam2, set2ObjectTeam2, set3ObjectTeam2

var sets
var points1, currentGames1, games1Set1, games1Set2, games1Set3
var points2, currentGames2, games2Set1, games2Set2, games2Set3

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

        if (sets == 1)   {
            set2ObjectTeam1.style.visibility  = "visible"
            set2ObjectTeam2.style.visibility  = "visible"
            if (games1Set1 > games2Set1) {
                set1ObjectTeam1.style.color  = "#FEDF2D"
            }
            else {
                set1ObjectTeam2.style.color  = "#FEDF2D"
            }
        }   

        if (sets == 2)   {
            set3ObjectTeam1.style.visibility  = "visible"
            set3ObjectTeam2.style.visibility  = "visible"
            if (games1Set2 > games2Set2) {
                set2ObjectTeam1.style.color  = "#FEDF2D"
            }
            else {
                set2ObjectTeam2.style.color  = "#FEDF2D"
            }
        }

        if (sets == 3)   {
            if (games1Set3 > games2Set3) {
                set3ObjectTeam1.style.color  = "#FEDF2D"
            }
            else {
                set3ObjectTeam2.style.color  = "#FEDF2D"
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
            set2ObjectTeam1.style.visibility  = "visible"
            set2ObjectTeam2.style.visibility  = "visible"
            if (games1Set1 > games2Set1) {
                set1ObjectTeam1.style.color  = "#FEDF2D"
            }
            else {
                set1ObjectTeam2.style.color  = "#FEDF2D"
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

    set1ObjectTeam1 = document.querySelector('.o-set1-1')
    set2ObjectTeam1 = document.querySelector('.o-set2-1')
    set3ObjectTeam1 = document.querySelector('.o-set3-1')
    set1ObjectTeam2 = document.querySelector('.o-set1-2')
    set2ObjectTeam2 = document.querySelector('.o-set2-2')
    set3ObjectTeam2 = document.querySelector('.o-set3-2')
    // gamesObject1 = document.querySelector('.o-games-1')
    // gamesObject2 = document.querySelector('.o-games-2')
    // setsObject1 = document.querySelector('.o-sets-1')
    // setsObject2 = document.querySelector('.o-sets-2')

    console.log(window.location.hostname)
    listenToSocket()
     
}

document.addEventListener('DOMContentLoaded', function () {
    init();
})