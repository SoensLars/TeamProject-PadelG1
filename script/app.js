'use strict'

const lanIP = `${window.location.hostname}:5000`;
const socketio = io(`http://${lanIP}`);

let scoreboardPage, servePage, winnerPage;

var pointsTeam1, currentGames1, gamesSet1Team1, gamesSet2Team1, gamesSet3Team1, setsTeam1;
var pointsTeam2, currentGames2, gamesSet1Team2, gamesSet2Team2, gamesSet3Team2, setsTeam2;

var sets;
var points1, currentGames1, games1Set1, games1Set2, games1Set3;
var points2, currentGames2, games2Set1, games2Set2, games2Set3;
var stateService;
var stateConnection = 0;

let serveTeam1, serveTeam2;
let winnerTeam, winnerTeamBg;
let pointsWinner1, pointsWinner2;

// Timer
let hoursElement, minutesElement;
var hours = 0, minutes = -1;

function listenToSocket () {
    socketio.on('B2F_esp_no_connection', function () {
        console.log('No esp connection');
    })
    socketio.on('B2F_esp_connection', function () {
        console.log('Esp connected');
        if (stateConnection == 0) {
            window.location.href = "pages/scoreboard.html";
            stateConnection = 1;
            console.log("Connected for the first time");
        }
        else {
            console.log("Loading screen");
        }        
    })
    socketio.on('B2F_serve', function (payload) {
        servePage.style.display = "none";
        scoreboardPage.style.display = "block";
        //laad scoreboard pagina
        if (payload == true) {
            console.log("team rood mag beginnen met serveren.");
            serveTeam1.style.visibility = "visible";
            //padelbal in scoreboard aanpassen naar rode team
        }
        else if (payload == false) {
            console.log("team blauw mag beginnen met serveren.");
            serveTeam2.style.visibility = "visible";
            //padelbal in scoreboard aanpassen naar blauwe team
        }
        // Match begint hier, dus timer mag gestart worden
        setInterval(timerFunction, 60000);
    })
    socketio.on('B2F_points_team1', function (payload) {
        // Punten in scoreboard weergeven
        points1 = payload['points'];
        currentGames1 = payload['games'];
        games1Set1 = payload['gamesSet1'];
        games1Set2 = payload['gamesSet2'];
        games1Set3 = payload['gamesSet3'];
        sets = payload['sets'];
        stateService = payload['stateService'];
        console.log(`State service is ${stateService}`);
        pointsTeam1.innerHTML = points1;
        gamesSet1Team1.innerHTML = games1Set1;
        gamesSet2Team1.innerHTML = games1Set2;
        gamesSet3Team1.innerHTML = games1Set3;

        // Games van set 2 weergeven
        if (sets == 1)   {
            gamesSet2Team1.style.display  = "block";
            gamesSet2Team2.style.display  = "block";
            if (games1Set1 > games2Set1) {
                gamesSet1Team1.style.color  = "#FEDF2D";
            }
            else {
                gamesSet1Team2.style.color  = "#FEDF2D";
            }
        }   

        // Games van set 3 weergeven indien de match niet beindigd is
        if (sets == 2)   {
            // Match is beindigd
            if ((games1Set1 > games2Set1 && games1Set2 > games2Set2) || (games2Set1 > games1Set1 && games2Set2 > games1Set2)) {
                gamesSet3Team1.style.display  = "hidden";
                gamesSet3Team2.style.display  = "hidden";
                scoreboardPage.style.display = "none";
                winnerPage.style.display = "block";
                if (games1Set2 > games2Set2) {
                    gamesSet2Team1.style.color  = "#FEDF2D";
                    winnerTeam.innerHTML = "Red";
                    winnerTeamBg.style.backgroundColor = "#fe2d2d"; // `<h1>${games1Set1}</h1><h1>${games1Set2+1}</h1>`
                    pointsWinner1.innerHTML = `<ul class="c-points"><li>${games1Set1}</li><li>${games1Set2}</li></ul>`;
                    pointsWinner2.innerHTML = `<ul class="c-points"><li>${games2Set1}</li><li>${games2Set2}</li></ul>`;
                }
                else {
                    gamesSet2Team2.style.color  = "#FEDF2D";
                    winnerTeam.innerHTML = "Blue";
                    winnerTeamBg.style.backgroundColor = "#2d3cfe";
                    pointsWinner1.innerHTML = `<ul class="c-points"><li>${games1Set1}</li><li>${games1Set2}</li></ul>`;
                    pointsWinner2.innerHTML = `<ul class="c-points"><li>${games2Set1}</li><li>${games2Set2}</li></ul>`;
                }
            }
            // Match is nog niet beindigd
            else {
                gamesSet3Team1.style.display  = "block";
                gamesSet3Team2.style.display  = "block";
                if (games1Set2 > games2Set2) {
                    gamesSet2Team1.style.color  = "#FEDF2D";
                }
                else {
                    gamesSet2Team2.style.color  = "#FEDF2D";
                }
            }
        }

        if (sets == 3)   {
            scoreboardPage.style.display = "none";
            winnerPage.style.display = "block";
            if (games1Set3 > games2Set3) {
                gamesSet3Team1.style.color  = "#FEDF2D";
                winnerTeam.innerHTML = "Red";
                winnerteamBg.style.backgroundColor = "#fe2d2d";
                pointsWinner1.innerHTML = `<ul class="c-points"><li>${games1Set1}</li><li>${games1Set2}</li><li>${games1Set3+1}</li></ul>`;
                pointsWinner2.innerHTML = `<ul class="c-points"><li>${games2Set1}</li><li>${games2Set2}</li><li>${games2Set3}</li></ul>`;
            }
            else {
                gamesSet3Team2.style.color  = "#FEDF2D";
                winnerTeam.innerHTML = "Blue";
                winnerTeamBg.style.backgroundColor = "#2d3cfe";
                pointsWinner1.innerHTML = `<ul class="c-points"><li>${games1Set1}</li><li>${games1Set2}</li><li>${games1Set3}</li></ul>`;
                pointsWinner2.innerHTML = `<ul class="c-points"><li>${games2Set1}</li><li>${games2Set2}</li><li>${games2Set3+1}</li></ul>`;
            }
        }

        if (stateService == true) {
            serveTeam1.style.visibility = "visible";
            serveTeam2.style.visibility = "hidden";
        }
        else {
            serveTeam1.style.visibility = "hidden";
            serveTeam2.style.visibility = "visible";
        }
    });
    socketio.on('B2F_points_team2', function (payload) {
        points2 = payload['points'];
        currentGames1 = payload['games'];
        games2Set1 = payload['gamesSet1'];
        games2Set2 = payload['gamesSet2'];
        games2Set3 = payload['gamesSet3'];
        sets = payload['sets']
        stateService = payload['stateService'];
        pointsTeam2.innerHTML = points2;
        gamesSet1Team2.innerHTML = games2Set1;
        gamesSet2Team2.innerHTML = games2Set2;
        gamesSet3Team2.innerHTML = games2Set3;


        if (sets == 1)   {
            gamesSet2Team1.style.display  = "block";
            gamesSet2Team2.style.display  = "block";
            if (games1Set1 > games2Set1) {
                gamesSet1Team1.style.color  = "#FEDF2D";
            }
            else {
                gamesSet1Team2.style.color  = "#FEDF2D";
            }
        }   

        if (sets == 2)   {
            if ((games1Set1 > games2Set1 && games1Set2 > games2Set2) || (games2Set1 > games1Set1 && games2Set2 > games1Set2)) {
                gamesSet3Team1.style.display  = "hidden";
                gamesSet3Team2.style.display  = "hidden";
                if (games1Set2 > games2Set2) {
                    gamesSet2Team1.style.color  = "#FEDF2D";
                }
                else {
                    gamesSet2Team2.style.color  = "#FEDF2D";
                }
            }
            else {
                gamesSet3Team1.style.display  = "block";
                gamesSet3Team2.style.display  = "block";
                if (games1Set2 > games2Set2) {
                    gamesSet2Team1.style.color  = "#FEDF2D";
                }
                else {
                    gamesSet2Team2.style.color  = "#FEDF2D";
                }
            }
        }

        if (sets == 3)   {
            if (games1Set3 > games2Set3) {
                gamesSet3Team1.style.color  = "#FEDF2D";
            }
            else {
                gamesSet3Team2.style.color  = "#FEDF2D";
            }
        }  

        if (stateService == true) {
            serveTeam1.style.visibility = "visible";
            serveTeam2.style.visibility = "hidden";
        }
        else {
            serveTeam1.style.visibility = "hidden";
            serveTeam2.style.visibility = "visible";
        }
    });
}

