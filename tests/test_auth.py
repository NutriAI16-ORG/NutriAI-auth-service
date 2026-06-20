"""
NutriAI Auth Service - Comprehensive Tests
"""

import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(client):
    """Health check endpoint should return 200 and auth service identification."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "auth-service"


class TestLoginPage:
    """Tests for the login endpoint."""

    def test_login_with_valid_credentials(self, client, test_user):
        """Login with valid credentials should set cookie and return success."""
        response = client.post(
            "/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "TestPassword123!",
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.cookies
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["user"]["email"] == "testuser@example.com"

    def test_login_with_invalid_password(self, client, test_user):
        """Login with wrong password should return 401."""
        response = client.post(
            "/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "WrongPassword!",
            }
        )
        assert response.status_code == 401
        assert "error" in response.json()

    def test_login_with_nonexistent_user(self, client):
        """Login with non-existent email should return 401."""
        response = client.post(
            "/auth/login",
            json={
                "email": "nobody@example.com",
                "password": "SomePassword123!",
            }
        )
        assert response.status_code == 401
        assert "error" in response.json()


class TestRegistration:
    """Tests for user registration."""

    def test_register_with_valid_data(self, client):
        """Registration with valid data should create user and return 200."""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "full_name": "New User",
                "password": "NewPassword123!",
                "confirm_password": "NewPassword123!",
                "age": 25,
                "gender": "female",
                "weight": 60.0,
                "height": 165.0
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.cookies
        data = response.json()
        assert data["message"] == "Registration successful"
        assert data["user"]["email"] == "newuser@example.com"

    def test_register_duplicate_email(self, client, test_user):
        """Registration with existing email should return 400."""
        response = client.post(
            "/auth/register",
            json={
                "email": "testuser@example.com",
                "username": "anotheruser",
                "full_name": "Another User",
                "password": "Password123!",
                "confirm_password": "Password123!",
            }
        )
        assert response.status_code == 400
        assert "errors" in response.json()


class TestLogout:
    """Tests for the logout flow."""

    def test_logout_clears_cookie(self, authenticated_client):
        """Logout should clear the auth cookie and return success message."""
        response = authenticated_client.get("/auth/logout")
        assert response.status_code == 200
        assert "access_token" not in response.cookies or response.cookies.get("access_token") == ""
        assert response.json()["message"] == "Logged out successfully"


class TestMeRoute:
    """Tests for the /auth/me route."""

    def test_me_requires_header(self, client):
        """Accessing /auth/me without X-User-ID header should return 401."""
        response = client.get("/auth/me")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_me_accessible_with_header(self, client, test_user):
        """Accessing /auth/me with X-User-ID header should return user profile details."""
        response = client.get("/auth/me", headers={"X-User-ID": str(test_user.id)})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == str(test_user.id)
