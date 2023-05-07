""""
This file contains all functionality surrounding the git
"""
import os.path

from webapp.helpers import *
import webapp.database as db
import threading
import time
import re


import sys


def git_files_changed():
    subprocess.run(['git', '--no-pager', 'fetch'], cwd="challenges/Challenges",
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    diff_output = subprocess.run(['git', '--no-pager', 'diff', '--name-only', 'main', 'origin/main'],
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd="challenges/Challenges")
    changed_files = diff_output.stdout.decode().split("\n")

    return changed_files


def update_challenges_from_git():
    changed_files = git_files_changed()
    git_update()

    changed_files = list(filter(lambda path: ".md" in path or "Handout" in path, [item for item in changed_files]))

    # We need to keep track of challenges we've already updated for handouts. A single change might update
    # multiple files, doing this allows us to batch them. Only handout changes are batched.
    updated_challenges = []
    for file in changed_files:
        try:
            if "README.md" == file.split("/")[2]:
                db.update_or_create_challenge(file)

                # Could be the challenge wasn't yet imported, update handout if it doesn't already exist
                if os.path.exists("./challenges/Challenges/" + file[:-9] + "Handouts") and \
                        not os.path.exists(f"static/handouts/{get_handout_name(file.split('/')[0], file.split('/')[1])}"):
                    updated_challenges.append(file)
                    create_challenge_handouts(file)

            if "Handout" == file.split("/")[2] and file not in updated_challenges:
                updated_challenges.append(file)
                create_challenge_handouts(file)
        except IndexError:
            pass


def git_update():
    # Rebase on origin, the reason we do this is to avoid conflicts when (accidentally) writing files
    subprocess.run(['git', 'checkout', 'main'], cwd='challenges/Challenges', stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    subprocess.run(['git', '--no-pager', 'reset', '--hard', 'HEAD'], cwd="challenges/Challenges",
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['git', '--no-pager', 'pull'], cwd="challenges/Challenges", stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    return


def init_git():
    # Copy challenge directory from Read Only volume to local
    subprocess.run(['cp', '-r', '/tmp/challenges/', '.'])
    subprocess.run(['git', '--no-pager', 'config', 'credential.helper', 'store'], cwd="challenges/Challenges",
                   stdout=subprocess.DEVNULL)

    print("Importing challenges...")
    with open("./challenges/Challenges/README.md") as f:
        matches = re.findall(r"]\((.*?)\)", f.read())
        for challenge in matches:
            if challenge.endswith("README.md"):
                challenge = challenge.replace("%20", " ").replace("./", "")
                # We have to account for url encoding, fortunately the only case for this is the space character
                db.update_or_create_challenge(challenge)

                if os.path.exists("./challenges/Challenges/" + challenge[:-9] + "Handout"):
                    create_challenge_handouts(challenge)
            else:
                print("Invalid challenge:", challenge)


def update_git_loop():
    while True:
        update_challenges_from_git()
        time.sleep(60)


init_git()
update_challenges_from_git()
thread = threading.Thread(target=update_git_loop)
thread.daemon = True
thread.start()
