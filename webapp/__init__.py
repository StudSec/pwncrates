from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_SECURE'] = True
# We have to put this at lax instead of secure to support Discord OAuth
# Should we drop support for the "state" parameter in the OAuth flow this can go back on strict
# However, as it stands we set the state parameter, navigate to Discord and navigate back to check if the
# state parameters still match. This requires us to persist the session after exiting Discord, which is not
# done in Strict.
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

from webapp import views, api, auth, template_preprocessor, database, git, mail
