from time import time
from pwncrates import app
from functools import wraps
from flask import redirect, url_for

START_TIME = int(app.config["runtime"].get("start_time", 0))
END_TIME = int(app.config["runtime"].get("end_time", 0))
TIMEZONE = int(app.config["runtime"].get("utc_offset", 2))

TIME_WINDOW_DISABLED = START_TIME == 0 and END_TIME == 0

def ctf_is_now():
    now = int(time())
    return TIME_WINDOW_DISABLED or (now >= START_TIME and now < END_TIME)

def ctf_has_started(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ctf_is_now():
            return f(*args, **kwargs)
        else:
            return redirect(url_for('soon'))
    return decorated_function
