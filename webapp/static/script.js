document.addEventListener('DOMContentLoaded', () => {

    let challenges = document.getElementById('challenge_submission').children
    for (let form of challenges) {

        form.addEventListener('submit', async function (handleSubmit) {
            handleSubmit.preventDefault();
            let form = handleSubmit.target;
            let url = form.action;
            try {
                let response = await fetch(url, {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json, text/html',
                    },
                    body: 'flag=' + form.children[0].children[0].value,
                });

                response.json().then(post => {
                    if (post.status === 'OK') {
                        form.children[0].children[0].style.backgroundColor = 'lightgreen';
                        setTimeout(function(){
                            form.style.display = 'none';
                            document.getElementById('solved').style.display = 'block';
                        }, 1000);
                    }
                    else {
                        form.children[0].children[0].style.backgroundColor = '#ff4040';
                        setTimeout(function(){
                            form.children[0].children[0].style.backgroundColor = 'white';
                        }, 1000);
                    }  
                });              
            }
            catch (error) {
                console.error(error);
            }    
        })

        for (let challenge of form.children) {
            let difficultyFilter = document.getElementById('difficulty-filter');
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
        }

    }

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
});

function updateUniversity() {
  fetch('{{ url_for("api_update_profile") }}', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: 'university=' + encodeURIComponent(document.getElementById('university').value)
  });
}