"""
This file handles all non-API and non-auth routes
"""
from webapp import app
from flask import render_template
import markdown


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
        print("Rules page not found!")
        return render_template("markdown_page.html", markdown_content="")
    return render_template("markdown_page.html", markdown_content=content)


# Contributing page
@app.route('/contributing')
def contributing():
    try:
        with open("./pages/contributing.md", "r") as f:
            content = markdown.markdown(f.read())
    except FileNotFoundError:
        # Maybe we should return a 404?
        print("Rules page not found!")
        return render_template("markdown_page.html", markdown_content="")
    return render_template("markdown_page.html", markdown_content=content)


# General category page, contains an overview of the categories if no category is specified
@app.route('/challenges')
@app.route('/challenges/<category>')
def challenges(category=None):
    return ""


# Writeups page, contains an overview of all available writeups if no challenge is specified.
@app.route('/writeups')
@app.route('/writeups/<challenge>')
def writeups(challenge=None):
    return ""
