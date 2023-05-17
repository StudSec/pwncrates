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
                    referrer: 'http://localhost:5000/challenges/pwn',
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

        // let difficultyFilter = document.getElementById('difficulty-filter');
        // let challengeDificulty = challenges.children;
        // if (challengeDificulty.getAttribute("difficulty") != "easy") {
        //     challenges.style.display = 'none';
        // }

    }    
    
});