from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask
import json
import logging
import os

# Set path to the correct location if called externally (as is done in unit tests)
os.chdir(os.path.dirname(os.path.abspath(__file__)))


with open("config.json") as f:
    config = json.load(f)


app = Flask(__name__)
app.secret_key = config["secret_key"]
app.config["INSTANCER_URL"] = config.get("instancer_url", "")
app.config['SESSION_COOKIE_SECURE'] = True
app.config['START_TIME'] = int(config.get("start_time", 0))
app.config['END_TIME'] = int(config.get("end_time", 0))
# We have to put this at lax instead of secure to support Discord OAuth
# Should we drop support for the "state" parameter in the OAuth flow this can go back on strict
# However, as it stands we set the state parameter, navigate to Discord and navigate back to check if the
# state parameters still match. This requires us to persist the session after exiting Discord, which is not
# done in Strict.
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# https://flask.palletsprojects.com/en/3.0.x/deploying/proxy_fix/
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# Based on: https://trstringer.com/logging-flask-gunicorn-the-manageable-way/
# In simple terms, we inherit the log level from gunicorn if run from gunicorn, if not we set it to debug
if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
else:
    app.logger.setLevel(logging.DEBUG)

# Add the other routes
from pwncrates import views, api, auth, template_preprocessor, database, git, mail, time_window, admin
