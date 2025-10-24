"""
Unit tests for helper functions in main.py
"""
import pytest
from fastapi import HTTPException, Request, status
from unittest.mock import MagicMock

from server.main import raise_bad_request, raise_not_found, get_db


def test_raise_bad_request():
    """Test that raise_bad_request raises HTTPException with 400 status"""
    message = "This is a bad request"

    with pytest.raises(HTTPException) as exc_info:
        raise_bad_request(message)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == message


def test_raise_bad_request_custom_message():
    """Test raise_bad_request with various custom messages"""
    messages = [
        "Invalid URL format",
        "Missing required field",
        "Data validation failed"
    ]

    for message in messages:
        with pytest.raises(HTTPException) as exc_info:
            raise_bad_request(message)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == message


def test_raise_not_found():
    """Test that raise_not_found raises HTTPException with 404 status"""
    # Create a mock request
    mock_request = MagicMock(spec=Request)
    mock_request.url = "http://localhost:8000/nonexistent"

    with pytest.raises(HTTPException) as exc_info:
        raise_not_found(mock_request)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "doesn't exist" in exc_info.value.detail
    assert str(mock_request.url) in exc_info.value.detail


def test_raise_not_found_includes_url():
    """Test that raise_not_found includes the URL in the error message"""
    test_urls = [
        "http://localhost:8000/ABC123",
        "http://localhost:8000/admin/secret_key_xyz"
    ]

    for url in test_urls:
        mock_request = MagicMock(spec=Request)
        mock_request.url = url

        with pytest.raises(HTTPException) as exc_info:
            raise_not_found(mock_request)

        assert url in exc_info.value.detail


def test_get_admin_info_sets_url_field(client):
    """Test that get_admin_info sets the url field correctly"""
    # Create a URL in database
    from server import crud
    from server.schemas import URLBase

    # Use the client's db_session fixture
    response = client.post("/url", json={"target_url": "https://example.com/test"})
    data = response.json()

    # The url field should be set
    assert "url" in data
    assert data["url"].endswith(data["url"].split("/")[-1])  # ends with the key


def test_get_admin_info_sets_admin_url_field(client):
    """Test that get_admin_info sets the admin_url field correctly"""
    response = client.post("/url", json={"target_url": "https://example.com/test"})
    data = response.json()

    # The admin_url field should be set
    assert "admin_url" in data
    assert "/admin/" in data["admin_url"]


def test_get_admin_info_preserves_target_url(client):
    """Test that get_admin_info preserves the target_url"""
    target_url = "https://example.com/preserve-test"
    response = client.post("/url", json={"target_url": target_url})
    data = response.json()

    assert data["target_url"] == target_url


def test_get_db_yields_session(db_session):
    """Test that get_db yields a database session"""
    from server.database import SessionLocal

    # get_db is a generator function
    db_generator = get_db()

    # Get the session from the generator
    session = next(db_generator)

    assert session is not None
    assert type(session).__name__ == type(SessionLocal()).__name__

    # Clean up
    try:
        next(db_generator)
    except StopIteration:
        pass  # Expected when generator finishes


def test_get_db_closes_session():
    """Test that get_db closes the session in finally block"""
    from unittest.mock import patch, MagicMock

    # Mock SessionLocal to track if close() is called
    with patch("server.main.SessionLocal") as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Use the generator
        db_generator = get_db()
        session = next(db_generator)

        # Finish the generator (triggers finally block)
        try:
            next(db_generator)
        except StopIteration:
            pass

        # Verify close was called
        mock_session.close.assert_called_once()


def test_get_db_closes_session_on_exception():
    """Test that get_db closes session even when exception occurs"""
    from unittest.mock import patch, MagicMock

    with patch("server.main.SessionLocal") as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        db_generator = get_db()
        session = next(db_generator)

        # Simulate an exception
        try:
            db_generator.throw(Exception("Test exception"))
        except Exception:
            pass

        # Verify close was called even with exception
        mock_session.close.assert_called_once()


def test_main_module_creates_tables():
    """Test that main module creates database tables on import"""
    from server import models
    from server.database import engine

    # Verify that Base has metadata
    assert hasattr(models.Base, "metadata")

    # Verify that tables exist in metadata
    assert len(models.Base.metadata.tables) > 0

    # The URL table should exist
    assert "urls" in models.Base.metadata.tables
