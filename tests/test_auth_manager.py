import pytest
from myapp.auth import AuthManager, AuthenticationError
from unittest.mock import patch

@pytest.fixture
def auth_manager():
    user_store = {
        "alice": {"password": "password123", "locked": False},
        "bob": {"password": "hunter2", "locked": True},
    }
    return AuthManager(user_store)

def test_login_success_returns_valid_token(auth_manager):
    token = auth_manager.login("alice", "password123")
    assert isinstance(token, str)
    assert auth_manager.is_token_valid(token) is True

@pytest.mark.parametrize(
    "username,password",
    [("alice", "wrongpass"), ("charlie", "whatever")]
)
def test_login_invalid_credentials_raise(auth_manager, username, password):
    with pytest.raises(AuthenticationError):
        auth_manager.login(username, password)

def test_login_locked_user_raises(auth_manager):
    with pytest.raises(AuthenticationError):
        auth_manager.login("bob", "hunter2")

@pytest.mark.parametrize("username,password", [("", "x"), ("alice", ""), ("", "")])
def test_login_blank_values_raise(auth_manager, username, password):
    with pytest.raises(ValueError):
        auth_manager.login(username, password)

def test_token_expiration(monkeypatch, auth_manager):
    start = 1_000_000
    monkeypatch.setattr("myapp.auth.time", lambda: start)
    token = auth_manager.login("alice", "password123")
    monkeypatch.setattr("myapp.auth.time", lambda: start + AuthManager.TOKEN_TTL + 1)
    assert auth_manager.is_token_valid(token) is False

def test_refresh_token_returns_new_valid_token(auth_manager):
    old_token = auth_manager.login("alice", "password123")
    new_token = auth_manager.refresh_token(old_token)
    assert new_token != old_token
    assert auth_manager.is_token_valid(new_token)

def test_password_reset_sends_email(auth_manager):
    with patch("myapp.auth.email_client") as mock_email:
        auth_manager.initiate_password_reset("alice")
        mock_email.send.assert_called_once()