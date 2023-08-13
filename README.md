# pwncrates
A CTF framework with a focus on education.


## Installation
#### The short version:

```commandline
./install.sh
docker-compose up
```

#### The longer (manual) version:

Firstly, you need to include the challenges in `data/challenges`
The repository should have the name `Challenges`.

For example
```commandline
git clone https://github.com/StudSec/Challenges-Examples.git 
mv Challenges-Examples data/challenges/
```

*Note: the git repository will automatically be updated
once a minute. If this is a private repository you can include
a `.git-credentials` file in `data/`. See the data paragraph for more information.*

Then run pwncrates using
```commandline
docker-compose up
```
This will start pwncrates on `http://localhost/`

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
    "SMTP_PASS": "",
    "webhook_url": ""
}
```

The file will need to exist with the above structure regardless. Currently, there is no support to disabled oauth & email
verification. However, the file will accept empty/ dummy values (but will of course not work).

The `hostname` field should contain the servers ip address/dns name, it is used to generate links for password 
resets/account verifications.

#### Migrating from ctfd
You can use the migration script in `./scripts/` to migrate a ctfd database to pwncrates. However, this has minimal
support, it will automate a lot for you, but it's not a "run and forget" solution. It expects a mysql dump/backup file
called `backup.sql` to be in the same folder as the script.

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
config.json
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

## TODO - frontend
#### General
- Move Javascript to script.js
- Improve homescreen
- Add favicon
- Make stylized login page
- Make stylized register page

#### Challenges
- Change color schema
- Collapse challenge upon successful solve
- Reset from bad submission (red -> normal)
- Change transition flag successfully submitted -> view writeups
- Mark solved challenges
- Set challenge images
