""""
This file contains all functionality surrounding Git
"""
import os.path

from pwncrates.helpers import *
import pwncrates.database as db
from pwncrates import app
from pwncrates.challenges import ChallengeSet
import threading
import time
import os

if "GIT_BRANCH" in app.config["pwncrates"].keys() and app.config["pwncrates"]["GIT_BRANCH"]:
    git_branch = app.config["pwncrates"]["GIT_BRANCH"]
else:
    git_branch = "main"

challenge_lock_file = "challenge_git.lock"


def acquire_challenge_lock():
    try:
        with open(challenge_lock_file, "r") as file:
            data = file.read()
            timestamp = data.split(" ")[0]
            pid = int(data.split(" ")[1])
        # Check if a minute has passed or the same thread wants access (again)
        if int(time.time()) - int(timestamp) > 60 or pid == os.getpid():
            lock_data = f"{int(time.time())} {os.getpid()}"
            with open(challenge_lock_file, "w") as file:
                file.write(lock_data)
            time.sleep(1)  # Prevent race conditions, this way only the most recent worker will update the repo.
            with open(challenge_lock_file, "r") as file:
                current_lock_data = file.read()
            if lock_data == current_lock_data:
                return True
        return False
    except (IndexError, FileNotFoundError, ValueError):
        # Lockfile malformed or doesn't exist. Make file and try again
        with open(challenge_lock_file, "w") as file:
            file.write(f"{int(time.time())} {os.getpid()}")
        return acquire_challenge_lock()


def git_files_changed():
    challenge_path = get_challenge_path()
    subprocess.run(['git', '--no-pager', 'fetch'], cwd=challenge_path,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    diff_output = subprocess.run(['git', '--no-pager', 'diff', '--name-only', f'{git_branch}', f'origin/{git_branch}'],
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=challenge_path)
    changed_files = diff_output.stdout.decode().split("\n")

    return changed_files


def update_challenges_from_git():
    challenge_path = get_challenge_path()

    if not challenge_path:
        return

    changed_files = git_files_changed()
    git_update()

    changed_files = list(filter(lambda path: ".md" in path or "Handout" in path or ".toml" in path, [item for item in changed_files]))

    if not changed_files:
        return

    app.logger.info("Updating challenges...")
    challenge_set = ChallengeSet(challenge_path)

    for uuid in challenge_set.categories:
        category = challenge_set.categories[uuid]
        db.update_or_create_category(category)
        if category.banner:
            subprocess.run(
                ['cp', category.path + category.banner, f"./static/banners/{uuid}.png"])

    for uuid in challenge_set.challenges:
        db.update_or_create_challenge(challenge_set.challenges[uuid])
        create_challenge_handouts(challenge_set.challenges[uuid])


def git_update():
    challenge_path = get_challenge_path()

    if not challenge_path:
        return

    # Rebase on origin, the reason we do this is to avoid conflicts when (accidentally) writing files
    subprocess.run(['git', 'checkout', f'{git_branch}'], cwd=challenge_path, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    subprocess.run(['git', '--no-pager', 'reset', '--hard', 'HEAD'], cwd=challenge_path,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['git', '--no-pager', 'pull'], cwd=challenge_path, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    return


def init_git():
    # Copy challenge directory from Read Only volume to local
    subprocess.run(['cp', '-r', f'/tmp/challenges/', '.'], stderr=subprocess.DEVNULL)
    challenge_path = get_challenge_path()

    if not challenge_path:
        return

    if not acquire_challenge_lock():
        return

    git_update()

    # Create challenge set
    app.logger.info("Importing challenges...")
    challenge_set = ChallengeSet(challenge_path)

    for uuid in challenge_set.categories:
        category = challenge_set.categories[uuid]
        db.update_or_create_category(category)
        if category.banner:
            subprocess.run(['cp', category.path + category.banner, f"./static/banners/{uuid}.png"])

    for uuid in challenge_set.challenges:
        db.update_or_create_challenge(challenge_set.challenges[uuid], legacy=True)
        create_challenge_handouts(challenge_set.challenges[uuid])



def update_git_loop():
    while True:
        try:
            time.sleep(60)
            if acquire_challenge_lock():
                update_challenges_from_git()
        except Exception as error:
            app.logger.error("Error updating git:")
            app.logger.error(error, exc_info=True)


try:
    init_git()
    update_challenges_from_git()
except Exception as e:
    app.logger.error("Error initializing git:")
    app.logger.error(e, exc_info=True)

thread = threading.Thread(target=update_git_loop)
thread.daemon = True
thread.start()
