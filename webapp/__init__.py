from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

from webapp import views, api, auth, template_preprocessor, database, git, mail
