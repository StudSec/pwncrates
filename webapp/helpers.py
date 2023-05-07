"""
Helper functions within the application
"""
from flask import render_template
import subprocess
import cmarkgfm
import hashlib
import sys


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

        for line in challenge_information:
            try:
                key = line.split("|")[1].strip().lower()
            except IndexError:
                continue
            # We want to skip over the ------ line
            if key != len(key) * key[0]:
                ret[key] = line.split("|")[2].strip()
    except ValueError as e:
        pass
    if not all(x in ret.keys() for x in ["description", "flag", "points", "subcategory", "difficulty"]):
        print(f"{path} doesn't contain all required challenge information, skipping")
        return {}

    print(f"{path} imported!")

    return ret


# Iterate through main README.md, return list of paths
def parse_markdown_overview(path):
    pass


# Create challenge zip in the static folder sha1(challenge_name + category).zip
def create_challenge_handouts(path):
    category, name, _ = path.split("/", 2)
    zip_file = hashlib.sha1()
    zip_file.update((category+name).encode())
    # Replaces existing zip
    subprocess.run(['zip', '-FSr', f'static/handouts/{zip_file.hexdigest()}.zip',
                    f'challenges/Challenges/{category}/{name}/Handout'], stdout=subprocess.DEVNULL)


# Takes a list of markdown lines and returns a list of lines that fall under the header.
def isolate_markdown_category(lines, header):
    index = lines.index(header) + 1
    for line in lines[lines.index(header) + 1:]:
        if line.startswith("##"):
            return lines[lines.index(header) + 1:index]
        index += 1

