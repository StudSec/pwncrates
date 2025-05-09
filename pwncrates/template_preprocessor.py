"""
This file handles the "global" variables for the Jinja2 templates.

Global variables are variables used by the base template, or its includes.
"""
from pwncrates import app
from flask import url_for
from flask_login import current_user


@app.after_request
def add_security_headers(resp):
    bootstrap_js_url = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/js/bootstrap.bundle.min.js"
    bootstrap_css_url = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css"

    # Graph things
    chart_url = "https://cdn.jsdelivr.net/npm/chart.js"
    graph_url = "https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"
    resp.headers['Content-Security-Policy'] = ("default-src 'none'; "
                                               f"script-src {app.config['pwncrates']['HOSTNAME'] + '/static/script.js'} "
                                               f"{bootstrap_js_url} "
                                               f"{chart_url} "
                                               f"{graph_url}; "
                                               f"style-src {app.config['pwncrates']['HOSTNAME'] + '/static/style.css'} "
                                               f"{bootstrap_css_url}; "
                                               "base-uri 'self'; "
                                               "img-src * data:; "
                                               "connect-src 'self';")
    return resp


@app.context_processor
def inject_globals():
    routes = {
        "Rules": url_for("rules"),
        "Getting started": url_for("getting_started"),
        "Challenges": url_for("challenges"),
        "Contributing": url_for("contributing"),
        "Scoreboard": url_for("scoreboard"),
    }
    
    if current_user.is_authenticated and current_user.is_admin:
        routes["Admin"] = url_for("admin")

    return dict(name="StudSec", routes=routes, app=app)
