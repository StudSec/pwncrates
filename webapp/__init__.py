from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

from webapp import views, api, auth, template_preprocessor, database, git, mail
