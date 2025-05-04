# Webapp
This folder contains all files directly related to the pwncrates.

When developing, use the following docker-compose command, this will start the application in debug mode
without nginx.
```commandline
docker compose --profile debug up
```

NOTE: This is an insecure configuration by design, do not expose it to external networks, by default it only
binds to localhost (127.0.0.1).

From here you can access the application at http://127.0.0.1/ as normal.

## Development
#### Flask
The pwncrates is written in Flask, to add new routes you can define a new function
to `views.py` as follows:
```python
@app.route('/')
def home():
    return "<h1>hello</h1>"
```

If you'd like to group several new routes together you can create a new file
which contains the following import (note: the file must be in the same directory
as `main.py`)

```python
from pwncrates import app

# Same function defenition as above
```

Don't forget to add the file to the import statement in `__init__.py`

#### Jinja2
The pwncrates uses Jinja2 for templating, this allows us to easily extend a
webpage. For example, we can have a `base.html` which we can then use to
make `home.html`, `scoreboard.html`, etc. For more information see:

- https://svn.python.org/projects/external/Jinja-1.1/docs/build/inheritance.html
- https://jinja.palletsprojects.com/en/3.1.x/templates/
- https://stackoverflow.com/questions/24847753/flask-jinja2-how-to-separate-header-base-and-footer

The `base.html` and all files included in it may contain variables, if these
variables differ per file they may be defined as follows within the extending file.
```jinja2
{% block title %}pwncrates - Home{% endblock %}
```
This example is from `home.html`, which defines the title as "pwncrates - Home"

For more global variables you can add them to the dictonary in `inject_globals`
in `template_preprocessor.py`
```python
@app.context_processor
def inject_globals():
    return dict(name="test_name")
```


#### Docker
The pwncrates runs within docker, as part of this all files within this directory
are added within the container. If you'd like to avoid that (for security,
optimizations or whatever) you can add the file path to `.dockerignore`.

#### Git
Git is used for the challenges to fetch & update. This lets CTF creators
update a git repository and automatically propagate the changes. To 
accommodate for this a few design decisions have been implemented.

The challenge repository should be put in `data/challenges`, upon startup
this folder will be mounted as read only and the first git repository (for 
now all folders will be copied but only one named `Challenges` will be used.) will
be copied within the docker folder. This is done to prevent out-of-container
attacks, where malicious code gets added to git hooks.

The challenge repository is expected to have a main README.md, which contains
links to all the challenges. And each challenge is expected to have its
own README, with the flag, point count, name and description.