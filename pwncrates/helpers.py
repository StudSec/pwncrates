"""
Helper functions within the application
"""
from flask import render_template
import subprocess
import cmarkgfm
import hashlib
import sys
import os
import tomllib
from webapp.helpers import *
import webapp.database as db
from webapp import app


def get_challenge_path():
    if os.path.isfile("challenges/README.md"):
        print("passing check", file=sys.stderr)
        return "challenges"
    else:
        print("not passing check", file=sys.stderr)
        return "challenges/Challenges"


def render_markdown(file_name, title=""):
    try:
        with open(file_name, "r") as f:
            content = cmarkgfm.github_flavored_markdown_to_html(f.read())
    except FileNotFoundError:
        print(f"File {file_name} not found!", file=sys.stderr)
        return render_template("404.html")
    return render_template("markdown_page.html", markdown_content=content, page_title=title)


# Create challenge zip in the static folder sha1(challenge_name + category).zip
def create_challenge_handouts(path):
    category, name, _ = path.split("/", 2)
    challenge_path = get_challenge_path()
    # Replaces existing zip
    # TODO: refactor to not use relative path
    subprocess.run(['zip', '-FSr', f'../../../../static/handouts/{get_handout_name(category, name)}',
                    f'Handout'],
                   stdout=subprocess.DEVNULL,
                   cwd=f'{challenge_path}/{category}/{name}')


# Takes a list of markdown lines and returns a list of lines that fall under the header.
def isolate_markdown_category(lines, header):
    index = lines.index(header) + 1
    for line in lines[lines.index(header) + 1:]:
        if line.startswith("##"):
            return lines[lines.index(header) + 1:index]
        index += 1

    # Reached end of file
    return lines[lines.index(header) + 1:]

# TODO: switch up to uuid
def get_handout_name(category, name):
    zip_file = hashlib.sha1()
    zip_file.update((category + name).encode())
    return f"{zip_file.hexdigest()}.zip"
