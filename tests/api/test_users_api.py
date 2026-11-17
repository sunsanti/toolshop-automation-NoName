import pytest

pytestmark = pytest.mark.api


def test_register_empty_body_returns_422_with_field_errors(api):
    """Goal: server-side validation.
    Precondition: none.
    Expected: 422 and error lists for 'email' and 'password'."""
    response = api.post("/users/register", data={})
    assert response.status == 422, response.text()
    errors = response.json()
    assert "email" in errors and "password" in errors, errors


@pytest.mark.smoke
def test_users_me_with_token_returns_own_profile(api, auth_headers, test_user):
    """Goal: bearer token grants access.
    Precondition: user registered by the test_user fixture.
    Expected: 200 and the same email."""
    response = api.get("/users/me", headers=auth_headers)
    assert response.status == 200, response.text()
    assert response.json()["email"] == test_user["email"]
