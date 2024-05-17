document.addEventListener('DOMContentLoaded', () => {
    /*
     * Code specific to the scoreboard page
     */
    if (window.location.pathname == '/scoreboard' ) {
        const universityFilter = document.getElementById('university-filter');
        const tableRows = document.querySelectorAll('tbody tr');

        universityFilter.addEventListener('change', () => {
            const filterValue = universityFilter.value.trim().toLowerCase();
            tableRows.forEach(row => {
                const universityId = row.querySelector('.university-id').getAttribute("university").trim().toLowerCase();
                if (filterValue === '' || universityId === filterValue) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
        manageScoreboard();
    }

    /*
     * Code specific to the challenge overview page
     */
    if (window.location.pathname == '/challenges') {
        for (img of document.querySelectorAll("img")) {
            img.addEventListener('error', function () { this.src='https://picsum.photos/536/354' });
        }
    }

    /*
     * Code specific to the challenge category page
     */
    if (window.location.pathname.startsWith('/challenges/')) {
        document.getElementById("difficulty-filter").addEventListener('change', function () { showSelectedDifficulty() });
        for (form of document.querySelectorAll("form")) {
            form.addEventListener('submit', handleChallengeSubmission);
        }

        document.querySelectorAll("button").forEach((button) => {
          if (button.id.startsWith("start_service")) { 
            var id = button.id.split('_')[2]
            button.addEventListener("click", (_) => startService(id))
          } else if (button.id.startsWith("stop_service")) {
            var id = button.id.split('_')[2]
            button.addEventListener("click", (_) => stopService(id))
            refreshService(id);
          }
        })
    }

    /*
     * Code specific to the player profile page
     */
    if (window.location.pathname == "/profile") {
        document.getElementById("university").addEventListener('change', function () {
            fetch('/api/profile/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'university=' + encodeURIComponent(document.getElementById('university').value)
            });
        });
    }
    if (window.location.pathname.startsWith("/profile")) {
        const profileChartCtx = document.getElementById('profile_chart');
        if (profileChartCtx != null) drawProfileChart(profileChartCtx);
    }

    /*
     * Code specific to the writeup editor.
     */
    if (window.location.pathname.split("/").at(-1) == "editor") {
        document.getElementById("ack-button").addEventListener('click', function(event) {
            event.preventDefault();
            document.getElementById("editor-warning-message").textContent = "";
            document.getElementById("submit-writeup").classList.remove("btn-danger");
            document.getElementById("submit-writeup").classList.add("btn-light");
            document.getElementById("submit-writeup").textContent = "Done";
            document.getElementById("ack-button").classList.add("invisible");
        });

        document.getElementById("submit-writeup").addEventListener('click', function(event) {
            event.preventDefault();
            writeup_data = document.getElementById("writeup-editor").value;
            console.log(writeup_data);

            if (writeup_data == "" && !document.getElementById("submit-writeup").classList.contains("btn-danger")) {
                document.getElementById("editor-warning-message").textContent = "Your about to delete this writeup, are you sure?";
                document.getElementById("submit-writeup").classList.add("btn-danger");
                document.getElementById("submit-writeup").classList.remove("btn-light");
                document.getElementById("submit-writeup").textContent = "Upload anyway";
                document.getElementById("ack-button").classList.remove("invisible");
                return;
            }

            const formData = new FormData();
            const fileBlob = new Blob([writeup_data], { type: 'text/plain' });
            formData.append('file', fileBlob, "file");

            fetch(document.getElementById("submit-writeup").href, {
                method: 'POST',
                body: formData
            }).then((response) => response.text()).then((text) => {
                if (writeup_data == "") {
                    current_location = document.location.pathname;
                    document.location = current_location.substring(0, current_location.length - 7);
                } else {
                    document.location = text.substring(5);
                }
            });
        });

        document.getElementById("writeup-editor").addEventListener('input', function() {
            element = document.getElementById("writeup-editor");
            element.style.height = 'auto';
            element.style.height = (element.scrollHeight) + 'px';
        });


        // Trigger this once to set the initial size.
        element = document.getElementById("writeup-editor");
        element.style.height = 'auto';
        element.style.height = (element.scrollHeight) + 'px';
    }
});

function drawProfileChart(ctx) {
    //Get the user id from path
    const userId = document.getElementById("user-id").textContent;
    fetch("https://" + window.location.hostname + "/api/user/solves/" + userId)
    .then((response) => response.json()) //2
    .then((data) => {
      new Chart(ctx, {
          type: 'line',
          data: {
            datasets: [{
                label: 'Score', data: data
            }]
          },
          options: {
            scales: {
              y: {
                beginAtZero: true
              },
              x: {
                type: "time",
                time: {
                    unit: 'day',
                    displayFormats: {
                        minute: 'yyyy-mm-dd'
                    },
                },
                ticks: {
                    autoSkip: true, maxTicksLimit: 20
                },
                parsing: false
              }
            }
          }
        });
    });
}


function showSelectedDifficulty() {
    const challengeCategories = document.querySelectorAll('.challenge-category');

    const difficultyFilter = document.getElementById('difficulty-filter');
    const selectedDifficulty = difficultyFilter.options[difficultyFilter.selectedIndex].value;

    challengeCategories.forEach((category) => category.classList.remove('show-easy', 'show-medium', 'show-hard', 'show-all'));
    if (selectedDifficulty === 'all') {
        challengeCategories.forEach((category) => category.classList.add('show-all'));
    } else {
        for (let category of challengeCategories) {
            if (Array.from(category.querySelectorAll('.challenge')).find(
                    el => el.classList.contains(selectedDifficulty))
                ) {
                category.classList.add(`show-${selectedDifficulty}`)
            }
        }
    }
}


async function handleChallengeSubmission(event) {
    event.preventDefault();
    let form = event.target;
    let url = form.action;

    // Find challenge associated with submit
    let challengeId = form.getAttribute("challenge");

    let challenge = document.querySelector(`.challenge[id=\"${challengeId}\"]`);
    let inputField = form.children[0].children[0];
    let solvesText = challenge.getElementsByClassName("solves-count")[0];
    let challengeName = challenge.getElementsByClassName("accordion-button")[0];
    
    try {
        let response = await fetch(url, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json, text/html',
            },
            body: 'flag=' + inputField.value,
        });
        response.json().then(post => {
            if (post.status === 'OK') {
                inputField.style.backgroundColor = 'lightgreen';
                setTimeout(function(){
                    form.classList.add('d-none');
                    document.getElementById(challengeId + '-solved').classList.remove('d-none');
                }, 2000);
                var num = solvesText.textContent.split(' ')[0];
                solvesText.textContent = solvesText.textContent.replace(num, num * 1 + 1);
                challengeName.classList.add("solved");
            }
            else {
                inputField.style.backgroundColor = '#ff4040';
                setTimeout(function(){
                    inputField.style.backgroundColor = 'white';
                }, 2000);
            }     
        });   
    } catch (error) {
        console.log(error)
    }
}

function manageScoreboard() {
    const universityFilter = document.getElementById('university-filter');
    const tableRows = document.querySelectorAll('tbody tr');

    universityFilter.addEventListener('change', () => {
        const filterValue = universityFilter.value.trim().toLowerCase();
        tableRows.forEach(row => {
            const universityId = row.querySelector('.university-id').getAttribute("university").trim().toLowerCase();
            if (filterValue === '' || universityId === filterValue) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

async function startService(id) {
  var startButton = document.getElementById("start_service_" + id)
  var display = document.getElementById("status_display_" + id)

  async function start() {
    startButton.setAttribute("disabled", "disabled");
    var response = await fetch("/api/challenge/start/" + id, {method: "POST", cache: "no-cache"});
    var state = await response.json();
    state = state[0];
    display.innerHTML = state;
  }

  start();
  var interval = setInterval(async function () {
    if (display.innerText == "running") {
      clearInterval(interval);
      await refreshService(id);
    } else {
      await start()
    }
  }, 2000);
}

async function stopService(id) {
  var stopButton = document.getElementById("stop_service_" + id)
  var display = document.getElementById("status_display_" + id)

  async function stop() {
    stopButton.setAttribute("disabled", "disabled");
    var response = await fetch("/api/challenge/stop/" + id, {method: "POST", cache: "no-cache"});
    var state = await response.json();
    state = state[0]
    display.innerHTML = state;
  }

  stop();
  var interval = setInterval(async function () {
    if (display.innerText == "not running" || display.innerText == "stopped") {
      clearInterval(interval);
      await refreshService(id);
    } else {
      await stop()
    }
  }, 2000);
}

async function refreshService(id) {
  var response = await fetch("/api/challenge/status/" + id, {method: "POST", cache: "no-cache"});
  var json = await response.json();

  var startButton = document.getElementById("start_service_" + id)
  var stopButton = document.getElementById("stop_service_" + id)
  var url = document.getElementById("url_service_" + id).innerText
  var display = document.getElementById("status_display_" + id)

  var state = json["state"]
  if (state == "running") {
    startButton.setAttribute("disabled", "disabled");
    stopButton.removeAttribute("disabled");

    var challengeUrl = json["port"].split(":")
    var newUrl = url.replaceAll("{IP}", challengeUrl[0]);
    var newUrl = newUrl.replaceAll("{PORT}", challengeUrl[1]);
    display.innerHTML = newUrl;
  } else {
    stopButton.setAttribute("disabled", "disabled");
    startButton.removeAttribute("disabled");
    display.innerHTML = json["state"]
  }
}
