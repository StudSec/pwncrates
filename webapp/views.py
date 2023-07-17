"""
This file handles all non-API and non-auth routes
"""
import os
import sys

from webapp import app
from flask import render_template, request
from flask_login import current_user, login_required
import webapp.database as db
from webapp.helpers import render_markdown
from webapp.models import User
import random


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/rules')
def rules():
    return render_markdown("./pages/rules.md")


@app.route('/contributing')
def contributing():
    return render_markdown("./pages/contributing.md")


@app.route('/profile')
@login_required
def profile():
    return public_profile(current_user.id)


@app.route('/profile/<int:user_id>')
def public_profile(user_id):
    user = User.get(user_id)

    if not user:
        return render_template("404.html")
    

    self_profile = user.id == current_user.id
    universities = []
    if self_profile:
        universities = db.get_universities()

    scores = db.get_scoreboard()

    try:
        index = [i for i in range(len(scores)) if scores[i][0] == user_id][0]
        rank, score = index + 1, scores[index][4]
    except IndexError:
        rank, score = 0, 0

    return render_template("profile.html", current_user=user, solves=db.get_user_solves(user.id),
                           rank=(rank, score), self_profile=self_profile, universities=universities)


# General category page, contains an overview of the categories if no category is specified
@app.route('/challenges')
@app.route('/challenges/<category>')
def challenges(category=None):
    if not category:
        return render_template("challenges_overview.html", categories=db.get_categories())

    if category not in db.get_categories():
        return render_template("404.html")

    if current_user.is_authenticated:
        solved_challenges = [solve[0] for solve in db.get_user_solves(current_user.id)]
    else:
        solved_challenges = []

    return render_template("challenges_category.html", category=category,
                           subcategories=db.get_challenges(category), solves=solved_challenges)


# Writeups page, contains an overview of all available writeups if no specific one is specified.
@app.route('/writeups/<int:challenge_id>')
@app.route('/writeups/<int:challenge_id>/<int:writeup_id>')
@login_required
def writeups(challenge_id, writeup_id=None):
    if challenge_id not in [solve[0] for solve in db.get_user_solves(current_user.id)]:
        return "Unauthorized"

    if not writeup_id:
        return render_template("writeups_overview.html",
                               challenge_id=challenge_id,
                               challenge_name=db.get_challenge_name(challenge_id),
                               writeups=db.get_writeups(challenge_id))
    file_name = db.get_writeup_file(challenge_id, writeup_id)

    if len(file_name) != 1:
        return render_template("404.html")

    assert(file_name[0].isalnum())

    return render_markdown(f"./writeups/{challenge_id}/{file_name[0]}.md")


@app.route('/writeups/<int:challenge_id>', methods=["POST"])
@login_required
def upload_writeups(challenge_id):
    if challenge_id not in [solve[0] for solve in db.get_user_solves(current_user.id)]:
        return "Unauthorized"

    file = request.files['file']

    filename = hex(random.getrandbits(128))[2:]

    if not os.path.exists(f"writeups/{str(challenge_id)}"):
        os.makedirs(f"writeups/{str(challenge_id)}")

    while f"{filename}.md" in os.listdir(f"writeups/{str(challenge_id)}"):
        filename = hex(random.getrandbits(128))[2:]

    if file:
        db.create_or_update_writeup(challenge_id, current_user.id, filename)
        file.save(f'writeups/{str(challenge_id)}/{filename}.md')
        return 'OK'
    else:
        return 'No file uploaded!'


@app.route('/solves/<int:challenge_id>')
def solves(challenge_id):
    return render_template("solves.html", users=db.get_challenge_solves(challenge_id),
                           challenge_name=db.get_challenge_name(challenge_id))


@app.route('/scoreboard')
def scoreboard():
    return render_template("scoreboard.html", users=db.get_scoreboard(), universities=db.get_universities())


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404
