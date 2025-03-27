# pwncrates
A CTF framework with a focus on education.


## Installation
#### The short version:

```commandline
./install.sh
docker compose up
```
_Note: some docker-compose versions require the profile to be explicitly set, in this case run:_
```commandline
docker compose --profile "" up
```

#### The longer (manual) version:
Firstly, you need to include the challenges in `data/challenges`
The repository should have the name `Challenges`.

For example
```commandline
git clone https://github.com/StudSec/Challenges-Examples.git 
mv Challenges-Examples data/challenges/Challenges
```

*Note: the git repository will automatically be updated
once a minute. If this is a private repository you can include
a `.git-credentials` file in `data/`. See the data paragraph for more information.*

Then run pwncrates using
```commandline
docker compose up
```
This will start pwncrates on `http://localhost/`

`update.sh` is also included, which is a simple way to check for remote changes and redeploy if needed.

If you want to have email and oauth functionality you need to create and configure a file in `data/config.toml`.
The file needs to be structured as follows:
```toml
# Settings that can be changed at runtime, these are stored in the database
[runtime]
registration_enabled = ""
start_time = 0
end_time = 0
utc_offset = 2
challenges_behind_login = 0

# Static settings, a restart is required to change these settings
[mailer]
SMTP_HOST = ""
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASS = ""

[oauth]
OAUTH_CLIENT_ID = ""
OAUTH_CLIENT_SECRET = ""
OAUTH_REDIRECT_URI = ""

[pwncrates]
HOSTNAME = "127.0.0.1"
SECRET_KEY = ""
WEBHOOK_URL = ""
GIT_BRANCH = ""

[instancer]
INSTANCER_URL = ""
INSTANCER_USERNAME = ""
INSTANCER_PASSWORD = ""
```

All fields must be present regardless of usage, you can disable aspects such as oauth or the instancer by providing
an empty value.

The `hostname` field should contain the servers ip address/dns name, it is used to generate links for password 
resets/account verifications and, importantly, the CSP. If the frontend is not working this is likely the issue.

Note, if no SMTP host is specified email confirmations are disabled and all newly registered accounts will be activated.

#### Migrating from ctfd
You can use the migration script in `./scripts/` to migrate a ctfd database to pwncrates. However, this has minimal
support, it will automate a lot for you, but it's not a "run and forget" solution. It expects a mysql dump/backup file
called `backup.sql` to be in the same folder as the script.

## Development
For development, you likely want to rapidly redeploy the docker
instance. For that you may use the following three commands.
```commandline
docker compose down
docker compose build
docker compose --profile debug up
```

You might also want to directly interact with the docker container for
debugging purposes. For this you can use the following command to start a
shell within the container
```commandline
sudo docker exec -it pwncrates-pwncrates-dev-1 bash
```

As a general design principle, try to keep all data within the data folder.
This means any configs, database data, user data, should reside in that. If 
a user would like to back up the entire application it should be a simple as
backing up the data folder.

If you'd like to manually look at the database you can explore the `.db` file
in `./data/db/`. One tool for this is https://inloop.github.io/sqlite-viewer/

## Data
The `data` folder contains all data for pwncrates. It should contain the
following
```commandline
challenges/
db/pwncrates.db
pages/contributing.md
pages/rules.md
writeups/
.git-credentials
config.toml
```

The .git-credentials file should contain git credentials. The format of
the file is as follows
```commandline
<protocol>://<username>:<password>@<host>:<port>
```
For more information see
https://git-scm.com/docs/git-credential-store

#### Challenges
Challenges should contain a git repository named `Challenges` which contains
the CTF challenges. For more details see https://github.com/StudSec/Challenges-Examples 
