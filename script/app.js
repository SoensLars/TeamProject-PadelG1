'use strict'

const lanIP = `${window.location.hostname}:5000`;
const socketio = io(`http://${lanIP}`);

let scoreboardPage, servePage, loaderPage, sponsorPage, clubPage;

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
var stateConnection = true;

// Is de game al beëindigd?
var stateMatch = false

// Html elements service
let serveTeam1, serveTeam2;

// Html elements trophy
let trophy1win, trophy2win, trophy1lose, trophy2lose

// Clock
let hoursElement, minutesElement;
var hours = 0, minutes = 0;

// Timer
let timerElement;
var seconds = 31;

function listenToSocket () {
    socketio.on('B2F_esp_no_connection', function () {
        console.log('No esp connection');
        stateConnection = false;
        if (stateMatch != true) {
            scoreboardPage.style.display = "none";
            servePage.style.display = "none";
            clubPage.style.display = "none";
            loaderPage.style.display = "block";
            document.body.style.background = "#5EAFE7";
        }
        else {
            console.log("Show clubpagina");
        }
    })
    socketio.on('B2F_esp_connection', function () {
        console.log('Esp connected');
        stateConnection = true;
        if (serviceStart == false) {
            // document.html.style.backgroundColor = "red";
            scoreboardPage.style.display = "none";
            loaderPage.style.display = "none";
            servePage.style.display = "block";
            document.body.style.background = "#FEC941";
            console.log("Connected, er moet nog een eerste punt gespeeld worden");
        }
        else {
            if (stateMatch == false) {
                loaderPage.style.display = "none";
                servePage.style.display = "none";
                scoreboardPage.style.display = "block";
                clubPage.style.display = "none";
                document.body.style.background = "#5EAFE7";
                console.log("Connected, wedstrijd kan verder gespeeld worden");
            }
            else {
                loaderPage.style.display = "none";
                servePage.style.display = "none";
                scoreboardPage.style.display = "none";
                clubPage.style.display = "block";
                document.body.style.background = "#FEC941";
                console.log("Connected, clubpage wordt getoond");
            }
        }       
    });
    socketio.on('B2F_serve', function (payload) {
        serviceStart = true;
        servePage.style.display = "none";
        scoreboardPage.style.display = "block";
        document.body.style.background = "#5EAFE7";
        // laad scoreboard pagina
        if (payload == true) {
            console.log("team rood mag beginnen met serveren.");
            serveTeam1.style.visibility = "visible";
            serveTeam2.style.visibility = "hidden";
            // padelbal in scoreboard aanpassen naar rode team
        }
        else if (payload == false) {
            console.log("team blauw mag beginnen met serveren.");
            serveTeam1.style.visibility = "hidden";
            serveTeam2.style.visibility = "visible";
            // padelbal in scoreboard aanpassen naar blauwe team
        }
    });
    socketio.on('B2F_points_team1', function (payload) {
        // Punten in scoreboard weergeven
        points1 = payload['points'];
        currentGames1 = payload['games'];
        games1Set1 = payload['gamesSet1'];
        games1Set2 = payload['gamesSet2'];
        games1Set3 = payload['gamesSet3'];
        sets = payload['sets'];
        stateService = payload['stateService'];
        pointsTeam1.innerHTML = points1;
        gamesSet1Team1.innerHTML = games1Set1;
        gamesSet2Team1.innerHTML = games1Set2;
        gamesSet3Team1.innerHTML = games1Set3;

        // Games van set 2 weergeven
        if (sets == 0)   {
            stateMatch = false;

            gamesSet2Team1.style.display  = "none";
            gamesSet2Team2.style.display  = "none";
            gamesSet1Team1.style.color  = "#FFFFFF";
            gamesSet1Team2.style.color  = "#FFFFFF";
        } 

        if (sets == 1)   {
            stateMatch = false;
            scoreboardPage.style.display = "block";

            gamesSet2Team1.style.display  = "block";
            gamesSet2Team2.style.display  = "block";
            gamesSet3Team1.style.display  = "none";
            gamesSet3Team2.style.display  = "none";
            gamesSet2Team1.style.color  = "#FFFFFF";
            gamesSet2Team2.style.color  = "#FFFFFF";
            if (games1Set1 > games2Set1) {
                gamesSet1Team1.style.color  = "#fec941";
            }
            else {
                gamesSet1Team2.style.color  = "#fec941";
            }
        }   

        // Games van set 3 weergeven indien de match niet beindigd is
        if (sets == 2)   {
            scoreboardPage.style.display = "block";
            // Match is beindigd
            if ((games1Set1 > games2Set1 && games1Set2 > games2Set2) || (games2Set1 > games1Set1 && games2Set2 > games1Set2)) {
                stateMatch = true;
                gamesSet3Team1.style.display  = "none";
                gamesSet3Team2.style.display  = "none";
                serveTeam1.style.display = "none";
                serveTeam2.style.display = "none";
                if (games1Set2 > games2Set2) {
                    // rood wint
                    trophy1win.style.display = "block";
                    trophy2win.style.display = "none";
                    trophy1lose.style.display = "none";
                    trophy2lose.style.display = "block";
                    gamesSet2Team1.style.color  = "#fec941";
                }
                else {
                    // blauw wint
                    trophy1win.style.display = "none";
                    trophy2win.style.display = "block";
                    trophy1lose.style.display = "block";
                    trophy2lose.style.display = "none";
                    gamesSet2Team2.style.color  = "#fec941";
                }
            }
            // Match is nog niet beindigd
            else {
                stateMatch = false;
                gamesSet3Team1.style.display  = "block";
                gamesSet3Team2.style.display  = "block";
                gamesSet3Team1.style.color  = "#FFFFFF";
                gamesSet3Team2.style.color  = "#FFFFFF";
                if (games1Set2 > games2Set2) {
                    gamesSet2Team1.style.color  = "#fec941";
                }
                else {
                    gamesSet2Team2.style.color  = "#fec941";
                }
            }
        }

        if (sets == 3)   {
            stateMatch = true;
            serveTeam1.style.display = "none";
            serveTeam2.style.display = "none";
            if (games1Set3 > games2Set3) {
                trophy1win.style.display = "block";
                trophy2win.style.display = "none";
                trophy1lose.style.display = "none";
                trophy2lose.style.display = "block";
                gamesSet3Team1.style.color  = "#fec941";
            }
            else {
                trophy1win.style.display = "none";
                trophy2win.style.display = "block";
                trophy1lose.style.display = "block";
                trophy2lose.style.display = "none";
                gamesSet3Team2.style.color  = "#fec941";
            }
        }

        if (stateService == true) {
            if (stateMatch != true) {
                trophy1win.style.display = "none";
                trophy2win.style.display = "none";
                trophy1lose.style.display = "none";
                trophy2lose.style.display = "none";

                serveTeam1.style.display = "block";
                serveTeam2.style.display = "block";
                serveTeam1.style.visibility = "visible";
                serveTeam2.style.visibility = "hidden";
            }
            else {
                serveTeam1.style.display = "none";
                serveTeam2.style.display = "none";
            }
        }
        else {
            if (stateMatch != true) {
                trophy1win.style.display = "none";
                trophy2win.style.display = "none";
                trophy1lose.style.display = "none";
                trophy2lose.style.display = "none";

                serveTeam1.style.display = "block";
                serveTeam2.style.display = "block";
                serveTeam1.style.visibility = "hidden";
                serveTeam2.style.visibility = "visible";
            }
            else {
                serveTeam1.style.display = "none";
                serveTeam2.style.display = "none";
            }
        }
    });
    socketio.on('B2F_points_team2', function (payload) {
        points2 = payload['points'];
        currentGames1 = payload['games'];
        games2Set1 = payload['gamesSet1'];
        games2Set2 = payload['gamesSet2'];
        games2Set3 = payload['gamesSet3'];
        sets = payload['sets'];
        stateService = payload['stateService'];
        pointsTeam2.innerHTML = points2;
        gamesSet1Team2.innerHTML = games2Set1;
        gamesSet2Team2.innerHTML = games2Set2;
        gamesSet3Team2.innerHTML = games2Set3;


        // Games van set 2 weergeven
        if (sets == 0)   {
            stateMatch = false;

            gamesSet2Team1.style.display  = "none";
            gamesSet2Team2.style.display  = "none";
            gamesSet1Team1.style.color  = "#FFFFFF";
            gamesSet1Team2.style.color  = "#FFFFFF";
        } 

        if (sets == 1)   {
            stateMatch = false;
            scoreboardPage.style.display = "block";

            gamesSet2Team1.style.display  = "block";
            gamesSet2Team2.style.display  = "block";
            gamesSet3Team1.style.display  = "none";
            gamesSet3Team2.style.display  = "none";
            gamesSet2Team1.style.color  = "#FFFFFF";
            gamesSet2Team2.style.color  = "#FFFFFF";
            if (games1Set1 > games2Set1) {
                gamesSet1Team1.style.color  = "#fec941";
            }
            else {
                gamesSet1Team2.style.color  = "#fec941";
            }
        }   

        // Games van set 3 weergeven indien de match niet beindigd is
        if (sets == 2)   {
            scoreboardPage.style.display = "block";
            // Match is beindigd
            if ((games1Set1 > games2Set1 && games1Set2 > games2Set2) || (games2Set1 > games1Set1 && games2Set2 > games1Set2)) {
                stateMatch = true;
                gamesSet3Team1.style.display  = "none";
                gamesSet3Team2.style.display  = "none";
                serveTeam1.style.display = "none";
                serveTeam2.style.display = "none";
                if (games1Set2 > games2Set2) {
                    // rood wint
                    trophy1win.style.display = "block";
                    trophy2win.style.display = "none";
                    trophy1lose.style.display = "none";
                    trophy2lose.style.display = "block";
                    gamesSet2Team1.style.color  = "#fec941";
                }
                else {
                    // blauw wint
                    trophy1win.style.display = "none";
                    trophy2win.style.display = "block";
                    trophy1lose.style.display = "block";
                    trophy2lose.style.display = "none";
                    gamesSet2Team2.style.color  = "#fec941";
                }
            }
            // Match is nog niet beindigd
            else {
                stateMatch = false;
                gamesSet3Team1.style.display  = "block";
                gamesSet3Team2.style.display  = "block";
                gamesSet3Team1.style.color  = "#FFFFFF";
                gamesSet3Team2.style.color  = "#FFFFFF";
                if (games1Set2 > games2Set2) {
                    gamesSet2Team1.style.color  = "#fec941";
                }
                else {
                    gamesSet2Team2.style.color  = "#fec941";
                }
            }
        }

        if (sets == 3)   {
            stateMatch = true;
            serveTeam1.style.display = "none";
            serveTeam2.style.display = "none";
            if (games1Set3 > games2Set3) {
                trophy1win.style.display = "block";
                trophy2win.style.display = "none";
                trophy1lose.style.display = "none";
                trophy2lose.style.display = "block";
                gamesSet3Team1.style.color  = "#fec941";
            }
            else {
                trophy1win.style.display = "none";
                trophy2win.style.display = "block";
                trophy1lose.style.display = "block";
                trophy2lose.style.display = "none";
                gamesSet3Team2.style.color  = "#fec941";
            }
        }

        if (stateService == true) {
            if (stateMatch != true) {
                trophy1win.style.display = "none";
                trophy2win.style.display = "none";
                trophy1lose.style.display = "none";
                trophy2lose.style.display = "none";

                serveTeam1.style.display = "block";
                serveTeam2.style.display = "block";
                serveTeam1.style.visibility = "visible";
                serveTeam2.style.visibility = "hidden";
            }
            else {
                serveTeam1.style.display = "none";
                serveTeam2.style.display = "none";
            }
        }
        else {
            if (stateMatch != true) {
                trophy1win.style.display = "none";
                trophy2win.style.display = "none";
                trophy1lose.style.display = "none";
                trophy2lose.style.display = "none";

                serveTeam1.style.display = "block";
                serveTeam2.style.display = "block";
                serveTeam1.style.visibility = "hidden";
                serveTeam2.style.visibility = "visible";
            }
            else {
                serveTeam1.style.display = "none";
                serveTeam2.style.display = "none";
            }
        }
    });
    socketio.on('B2F_show_sponsors', function () {
        setTimeout(() => { 
            seconds = 31
            document.body.style.background = "#fec941";
            scoreboardPage.style.display = "none";
            sponsorPage.style.display = "block";         
        }, 5000);
    });
    socketio.on('B2F_hide_sponsors', function () {
        document.body.style.background = "#5eafe7";
        scoreboardPage.style.display = "block";
        sponsorPage.style.display = "none";
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
        trophy1win.style.display = "none"
        trophy2win.style.display = "none"
        trophy1lose.style.display = "none"
        trophy2lose.style.display = "none"
        serveTeam1.style.display = "block";
        serveTeam2.style.display = "block";
        serviceStart = false;
        stateMatch = false;

        if (stateConnection == true) {
            scoreboardPage.style.display = "none";
            loaderPage.style.display = "none";
            clubPage.style.display = "none";
            sponsorPage.style.display = "none";
            servePage.style.display = "block";

            document.body.style.background = "#FEC941";
        }
        else {
            scoreboardPage.style.display = "none";
            loaderPage.style.display = "block";
            clubPage.style.display = "none";
            sponsorPage.style.display = "none";
            servePage.style.display = "none";

            document.body.style.background = "#5EAFE7";
        }
    });
    socketio.on('B2F_club_page', function () {
        scoreboardPage.style.display = "none";
        winnerPage.style.display = "none";
        clubPage.style.display = "block";
        sponsorPage.style.display = "none";
        servePage.style.display = "none";

        document.body.style.background = "#FEC941"
    });
}