function timerFunction() {
    if (minutes != 59) {
        minutes += 1;
    }
    else {
        minutes = 0;
        hours += 1;
    }
    hoursElement.innerHTML = hours;
    minutesElement.innerHTML = minutes.toLocaleString('en-US', {minimumIntegerDigits: 2,useGrouping: false});
}

function init () {
    scoreboardPage = document.querySelector('.js-scoreboard-page');
    servePage = document.querySelector('.js-serve-page');
    winnerPage = document.querySelector('.js-winner-page');

    pointsTeam1 = document.querySelector('.js-points-1');
    currentGames1 = document.querySelector('.js-games-1');
    gamesSet1Team1 = document.querySelector('.js-games-set1-1');
    gamesSet2Team1 = document.querySelector('.js-games-set2-1');
    gamesSet3Team1 = document.querySelector('.js-games-set3-1');

    pointsTeam2 = document.querySelector('.js-points-2');
    currentGames2 = document.querySelector('.js-games-2');
    gamesSet1Team2 = document.querySelector('.js-games-set1-2');
    gamesSet2Team2 = document.querySelector('.js-games-set2-2');
    gamesSet3Team2 = document.querySelector('.js-games-set3-2');

    serveTeam1 = document.querySelector('.js-serve-1');
    serveTeam2 = document.querySelector('.js-serve-2');

    pointsWinner1 = document.querySelector('.js-points--winner-1');
    pointsWinner2 = document.querySelector('.js-points--winner-2');

    winnerTeam = document.querySelector('.js-winner-team');
    winnerTeamBg = document.querySelector('.js-winner-bg');

    hoursElement = document.querySelector('.js-hours');
    minutesElement = document.querySelector('.js-minutes');

    // console.log(window.location.hostname)
    listenToSocket();
     
}

document.addEventListener('DOMContentLoaded', function () {
    init();
})