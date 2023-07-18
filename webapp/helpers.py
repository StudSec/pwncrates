"""
Helper functions within the application
"""
from flask import render_template
import subprocess
import cmarkgfm
import hashlib
import sys
import os


def get_challenge_path():
    if os.path.isfile("challenges/README.md"):
        print("passing check", file=sys.stderr)
        return "challenges/"
    else:
        return "challenges/Challenges/"


def render_markdown(file_name):
    try:
        with open(file_name, "r") as f:
            content = cmarkgfm.github_flavored_markdown_to_html(f.read())
    except FileNotFoundError:
        print(f"File {file_name} not found!", file=sys.stderr)
        return render_template("404.html")
    return render_template("markdown_page.html", markdown_content=content)


# Iterate through challenge README.md, return title, description, points, flag
def parse_markdown_challenge(path):
    ret = {"url": "Null"}
    with open(path, "r") as f:
        lines = f.readlines()

    try:
        ret["description"] = ''.join(isolate_markdown_category(lines, "## Description\n"))
        challenge_information = isolate_markdown_category(lines, "## Challenge information\n")

        if not challenge_information:
            raise ValueError

        for line in challenge_information:
            try:
                key = line.split("|")[1].strip().lower()
            except IndexError:
                continue
            # We want to skip over the ------ line
            if key != len(key) * key[0]:
                ret[key] = line.split("|")[2].strip()
    except ValueError:
        pass
    if not all(x in ret.keys() for x in ["description", "flag", "points", "subcategory", "difficulty"]):
        print(f"{path} doesn't contain all required challenge information, skipping")
        return {}

    return ret


# Parses category markdown, extracts any subcategories and descriptions
# Returns a dict of all (sub)category names and descriptions and the parent category as a string
def parse_markdown_category(path):
    ret = {}

    with open(path, "r") as f:
        lines = f.readlines()

    subcategories = [line for line in lines if "#### " in line]
    try:
        for category in subcategories:
            ret[category[5:].strip()] = "\n".join(isolate_markdown_category(lines, category))

        # Get main category description
        ret[path.split("/")[-2]] = "\n".join(isolate_markdown_category(lines, lines[0]))
    except ValueError:
        pass

    return ret, path.split("/")[-2]


# Create challenge zip in the static folder sha1(challenge_name + category).zip
def create_challenge_handouts(path):
    category, name, _ = path.split("/", 2)
    challenge_path = get_challenge_path()
    # Replaces existing zip
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


def get_handout_name(category, name):
    zip_file = hashlib.sha1()
    zip_file.update((category + name).encode())
    return f"{zip_file.hexdigest()}.zip"
