document.addEventListener('DOMContentLoaded', () => {
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
                    unit: 'day',
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

    //find challenge assosiated with sumbit
    let challengeId = form.getAttribute("challenge");

    let challenge = document.querySelector(`.challenge[id=${challengeId}]`);
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