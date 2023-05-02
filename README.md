# pwncrates
A CTF framework with a focus on education.


## Installation
To install this application simply run
```commandline
docker-compose up
```
This will start pwncrates on `http://localhost:5000/`

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
## TODO
- Make markdown pages prettier (eg, code blocks)
- Add git integration (fetch challenges from repo)
- Add javascript to flag submissions to update page.
- Add by-university scoreboard
- Add descriptions for (sub)categories
- Add links to easy challenges -> make it easier to get started
- Add challenge difficulty filter
- Add a way to add writeups
- Add profile page + optional fields (universities, links, etc)
- Add discord auth