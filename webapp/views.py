"""
This file handles all non-API and non-auth routes
"""
from webapp import app
from flask import render_template
import webapp.database as db
import markdown
import sys


# Home page
@app.route('/')
def home():
    return render_template("home.html")


# Rule page
@app.route('/rules')
def rules():
    try:
        with open("./pages/rules.md", "r") as f:
            content = markdown.markdown(f.read())
    except FileNotFoundError:
        # Maybe we should return a 404?
        print("Rules page not found!", file=sys.stderr)
        return render_template("404.html")
    return render_template("markdown_page.html", markdown_content=content)


# Contributing page
@app.route('/contributing')
def contributing():
    try:
        with open("./pages/contributing.md", "r") as f:
            content = markdown.markdown(f.read())
    except FileNotFoundError:
        print("Contributing page not found!", file=sys.stderr)
        return render_template("404.html")
    return render_template("markdown_page.html", markdown_content=content)


# General category page, contains an overview of the categories if no category is specified
@app.route('/challenges')
@app.route('/challenges/<category>')
def challenges(category=None):
    if not category:
        return render_template("challenges_overview.html", categories=db.get_categories())
    if category not in db.get_categories():
        return render_template("404.html")
    # TODO: change 1 to userid
    return render_template("challenges_category.html", category=category,
                           subcategories=db.get_challenges(category), solves=db.get_solves(1))


# Writeups page, contains an overview of all available writeups if no challenge is specified.
@app.route('/writeups')
@app.route('/writeups/<challenge>')
def writeups(challenge=None):
    return ""


@app.route('/scoreboard')
def scoreboard():
    return render_template("scoreboard.html", users=db.get_scoreboard())
