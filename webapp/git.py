""""
This file contains all functionality surrounding the git
"""
import os.path

from webapp.helpers import *
import webapp.database as db
import threading
import time
import sys
import re
import os


def git_files_changed():
    challenge_path = get_challenge_path()
    subprocess.run(['git', '--no-pager', 'fetch'], cwd=challenge_path,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    diff_output = subprocess.run(['git', '--no-pager', 'diff', '--name-only', 'main', 'origin/main'],
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=challenge_path)
    changed_files = diff_output.stdout.decode().split("\n")

    return changed_files


def update_challenges_from_git():
    challenge_path = get_challenge_path()
    changed_files = git_files_changed()
    git_update()

    changed_files = list(filter(lambda path: ".md" in path or "Handout" in path, [item for item in changed_files]))

    # We need to keep track of challenges we've already updated for handouts. A single change might update
    # multiple files, doing this allows us to batch them. Only handout changes are batched.
    updated_challenges = []
    for file in changed_files:
        try:
            if "README.md" == file.split("/")[1]:
                db.update_or_create_category(file)
            if "README.md" == file.split("/")[2]:
                db.update_or_create_challenge(file)

                # Could be the challenge wasn't yet imported, update handout if it doesn't already exist
                if os.path.exists(f"./{challenge_path}" + file[:-9] + "Handouts") and \
                        not os.path.exists(f"static/handouts/{get_handout_name(file.split('/')[0], file.split('/')[1])}"):
                    updated_challenges.append(file)
                    create_challenge_handouts(file)

            if "Handout" == file.split("/")[2] and file not in updated_challenges:
                updated_challenges.append(file)
                create_challenge_handouts(file)
            if "Writeup.md" == file.split("/")[2]:
                challenge_id = db.get_challenge_id(file.split("/")[1])
                subprocess.run(['mkdir', f'writeups/{challenge_id}'])
                subprocess.run(['cp', file, f'writeups/{challenge_id}/Author.md'])
        except IndexError:
            pass
        except FileNotFoundError as error:
            print(f"Error parsing {file}:", error, file=sys.stderr)


def git_update():
    challenge_path = get_challenge_path()
    # Rebase on origin, the reason we do this is to avoid conflicts when (accidentally) writing files
    subprocess.run(['git', 'checkout', 'main'], cwd=challenge_path, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    subprocess.run(['git', '--no-pager', 'reset', '--hard', 'HEAD'], cwd=challenge_path,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['git', '--no-pager', 'pull'], cwd=challenge_path, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    return


def init_git():
    # Copy challenge directory from Read Only volume to local
    subprocess.run(['cp', '-r', f'/tmp/challenges/', '.'])
    challenge_path = get_challenge_path()
    subprocess.run(['git', '--no-pager', 'config', 'credential.helper', 'store'], cwd=challenge_path,
                   stdout=subprocess.DEVNULL)

    print("Importing challenges...")
    with open(f"./{challenge_path}/README.md") as f:
        matches = re.findall(r"]\((.*?)\)", f.read())
        for challenge in matches:
            if challenge.endswith("README.md"):
                challenge = challenge.replace("%20", " ").replace("./", "")
                # We have to account for url encoding, fortunately the only case for this is the space character
                challenge_id = db.update_or_create_challenge(challenge)

                if os.path.exists(f"./{challenge_path}/" + challenge[:-9] + "Handout"):
                    create_challenge_handouts(challenge)
                if os.path.exists(f"./{challenge_path}/" + challenge[:-9] + "Writeup.md"):
                    subprocess.run(['mkdir', f'writeups/{challenge_id}'])
                    subprocess.run(['cp', f"./{challenge_path}/" + challenge[:-9] + "Writeup.md",
                                    f'writeups/{challenge_id}/Author.md'])

            else:
                print("Invalid challenge:", challenge)

    print("Importing categories...")
    for category in [x for x in os.listdir(f"./{challenge_path}/")
                     if os.path.isdir(f"./{challenge_path}/{x}")]:
        if os.path.exists(f"./{challenge_path}/{category}/README.md"):
            db.update_or_create_category(f"./{challenge_path}/{category}/README.md", folder="")


def update_git_loop():
    while True:
        try:
            update_challenges_from_git()
            time.sleep(60)
        except Exception as e:
            print("Error updating git:", e)


try:
    init_git()
    update_challenges_from_git()
except Exception as e:
    print("Error initializing git:", e, file=sys.stderr)

thread = threading.Thread(target=update_git_loop)
thread.daemon = True
thread.start()
