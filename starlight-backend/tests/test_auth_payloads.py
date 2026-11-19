"""Malformed JSON bodies on auth routes get a 400, not a 500."""

import pytest


@pytest.mark.parametrize(
    "body",
    [
        {"email": 123, "password": "secret-password"},
        {"email": ["a@example.com"], "password": "secret-password"},
        {"email": "a@example.com", "password": 12345678},
    ],
)
def test_login_rejects_non_string_credentials(client, body):
    response = client.post("/api/login", json=body)
    assert response.status_code == 400


@pytest.mark.parametrize("email", [123, None, {"x": 1}, "   "])
def test_forgot_password_rejects_missing_or_non_string_email(client, email):
    response = client.post("/api/forgot_password", json={"email": email})
    assert response.status_code == 400


@pytest.mark.parametrize("route", ["/api/login", "/api/forgot_password", "/api/register"])
def test_json_array_body_is_a_client_error(client, route):
    response = client.post(route, json=["not", "an", "object"])
    assert 400 <= response.status_code < 500
