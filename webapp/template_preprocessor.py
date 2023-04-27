from webapp import app
from flask import url_for


@app.context_processor
def inject_globals():
    return dict(name="StudSec",
                routes={
                    "Home": url_for("home"),
                    "Rules": url_for("rules"),
                    "Challenges": url_for("challenges"),
                    "Writeups": url_for("writeups")
                })
