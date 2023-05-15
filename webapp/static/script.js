document.addEventListener('DOMContentLoaded', () => {

    let challenges = document.getElementById('challenge_submission').children
    for (let form of challenges) {
        form.addEventListener('submit', async function (handleSubmit) {
            handleSubmit.preventDefault();
            let form = handleSubmit.target;
            let url = form.action;
            try {
                let formData = new FormData(form);
                let response = await fetch({url, formData});
                if (response.json() == 'OK') {
                    form.children[0].children[0].style.backgroundColor = 'lightgreen';
                }
                else {
                    form.children[0].children[0].style.backgroundColor = '#ff4040';
                }                
            }
            catch (error) {
                console.error(error);
            }    
        })
    }
    
});