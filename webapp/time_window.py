from time import time
from json import load
from functools import wraps
from flask import redirect, url_for

with open("config.json") as f:
    config = load(f)

START_TIME = int(config.get("start_time", 0))
END_TIME = int(config.get("end_time", 0))

TIME_WINDOW_DISABLED = START_TIME == 0 and END_TIME == 0

def ctf_has_started(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        now = int(time())
        if TIME_WINDOW_DISABLED or (now >= START_TIME and now < END_TIME):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('rules'))
    return decorated_function