function timerFunction () {
    const today = new Date();
    hours = today.getHours();
    minutes = today.getMinutes();
    hoursElement.innerHTML = hours;
    minutesElement.innerHTML = minutes.toLocaleString('en-US', {minimumIntegerDigits: 2,useGrouping: false});
}

function countdownFunction () {
    seconds -= 1;
    timerElement.innerHTML = seconds;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function init () {
    scoreboardPage = document.querySelector('.js-scoreboard-page');
    servePage = document.querySelector('.js-serve-page');
    loaderPage = document.querySelector('.js-loader-page');
    sponsorPage = document.querySelector('.js-sponsor-page');
    clubPage = document.querySelector('.js-club-page');

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

    trophy1win = document.querySelector('.js-trophy-1-win');
    trophy2win = document.querySelector('.js-trophy-2-win');
    trophy1lose = document.querySelector('.js-trophy-1-lose');
    trophy2lose = document.querySelector('.js-trophy-2-lose');

    hoursElement = document.querySelector('.js-hours');
    minutesElement = document.querySelector('.js-minutes');

    timerElement = document.querySelector('.js-countdown');

    listenToSocket();
    setInterval(timerFunction, 1000); 
    setInterval(countdownFunction, 1000);     
}

document.addEventListener('DOMContentLoaded', function () {
    init();
})