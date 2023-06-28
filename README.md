# pwncrates
A CTF framework with a focus on education.


## Installation
Firstly, you need to include the challenges in `data/challenges`
The repository should have the name `Challenges`.

For example
```commandline
git clone https://github.com/StudSec/Challenges-Examples.git 
mv Challenges-Examples Challenges
```

*Note: the git repository will automatically be updated
once a minute. If this is a private repository you can include
a `.git-credentials` file in `data/`*

Then run pwncrates using
```commandline
docker-compose up
```
This will start pwncrates on `http://localhost:5000/`

`update.sh` is also included, which is a simple way to check for remote changes and redeploy if needed.

If you want to have email and oauth functionality you need to create and configure a file in `data/config.json`.
The file needs to be structured as follows:
```json
{
    "hostname": "",
    "oauth_client_id": "",
    "oauth_client_secret": "",
    "oauth_redirect_uri": "",
    "SMTP_HOST": "",
    "SMTP_PORT": 587,
    "SMTP_USER": "",
    "SMTP_PASS": ""
}
```

The file will need to exist with the above structure regardless. Currently there is no support to disabled oauth & email
verification. However the file will accept empty/ dummy values (but will of course not work).

The `hostname` field should contain the servers ip address/dns name, it is used to generate links for password 
resets/account verifications.

## Development
For development, you likely want to rapidly redeploy the docker
instance. For that you may use the following three commands.
```commandline
docker-compose down
docker-compose build
docker-compose up
```

You might also want to directly interact with the docker container for
debugging purposes. For this you can use the following command to start a
shell within the container
```commandline
sudo docker exec -it pwncrates-pwncrates-1 bash
```

As a general design principle, try to keep all data within the data folder.
This means any configs, database data, user data, should reside in that. If 
a user would like to backup the entire application it should be a simple as
backing up the data folder.

If you'd like to manually look at the database you can explore the `.db` file
in data. One tool for this is https://inloop.github.io/sqlite-viewer/

## Data
The `data` folder contains all data for pwncrates. It should contain the
following setup
```commandline
challenges/
db/pwncrates.db
pages/contributing.md
pages/rules.md
writeups/
.git-credentials
```

Challenges should contain a git repository named `Challenges` which contains
the CTF challenges. 

TODO: Explain challenge folder setup

The .git-credentials file should contain git credentials. The format of
the file is as follows
```commandline
<protocol>://<username>:<password>@<host>:<port>
```
For more information see
https://git-scm.com/docs/git-credential-store

## TODO - backend
- Discord nonce (https://discord.com/developers/docs/topics/oauth2#state-and-security)
- Discord account linking after creation
- Add CSP headers
- Migrate database

## TODO - frontend
#### General
- Move Javascript to script.js
- Home screen
- Add favicon
- Check mobile style
- Make stylized login page
- Make stylized register page

#### Challenges
- Change card appearence on smaller screens
- Change color schema
- Collapse challenge upon successful solve
- Reset from bad submission (red -> normal)
- Change connection string appearance
- Change transition flag successfully submitted -> view writeups
- Mark solved challenges

#### Writeups
- Change writeup submission text/form
- Set challenge images

#### Scoreboard
- Improve scoreboard style
- Add university logos
- Fix bug -> university filter selector doesn't reset on reload (but scoreboard does)
- Migrate in-line javascript to script.js in scoreboard.html
- Fix filter absolute position

## TODO - Challenges
- Add links to easy challenges -> make it easier to get started

## TODO - Final
- Remove all debug/development switches (print statements, docker configs, flask settings, init.sql data, etc)
