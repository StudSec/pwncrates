from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

from webapp import views, api, auth, template_preprocessor, database, git, mail
