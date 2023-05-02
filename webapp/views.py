"""
This file handles all non-API and non-auth routes
"""
from webapp import app
from flask import render_template
from flask_login import current_user, login_required
import webapp.database as db
from webapp.helpers import render_markdown


# Home page
@app.route('/')
def home():
    return render_template("home.html")


# Rule page
@app.route('/rules')
def rules():
    return render_markdown("./pages/rules.md")


# Contributing page
@app.route('/contributing')
def contributing():
    return render_markdown("./pages/contributing.md")


# General category page, contains an overview of the categories if no category is specified
@app.route('/challenges')
@app.route('/challenges/<category>')
def challenges(category=None):
    if not category:
        return render_template("challenges_overview.html", categories=db.get_categories())

    if category not in db.get_categories():
        return render_template("404.html")

    if current_user.is_authenticated:
        solves = db.get_solves(current_user.id)
    else:
        solves = []

    return render_template("challenges_category.html", category=category,
                           subcategories=db.get_challenges(category), solves=solves)


# Writeups page, contains an overview of all available writeups if no specific one is specified.
@app.route('/writeups/<int:challenge_id>')
@app.route('/writeups/<int:challenge_id>/<int:writeup_id>')
@login_required
def writeups(challenge_id, writeup_id=None):
    if challenge_id not in db.get_solves(current_user.id):
        return "Unauthorized"

    if not writeup_id:
        return render_template("writeups_overview.html",
                               challenge_id=challenge_id,
                               challenge_name=db.get_challenge_name(challenge_id)[0],
                               writeups=db.get_writeups(challenge_id))
    file_name = db.get_writeup_file(challenge_id, writeup_id)

    if len(file_name) != 1:
        return render_template("404.html")

    assert(file_name[0].isalnum())

    return render_markdown(f"./writeups/{challenge_id}/{file_name[0]}.md")


@app.route('/scoreboard')
def scoreboard():
    return render_template("scoreboard.html", users=db.get_scoreboard())


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404
