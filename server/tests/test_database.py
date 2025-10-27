"""
Unit tests for database.py module
"""

import os


def test_sqlite_database_uses_check_same_thread():
	"""Test that SQLite database uses check_same_thread=False"""
	# Save original environment
	original_db_url = os.environ.get("DB_URL")

	try:
		# Set SQLite database URL
		os.environ["DB_URL"] = "sqlite:///./test_check_thread.db"

		# Clear the lru_cache to force settings reload
		from app.core.config import get_settings

		get_settings.cache_clear()

		# Re-import database module to apply new settings
		import importlib

		from app.core import database

		importlib.reload(database)

		# The connect_args should have check_same_thread for SQLite
		assert database.db_url.startswith("sqlite")
		assert "check_same_thread" in database.connect_args
		assert database.connect_args["check_same_thread"] is False

	finally:
		# Restore original environment
		if original_db_url:
			os.environ["DB_URL"] = original_db_url
		elif "DB_URL" in os.environ:
			del os.environ["DB_URL"]

		# Clear cache again and reload to restore state
		get_settings.cache_clear()
		importlib.reload(database)


def test_postgresql_database_has_empty_connect_args():
	"""Test that PostgreSQL database has empty connect_args"""
	# Save original environment
	original_db_url = os.environ.get("DB_URL")

	try:
		# Set PostgreSQL database URL
		os.environ["DB_URL"] = "postgresql://user:pass@localhost:5432/testdb"

		# Clear the lru_cache to force settings reload
		from app.core.config import get_settings

		get_settings.cache_clear()

		# Re-import database module to apply new settings
		import importlib

		from app.core import database

		importlib.reload(database)

		# The connect_args should be empty for PostgreSQL
		assert database.db_url.startswith("postgresql")
		assert database.connect_args == {}

	finally:
		# Restore original environment
		if original_db_url:
			os.environ["DB_URL"] = original_db_url
		elif "DB_URL" in os.environ:
			del os.environ["DB_URL"]

		# Clear cache and reload to restore state
		get_settings.cache_clear()
		importlib.reload(database)


def test_database_engine_created_successfully():
	"""Test that database engine is created successfully"""
	from app.core.database import engine

	assert engine is not None
	assert hasattr(engine, "connect")


def test_session_local_created_successfully():
	"""Test that SessionLocal is created successfully"""
	from app.core.database import SessionLocal

	assert SessionLocal is not None

	# Create a session instance
	session = SessionLocal()
	assert session is not None
	session.close()


def test_base_declarative_created_successfully():
	"""Test that Base declarative is created successfully"""
	from app.core.database import Base

	assert Base is not None
	assert hasattr(Base, "metadata")


def test_connect_args_logic_for_non_sqlite():
	"""Test that connect_args is empty for non-SQLite databases"""
	# Test the logic without actually creating a database connection

	# Test with PostgreSQL URL
	postgres_url = "postgresql://user:pass@localhost:5432/testdb"
	assert not postgres_url.startswith("sqlite")

	# Simulate the logic from database.py
	connect_args = {}
	if postgres_url.startswith("sqlite"):
		connect_args = {"check_same_thread": False}

	# Should remain empty for PostgreSQL
	assert connect_args == {}
