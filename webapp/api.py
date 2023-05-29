"""
This file contains all API routes.

An API route is used either by external applications (for example the StudBot), or client side javascript.
"""
from flask_login import login_required, current_user
import webapp.database as db
from webapp import app
from flask import request
from flask import Response
import json
# General API file


@app.route('/api/get_users')
def api_get_users():
    return Response(json.dumps({user_id: username for user_id, username in enumerate(db.get_users())}),
                    mimetype="application/json")


@app.route('/api/challenges/categories')
def api_get_categories():
    return Response(json.dumps(db.get_categories()),
                    mimetype="application/json")


@app.route('/api/challenges/<category>')
def api_get_challenges(category):
    ret = {}

    for subcategory in db.get_challenges(category):
        ret[subcategory[0]] = {
            "description": subcategory[1],
            "challenges": [
                {
                    "id": challenge[0],
                    "name": challenge[1],
                    "description": challenge[2],
                    "points": challenge[3],
                    "url": challenge[4],
                    "solves": challenge[5],
                    "handout": challenge[6]
                }
                for challenge in subcategory[2]
            ]
        }

    return Response(json.dumps(ret),
                    mimetype="application/json")


@app.route('/api/challenges/submit/<challenge_id>', methods=["POST"])
@login_required
def api_submit_challenge(challenge_id):
    try:
        return Response(json.dumps({"status": db.submit_flag(challenge_id, request.form['flag'], current_user.id)}),
                        mimetype="application/json")
    except KeyError:
        return "Flag missing."


@app.route('/api/scoreboard')
def api_scoreboard():
    ret = {}
    scoreboard = db.get_scoreboard()

    for rank, user in enumerate(scoreboard):
        ret[rank] = {
            "username": user[0],
            "university_id": user[1],
            "score": user[2],
            "user_id": user[3]
        }

    return Response(json.dumps(ret),
                    mimetype="application/json")
