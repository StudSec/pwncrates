"""
Helper functions within the application
"""
from flask import render_template
import subprocess
import cmarkgfm
import hashlib
import sys
import os
import tomli
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

    if "subcategory" not in ret.keys():
        ret["subcategory"] = ""

    if "docker_name" not in ret.keys():
        ret["docker_name"] = ""

    if "case_insensitive" not in ret.keys():
        ret["case_insensitive"] = False
    elif "false" not in ret["case_insensitive"].lower():
        # If the flag is present, we will assume it was intended to be case-insensitive unless explicitly
        # directed otherwise.
        ret["case_insensitive"] = True

    if not all(x in ret.keys() for x in ["description", "flag", "points", "subcategory", "difficulty"]):
        print(f"{path} doesn't contain all required challenge information, skipping", file=sys.stderr)
        return {}

    return ret

import tomli  # or use tomllib for Python 3.11+
import sys
from typing import Dict, List, Any

def parse_toml_challenge(path):

    challenges = []
    
    try:
        # Read and parse the TOML file
        with open(path, "rb") as f:
            toml_data = tomli.load(f)
        
        for challenge_id, challenge_data in toml_data.items():
            ret = {"url": "Null"}
            
            # Set description if available, otherwise empty string
            ret["description"] = challenge_data.get("description", "")
            
            # Handle flag field which could be a dictionary with flag-to-points mapping
            if "flag" in challenge_data:
                flag_data = challenge_data["flag"]
                if isinstance(flag_data, dict):
                    ret["flag"] = next(iter(flag_data.keys()))
                    ret["points"] = next(iter(flag_data.values()))
                else:
                    ret["flag"] = flag_data
                    ret["points"] = challenge_data.get("points", 0)
            
            for field in ["name", "url"]:
                if field in challenge_data:
                    # Handle URL arrays by taking the first one
                    if field == "url" and isinstance(challenge_data[field], list):
                        ret[field] = challenge_data[field][0]
                    else:
                        ret[field] = challenge_data[field]
                        
            if "difficulty" in challenge_data:
                difficulty = challenge_data["difficulty"].lower()
                if difficulty in ["easy", "medium", "hard"]:
                    ret["difficulty"] = difficulty
                else:
                    ret["difficulty"] = "easy"
            else:
                ret["difficulty"] = "easy"
            
            ret["subcategory"] = challenge_data.get("subcategory", "")
            ret["docker_name"] = challenge_data.get("docker_name", "")
            
            case_insensitive = challenge_data.get("case_insensitive", False)
            if isinstance(case_insensitive, str):
                ret["case_insensitive"] = "false" not in case_insensitive.lower()
            else:
                ret["case_insensitive"] = bool(case_insensitive)
            
            ret["id"] = challenge_id
            
            # Check if all required fields are present
            required_fields = ["description", "flag", "points", "subcategory", "difficulty"]
            if all(field in ret for field in required_fields):
                challenges.append(ret)
            else:
                missing = [field for field in required_fields if field not in ret]
                print(f"Challenge in {path} missing required fields: {missing}, skipping", file=sys.stderr)
    
    except Exception as e:
        print(f"Error parsing {path}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    
    return challenges

# Usage example:
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        challenges = parse_toml_challenge(sys.argv[1])
        for challenge in challenges:
            print(challenge)
    else:
        print("Please provide a TOML file path")

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
