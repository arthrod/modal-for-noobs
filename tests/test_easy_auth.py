# Framework: pytest
# Tests for EasyAuth – using pytest framework

import pytest
from path.to.easy_auth import EasyAuth, InvalidTokenError, AuthError  # adjust path to your module
from unittest.mock import patch, MagicMock

@pytest.fixture()
def auth():
    """
    Returns an EasyAuth instance configured with dummy parameters.
    """
    return EasyAuth(secret="dummy-secret", issuer="my-svc")

@pytest.mark.parametrize("username,password", [
    ("alice", "wonder"),
    ("bob", "builder"),
])
def test_login_success(auth, username, password):
    token = auth.login(username, password)
    assert isinstance(token, str)
    # A JWT consists of three segments separated by dots
    assert token.count(".") == 2

def test_validate_token_success(auth):
    token = auth.login("charlie", "chocolate")
    payload = auth.validate_token(token)
    assert payload.get("sub") == "charlie"

@pytest.mark.parametrize("username,password", [
    ("", "pwd"),
    ("user", ""),
    (None, "pwd"),
])
def test_login_invalid_credentials(auth, username, password):
    with pytest.raises(AuthError):
        auth.login(username, password)

def test_validate_token_expired(auth, monkeypatch):
    token = auth.login("dan", "dandelion")
    # Simulate expiry: assume EasyAuth._issued_at(token) returns iat timestamp
    monkeypatch.setattr(auth, "_now", lambda: auth._issued_at(token) + 4000)
    with pytest.raises(InvalidTokenError):
        auth.validate_token(token)

def test_refresh_token_calls_remote(auth):
    # Mock external HTTP POST for token refresh
    with patch("path.to.easy_auth.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"token": "new-jwt"}
        new_token = auth.refresh_token("old-jwt")
        mock_post.assert_called_once()
        assert new_token == "new-jwt"

@pytest.mark.parametrize("username", [
    "' OR 1=1 --",
    "😀",
    "a" * 5000,
])
def test_username_edge_cases(auth, username):
    with pytest.raises(AuthError):
        auth.login(username, "irrelevant")