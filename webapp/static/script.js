document.addEventListener('DOMContentLoaded', () => {
    let challenges = document.getElementById('challenge_submission')
    if (challenges != null) manageChallanges(challenges);

    if (window.location.pathname.startsWith('/scoreboard')) {
        manageScoreboard();
    }

    const profileChartCtx = document.getElementById('profile_chart');
    if (profileChartCtx != null) drawProfileChart(profileChartCtx)
});

function drawProfileChart(ctx) {
    //Get the user id from path
    const userId = document.getElementById("user-id").textContent;
    fetch("https://" + window.location.hostname + "/api/user/solves/" + userId)
    .then((response) => response.json()) //2
    .then((data) => {
      console.log(data);
      new Chart(ctx, {
          type: 'line',
          data: {
            datasets: [{
                label: 'Score',
                data: data
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
                    unit: 'minute',
                    displayFormats: {
                        minute: 'yyyy-mm-dd'
                    },
                },
                ticks: {
                    autoSkip: true,
                    maxTicksLimit: 20
                },
                parsing: false
              }
            }
          }
        });
    });

}

function updateUniversity(update_url) {
    fetch(update_url, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'university=' + encodeURIComponent(document.getElementById('university').value)
    });
}

function manageChallanges(challenge_container) {

    //Make solves work properly
    const solves_links = document.querySelectorAll(".solves_link");
    for (let solves_link of solves_links) {
        solves_link.addEventListener('mouseenter', (e) => {
            let accordionButton = solves_link.closest(".accordion-button");
            accordionButton.setAttribute('data-bs-toggle', '');
        });
        solves_link.addEventListener('mouseleave', (e) => {
            let accordionButton = solves_link.closest(".accordion-button");
            accordionButton.setAttribute('data-bs-toggle', 'collapse');
        });
    }

    //find all of the challenges in a page
    let challenges = [];
    for (let accordion of challenge_container.children) {
        Array.from(accordion.children).forEach(x => {if (x.className == "accordion-item") challenges.push(x)});
    }

    //Assign difficulty filters
    let difficultyFilter = document.getElementById('difficulty-filter');
    challenges.forEach(challenge => {
        difficultyFilter.addEventListener('change', () => {
            challenge.style.display = '';
            
            let difficulty = difficultyFilter.value;
            if (challenge.getAttribute("difficulty")) {
                switch (difficulty) {
                    case 'easy':
                        if (challenge.getAttribute("difficulty") != "easy") {
                            challenge.style.display = 'none';
                        }
                        break;
                    case 'medium':
                        if (challenge.getAttribute("difficulty") != "medium") {
                            challenge.style.display = 'none';
                        }
                        break;
                    case 'hard':
                        if (challenge.getAttribute("difficulty") != "hard") {
                            challenge.style.display = 'none';
                        }
                        break;  
                    default: 
                        challenge.style.display = '';
                }
            };
        });
    });

    //allow submissions
    document.addEventListener('submit', async function (handleSubmit) {
        handleSubmit.preventDefault();
        let form = handleSubmit.target;
        let url = form.action;

        //find challenge assosiated with sumbit
        let challengeId = form.getAttribute("challenge");
        let challenge = challenges.find(x => x.id == challengeId);
        let inputField = form.children[0].children[0];
        let solvesText = challenge.getElementsByClassName("solves-count")[0];
        let challengeName = challenge.getElementsByClassName("challenge-name")[0];
        
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
                        form.style.display = 'none';
                        document.getElementById('solved').style.display = 'block';
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
    });
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