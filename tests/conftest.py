"""
Pytest setup as described in https://flask.palletsprojects.com/en/3.0.x/testing/
"""
import os
# Ensure tests are run against a clean database
os.system('mv /webapp/db/pwncrates.db /tmp/pwncrates.db')

# Bit ugly, we don't have an 'app factory'. Instead, creating only a single Flask application. So instead we pretend.
from webapp import app as create_app
import pytest


@pytest.fixture()
def app():
    app = create_app
    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
