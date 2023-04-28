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

You might also want to directly interact with the database, for this
you can use the following command.
```commandline
mysql -u root -proot -h localhost -P3306
```

## TODO
- Create authentication
- Create pages
- Create API
- Create persistence/backup mechanism.
