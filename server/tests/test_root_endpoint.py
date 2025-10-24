"""
Unit tests for GET / endpoint
"""
from fastapi import status

def test_root_returns_welcome_message(client):
    """Test that root endpoint returns expected welcome message"""
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.text == '"Welcome to the URL shortener API :)"'


def test_root_endpoint_content_type(client):
    """Test that root endpoint returns correct content type"""
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert "application/json" in response.headers["content-type"]
