"""
Helper functions within the application
"""
from flask import render_template
from pwncrates import app
import subprocess
import cmarkgfm
import sys


def get_challenge_path():
    return app.config["runtime"].get("challenge_path", 2)


def render_markdown(file_name, title=""):
    try:
        with open(file_name, "r") as f:
            content = cmarkgfm.github_flavored_markdown_to_html(f.read())
    except FileNotFoundError:
        print(f"File {file_name} not found!", file=sys.stderr)
        return render_template("404.html")
    return render_template("markdown_page.html", markdown_content=content, page_title=title)


# Create challenge zip in the static folder uuid.zip
def create_challenge_handouts(challenge):
    subprocess.run(['zip', '-FSr', f'/pwncrates/static/handouts/{get_handout_name(challenge.uuid)}',
                    f'Handout'],
                   stdout=subprocess.DEVNULL,
                   cwd=challenge.path)


def get_handout_name(challenge_uuid):
    return f"{challenge_uuid}.zip"
