"""
Unit tests for keygen.py module
"""
import string
from unittest.mock import MagicMock, patch

import pytest

from server import keygen


def test_create_random_key_default_length():
    """Test that create_random_key generates key with default length of 5"""
    key = keygen.create_random_key()

    assert len(key) == 5
    assert all(c in string.ascii_uppercase + string.digits for c in key)


def test_create_random_key_custom_length():
    """Test that create_random_key generates key with custom length"""
    length = 10
    key = keygen.create_random_key(length=length)

    assert len(key) == length
    assert all(c in string.ascii_uppercase + string.digits for c in key)


def test_create_random_key_generates_different_keys():
    """Test that create_random_key generates different keys on multiple calls"""
    keys = [keygen.create_random_key() for _ in range(100)]

    # Should have at least some unique keys (very unlikely to have all duplicates)
    assert len(set(keys)) > 1


def test_create_random_key_only_uppercase_and_digits():
    """Test that generated key only contains uppercase letters and digits"""
    key = keygen.create_random_key(length=20)

    for char in key:
        assert char in string.ascii_uppercase or char in string.digits


def test_create_unique_random_key_returns_unique_key(client, db_session):
    """Test that create_unique_random_key returns a key not in database"""
    # Create some URLs in database
    from server.schemas import URLBase
    from server import crud

    crud.create_db_url(db_session, URLBase(target_url="https://example.com/1"))
    crud.create_db_url(db_session, URLBase(target_url="https://example.com/2"))
    crud.create_db_url(db_session, URLBase(target_url="https://example.com/3"))

    # Generate unique key
    unique_key = keygen.create_unique_random_key(db_session)

    # Verify it's not in database
    result = crud.get_db_url_by_key(db_session, unique_key)
    assert result is None


def test_create_unique_random_key_handles_collision(db_session):
    """Test that create_unique_random_key handles key collision by retrying"""
    from server.schemas import URLBase
    from server import crud

    # Create a URL with a specific key
    existing_url = crud.create_db_url(
        db_session, URLBase(target_url="https://example.com/collision")
    )
    existing_key = existing_url.key

    # Mock create_random_key to return existing key first, then a new key
    with patch("server.keygen.create_random_key") as mock_create:
        # First call returns existing key (collision), second call returns new key
        mock_create.side_effect = [existing_key, "NEWKEY123"]

        # This should handle the collision and return the new key
        unique_key = keygen.create_unique_random_key(db_session)

        # Should have called create_random_key twice due to collision
        assert mock_create.call_count == 2
        assert unique_key == "NEWKEY123"


def test_create_unique_random_key_multiple_collisions(db_session):
    """Test that create_unique_random_key handles multiple collisions"""
    from server.schemas import URLBase
    from server import crud

    # Create URLs with specific keys
    url1 = crud.create_db_url(db_session, URLBase(target_url="https://example.com/1"))
    url2 = crud.create_db_url(db_session, URLBase(target_url="https://example.com/2"))
    key1 = url1.key
    key2 = url2.key

    # Mock create_random_key to return existing keys multiple times
    with patch("server.keygen.create_random_key") as mock_create:
        # First two calls return existing keys, third returns new key
        mock_create.side_effect = [key1, key2, "UNIQUE999"]

        unique_key = keygen.create_unique_random_key(db_session)

        # Should have called create_random_key three times
        assert mock_create.call_count == 3
        assert unique_key == "UNIQUE999"


def test_create_random_key_length_one():
    """Test that create_random_key works with length of 1"""
    key = keygen.create_random_key(length=1)

    assert len(key) == 1
    assert key in string.ascii_uppercase + string.digits


def test_create_random_key_large_length():
    """Test that create_random_key works with large length"""
    length = 100
    key = keygen.create_random_key(length=length)

    assert len(key) == length
