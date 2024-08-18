"""
Testing for the login flow, asserts:
- Register page exists
- Login page exists
- User can register
- User can log in

NOTE: Does not test
- Discord OAuth flow
- Registration email confirmation
"""
import pytest


def test_register_200(client):
    response = client.get("/register")
    assert response.status == '200 OK'


def test_login_200(client):
    response = client.get("/register")
    assert response.status == '200 OK'


@pytest.mark.parametrize("test_input,expected_response_data,expected_redirect",
                         [
                             ({"username": "Flask", "email": "a@a.a", "password": ""}, "Registered", "/login"),
                             ({"username": "Flask", "email": "a@a.a", "password": ""}, "Email already taken", ""),
                             ({"username": "Flask", "email": "a@a.a"}, "Missing parameters", "")
                         ])
def test_register(client, test_input, expected_response_data, expected_redirect):
    with client:
        response = client.post("/register", data=test_input)
        if expected_redirect:
            assert response.headers.get("Location") == expected_redirect
            response = client.get(expected_redirect)
        assert expected_response_data.encode() in response.data


@pytest.mark.parametrize("test_input,expected_response_data,expected_redirect",
                         [
                             ({"email": "a@a.a", "password": ""}, "Profile", "/challenges"),
                             ({"email": "a@a.a", "password": "aa"}, "Invalid credentials", ""),
                             ({"email": "a@a.a"}, "Invalid credentials", "")
                         ])
def test_login(client, test_input, expected_response_data, expected_redirect):
    with client:
        response = client.post("/login", data=test_input)
        if expected_redirect:
            assert response.headers.get("Location") == expected_redirect
            response = client.get(expected_redirect)
        assert expected_response_data.encode() in response.data
