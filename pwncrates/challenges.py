from pwncrates import app
import toml
import os
import re


class Challenge:
    def __init__(self, path, uuid):
        self.path = path + "/"
        config = toml.load(path + "/challenge.toml")
        self.name = config[uuid]["name"]
        self.uuid = uuid
        self.difficulty = config[uuid]["difficulty"]
        self.flag = config[uuid]["flag"]
        if "url" in config[uuid]:
            self.url = config[uuid]["url"]
        else:
            self.url = [""]
        self.dynamic_flags = config.get("dynamic_flags", False)
        self.handouts = []
        self.category = None
        self.description = ""

        # Runtime variables
        self.solves = []

        if os.path.exists(path + "/Description.md"):
            with open(self.path + "/Description.md") as f:
                self.description += f.read()

        if os.path.exists(self.path + "/Source/run.sh") or os.path.exists(self.path + "/Source/destroy.sh"):
            self.hosted = True
        else:
            self.hosted = False

        for dirpath, dirnames, filenames in os.walk(path + "/Handout"):
            for filename in filenames:
                relative_path = os.path.relpath(str(os.path.join(dirpath, filename)), path + "/Handout")
                self.handouts.append(relative_path)

    def allocate_port(self, generator):
        self.url = [re.sub(r"{{PORT}}", lambda match: str(next(generator)), url) for url in self.url]


class Category:
    def __init__(self, path):
        self.path = path + "/"
        config = toml.load(path + "/category.toml")
        self.challenges = []
        self.subcategories = []
        self.parent = None
        self.uuid = config["uuid"]
        self.banner = config.get("banner", "")
        self.name = config["name"]
        self.description = ""

        if os.path.exists(path + "/Description.md"):
            with open(path + "/Description.md", "r") as f:
                self.description += f.read()


class ChallengeSet:
    def allocate_ports(self):
        # Allocate port in order of uuid
        allocate_port = allocate_port_generator()
        allocated_ports = {}
        for uuid in sorted(self.challenges.keys()):
            if self.challenges[uuid].path not in allocated_ports.keys():
                self.challenges[uuid].allocate_port(allocate_port)

    def __init__(self, path: str):
        self.challenges = {}
        self.categories = {}

        for dirpath, dirnames, filenames in os.walk(path):

            # We don't want to try to parse challenge source, though this might be a bit overly aggressive
            if any(folder in dirpath for folder in ["/Source/", "/Handout/", "/Tests/"]):
                continue
            try:
                if "challenge.toml" in filenames:
                    uuids = toml.load(dirpath + "/challenge.toml").keys()
                    for uuid in uuids:
                        if uuid in self.challenges.keys() or uuid in self.categories.keys():
                            app.logger.warning(f"Duplicate uuid found: {uuid}", "red")
                            continue

                        self.challenges[uuid] = Challenge(dirpath, uuid)

                        # Link to category
                        category_uuid = toml.load(dirpath + "/../category.toml")["uuid"]
                        self.categories[category_uuid].challenges.append(self.challenges[uuid])
                        self.challenges[uuid].category = category_uuid
                if "category.toml" in filenames:
                    uuid = toml.load(dirpath + "/category.toml")["uuid"]
                    if uuid in self.challenges.keys() or uuid in self.categories.keys():
                        app.logger.warning(f"Warning: Duplicate uuid found: {uuid}")

                    self.categories[uuid] = Category(dirpath)

                    # Link to upper category, if exists
                    if os.path.isfile(dirpath + "/../category.toml"):
                        category_uuid = toml.load(dirpath + "/../category.toml")["uuid"]
                        self.categories[category_uuid].subcategories.append(self.categories[uuid])
                        self.categories[uuid].parent = category_uuid

            except Exception as e:
                app.logger.error(f"Error with {dirpath}: {e}", "red")

        self.allocate_ports()

def allocate_port_generator():
    current = 4000
    while current < 5000:
        yield current
        current += 1
    raise Exception("Exhausted all ports.")
