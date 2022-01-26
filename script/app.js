'use strict'

const lanIP = `${window.location.hostname}:5000`;
const socketio = io(`http://${lanIP}`);

let scoreboardPage, servePage, winnerPage, loaderPage;

// Html elements
var pointsTeam1, currentGames1, gamesSet1Team1, gamesSet2Team1, gamesSet3Team1, setsTeam1;
var pointsTeam2, currentGames2, gamesSet1Team2, gamesSet2Team2, gamesSet3Team2, setsTeam2;

var sets;
var points1, currentGames1, games1Set1, games1Set2, games1Set3;
var points2, currentGames2, games2Set1, games2Set2, games2Set3;

// Welk team is aan de beurt om te serveren
var stateService;

// Is er al iemand gestart met serveren?
var serviceStart =  false;

// Is er connectie met de esp?
var stateConnection = 0;

// Html elements service
let serveTeam1, serveTeam2;

// Html elements winnerpage
let winnerTeam, winnerTeamBg;
let pointsWinner1, pointsWinner2;

// Clock
let hoursElement, minutesElement;
var hours = 0, minutes = 0;

// Form
let button, macAddress;
var macAddressValue;

function listenToSocket () {
    socketio.on('B2F_esp_no_connection', function () {
        console.log('No esp connection');
        scoreboardPage.style.display = "none";
        servePage.style.display = "none";
        winnerPage.style.display = "none";
        loaderPage.style.display = "block";
    })
    socketio.on('B2F_esp_connection', function () {
        console.log('Esp connected');
        if (serviceStart == false) {
            // document.html.style.backgroundColor = "red";
            scoreboardPage.style.display = "none";
            loaderPage.style.display = "none";
            servePage.style.display = "block";
            document.body.style.background = "#FEC941";
            console.log("Connected, er moet nog een eerste punt gespeeld worden")
        }
        else {
            loaderPage.style.display = "none";
            servePage.style.display = "none";
            scoreboardPage.style.display = "block";
            document.body.style.background = "#5EAFE7"
            console.log("Connected, wedstrijd kan verder gespeeld worden")
        }     
        setInterval(timerFunction, 1000);   
    })
    socketio.on('B2F_serve', function (payload) {
        serviceStart = true;
        servePage.style.display = "none";
        scoreboardPage.style.display = "block";
        document.body.style.background = "#5EAFE7"
        //laad scoreboard pagina
        if (payload == true) {
            console.log("team rood mag beginnen met serveren.");
            serveTeam1.style.visibility = "visible";
            serveTeam2.style.visibility = "hidden";
            //padelbal in scoreboard aanpassen naar rode team
        }
        else if (payload == false) {
            console.log("team blauw mag beginnen met serveren.");
            serveTeam1.style.visibility = "hidden";
            serveTeam2.style.visibility = "visible";
            //padelbal in scoreboard aanpassen naar blauwe team
        }
        // Match begint hier, dus timer mag gestart worden
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
                    pointsWinner1.innerHTML = `<ul class="c-points"><li class="u-yellow">${games1Set1}</li><li class="u-yellow">${games1Set2}</li></ul>`;
                    pointsWinner2.innerHTML = `<ul class="c-points"><li>${games2Set1}</li><li>${games2Set2}</li></ul>`;
                }
                else {
                    gamesSet2Team2.style.color  = "#FEDF2D";
                    winnerTeam.innerHTML = "Blue";
                    winnerTeamBg.style.backgroundColor = "#2d3cfe";
                    pointsWinner1.innerHTML = `<ul class="c-points"><li>${games1Set1}</li><li>${games1Set2}</li></ul>`;
                    pointsWinner2.innerHTML = `<ul class="c-points"><li class="u-yellow">${games2Set1}</li><li class="u-yellow">${games2Set2+1}</li></ul>`;
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
                gamesSet2Team1.style.color  = "#FEDF2D";
                winnerTeam.innerHTML = "Red";
                winnerTeamBg.style.backgroundColor = "#fe2d2d"; // `<h1>${games1Set1}</h1><h1>${games1Set2+1}</h1>`
                if (games1Set1 > games2Set1) {
                    pointsWinner1.innerHTML = `<ul class="c-points"><li class="u-yellow">${games1Set1}</li><li>${games1Set2}</li><li class="u-yellow">${games1Set3}</li></ul>`;
                    pointsWinner2.innerHTML = `<ul class="c-points"><li>${games2Set1}</li><li class="u-yellow">${games2Set2}</li><li>${games2Set3}</li></ul>`;
                }
                else {
                    pointsWinner1.innerHTML = `<ul class="c-points"><li>${games1Set1}</li><li class="u-yellow">${games1Set2}</li><li class="u-yellow">${games1Set3}</li></ul>`;
                    pointsWinner2.innerHTML = `<ul class="c-points"><li class="u-yellow">${games2Set1}</li><li>${games2Set2}</li><li>${games2Set3}</li></ul>`;
                }
            }
            else {
                gamesSet2Team2.style.color  = "#FEDF2D";
                winnerTeam.innerHTML = "Blue";
                winnerTeamBg.style.backgroundColor = "#2d3cfe";
                if (games1Set1 > games2Set1) {
                    pointsWinner1.innerHTML = `<ul class="c-points"><li class="u-yellow">${games1Set1}</li><li>${games1Set2}</li><li>${games1Set3}</li></ul>`;
                    pointsWinner2.innerHTML = `<ul class="c-points"><li>${games2Set1}</li><li class="u-yellow">${games2Set2}</li><li class="u-yellow">${games2Set3+1}</li></ul>`;
                }
                else {
                    pointsWinner1.innerHTML = `<ul class="c-points"><li>${games1Set1}</li><li class="u-yellow">${games1Set2}</li><li>${games1Set3}</li></ul>`;
                    pointsWinner2.innerHTML = `<ul class="c-points"><li class="u-yellow">${games2Set1}</li><li>${games2Set2}</li><li class="u-yellow">${games2Set3+1}</li></ul>`;
                }
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
    socketio.on('B2F_reset', function () {

        gamesSet1Team1.style.color  = "#FFFFFF";
        gamesSet2Team1.style.color  = "#FFFFFF";
        gamesSet3Team1.style.color  = "#FFFFFF";

        gamesSet1Team2.style.color  = "#FFFFFF";
        gamesSet2Team2.style.color  = "#FFFFFF";
        gamesSet3Team2.style.color  = "#FFFFFF";

        gamesSet2Team1.style.display = "none";
        gamesSet2Team2.style.display = "none";
        gamesSet3Team1.style.display = "none";
        gamesSet3Team2.style.display = "none";

        // serveTeam1.style.visibility = "hidden";
        // serveTeam2.style.visibility = "hidden";

        scoreboardPage.style.display = "none"
        winnerPage.style.display = "none"
        servePage.style.display = "block"

        document.body.style.background = "#FEC941"

    });
}

function listenToUI () {
    button.addEventListener('click', function () {
        macAddressValue = macAddress.value;
        console.log(macAddressValue);
        socketio.emit('F2B_mac', {'MAC': macAddressValue})
    });
}

function timerFunction() {
    const today = new Date();
    hours = today.getHours();
    minutes = today.getMinutes();
    hoursElement.innerHTML = hours;
    minutesElement.innerHTML = minutes.toLocaleString('en-US', {minimumIntegerDigits: 2,useGrouping: false});
}

function init () {
    scoreboardPage = document.querySelector('.js-scoreboard-page');
    servePage = document.querySelector('.js-serve-page');
    winnerPage = document.querySelector('.js-winner-page');
    loaderPage = document.querySelector('.js-loader-page');

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

    button = document.querySelector('.js-button-form');
    macAddress = document.querySelector('.js-mac');

    // console.log(window.location.hostname)
    listenToSocket();
    // listenToUI();
     
}

document.addEventListener('DOMContentLoaded', function () {
    init();
})