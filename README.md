# pwncrates
A CTF framework with a focus on education.


## Installation
#### The short version:

```commandline
./install.sh
docker-compose up
```
_Note: some docker-compose versions require the profile to be explicitly set, in this case run:_
```commandline
docker-compose --profile "" up
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
    "webhook_url": "",
    "secret_key": "...",
    "registration_enabled": 1,
    "instancer_url": "...",
    "instancer_username": "...",
    "instancer_password": "...",
    "start_time": 0,
    "end_time": 0,
    "utc_offset": 2,
    "challenges_behind_login": 0
}
```

The file will need to exist with the above structure regardless. Currently, there is no support to disabled oauth & email
verification. However, the file will accept empty/ dummy values (but will of course not work).

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
docker-compose down
docker-compose build
docker-compose --profile debug up
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
config.json
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
the CTF challenges. This repository should contain the following, see https://github.com/StudSec/Challenges-Examples for
an example.
```commandline
.
| - challenge_category/
|   | - challenge_name
|   |   | - README.md
|   |   \ - Handout/
|   |       \ - File
|   | - other_challenge
|   |        \ - README.md
|   | - Banner.png
|   \ - README.md
\ - README.md    
```
The README's are broken down as follows
```md
## Master README
This contains links to all challenges, it acts as an index to the repository.

## Category README
This contains a description of the category, in addition to all the subcategories (and their descriptions)

## Challenge README
This contains the challenge description and a table containing connection info, flag, point count, etc
```
The Handout is optional, if present all files within the folder will be zipped and this zip will be provided as
a challenge handout.

The Banner.png contains the banner for each category, if this is not present a fallback image provider will be used.

The challenge README's are structured as follows:
```md
## Challenge Name (for example fuzzy lobster)
This part contains an unofficial description. It won't be displayed to the players.

## Description
Example description

## Challenge information
| Difficulty            | Easy                    |
|-----------------------|-------------------------|
| points                | 25                      |
| subcategory           | Intro                   |
| flag                  | CTF{Example_Flag}       |
| url                   | challs.example.com:7100 |
| case_insensitive      | True                    |
```

In this the final two table entries are optional, when present `case_insensitive` will verify flags
without regarding the casing (Eg `Hi == hi`). 
