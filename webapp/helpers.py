"""
Helper functions within the application
"""
from flask import render_template
import cmarkgfm
import sys


def render_markdown(file_name):
    try:
        with open(file_name, "r") as f:
            content = cmarkgfm.github_flavored_markdown_to_html(f.read())
    except FileNotFoundError:
        # Maybe we should return a 404?
        print(f"File {file_name} not found!", file=sys.stderr)
        return render_template("404.html")
    return render_template("markdown_page.html", markdown_content=content)
