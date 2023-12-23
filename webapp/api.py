"""
This file contains all API routes.

An API route is used either by external applications (for example the StudBot), or client side javascript.
"""
import sys

from flask_login import login_required, current_user
import webapp.database as db
from webapp import app
from flask import request
from flask import Response
import requests
import json
import datetime
# General API file

# Read and eval config file
with open("config.json", "r") as f:
    config = json.loads(f.read())


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
        status = db.submit_flag(challenge_id, request.form['flag'], current_user.id)

        if status != "OK":
            return Response(json.dumps({"status": status}),
                            mimetype="application/json")

        data = {
            "content": f"{db.get_user(user_id=current_user.id)['username']} solved {db.get_challenge_name(challenge_id)}!",
            "allowed_mentions": {
                "parse": []
              },
            "tts": False,
            # SUPPRESS_EMBEDS & SUPPRESS_NOTIFICATIONS, for more info see:
            # https://discord.com/developers/docs/resources/channel#message-object-message-flags
            "flags": 1 << 2 | 1 << 12,
        }
        if config["webhook_url"].startswith("https://") or config["webhook_url"].startswith("http://"):
            requests.post(config["webhook_url"], json=data)

        return Response(json.dumps({"status": status}),
                        mimetype="application/json")
    except KeyError:
        return Response(json.dumps({"Error": "Flag missing."}), mimetype="application/json")


@app.route('/api/profile/update', methods=["POST"])
@login_required
def api_update_profile():
    try:
        university_id = int(request.form["university"])
        if len([university for university in db.get_universities() if university[0] == university_id]) == 0:
            return Response(json.dumps({"Error": "Invalid university id"}), mimetype="application/json")
        db.update_user_university(current_user.id, request.form["university"])
        return Response(json.dumps({"Status": "OK"}), mimetype="application/json")
    except KeyError:
        return Response(json.dumps({"Error": "Missing parameters"}), mimetype="application/json")
    except ValueError:
        return Response(json.dumps({"Error": "Invalid datatype"}), mimetype="application/json")


@app.route('/api/scoreboard')
def api_scoreboard():
    ret = []
    scoreboard = db.get_scoreboard()

    for rank, user in enumerate(scoreboard):
        ret.append({
            "username": user[1],
            "university": user[3],
            "position": rank+1,
            "score": user[4],
            "user_id": user[0]
        })

    return Response(json.dumps(ret),
                    mimetype="application/json")


@app.route('/api/discord_id/<user_id>')
def api_discord_id(user_id):
    user_data = db.get_user(user_id=user_id)

    ret = {
        "discord_id": user_data["discord_id"]
    }

    return Response(json.dumps(ret),
                    mimetype="application/json")


@app.route('/api/user/solves/<user_id>')
def api_get_user(user_id):
    user_data = db.get_user_scores(user_id=user_id)
    return Response(json.dumps(user_data),
                    mimetype="application/json")

