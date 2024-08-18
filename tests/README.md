## Tests
*WARNING: unit tests currently only work in the context of the docker container. Running tests outside of this context
MAY result in complete loss of any pre-existing database*

To run the tests simply run:
```bash
 docker-compose --profile test up --build --remove-orphans
```

#### Adding tests
To add a test simply add a new python file in the `./tests/` (this) directory with the name `test_<something>.py`.
Any function in this file with either `_test` or `test_` in the filename will be run by pytest. For a reference
implementation see `test_auth.py`.

#### Reading material
- https://flask.palletsprojects.com/en/3.0.x/testing/
- https://emimartin.me/pytest_best_practices