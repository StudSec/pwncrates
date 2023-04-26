# Webapp
This folder contains all files directly related to the webapp.

## Development
#### Flask
The webapp is written in Flask, to add new routes you can define a new function
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
from webapp import app

# Same function defenition as above
```

Don't forget to add the file to the import statement in `__init__.py`

#### Docker
The webapp runs within docker, as part of this all files within this directory
are added within the container. If you'd like to avoid that (for security
optimizations or whatever) you can add the file path to `.dockerignore`.