"""
Pytest setup as described in https://flask.palletsprojects.com/en/3.0.x/testing/
"""
import os

# Bit ugly, we don't have an 'app factory'. Instead, creating only a single Flask application. So instead we pretend.
from pwncrates import app as create_app
import pytest


@pytest.fixture()
def app():
    # Ensure tests are run against a clean database, this should be run inside the Docker container
    # which should ensure the database is clean.
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
