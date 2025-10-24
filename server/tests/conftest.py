import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after path is set
from server import models
from server.main import app, get_db

Base = models.Base

# Set test database URL
TEST_DB_URL = os.getenv(
	"TEST_DB_URL",
	"postgresql://test_user:test_pass@localhost:5433/url_shortener_test",
)

# Create test engine with proper connect_args for PostgreSQL
connect_args = {}
test_engine = create_engine(TEST_DB_URL, connect_args=connect_args)
TestSessionLocal = sessionmaker(
	autocommit=False, autoflush=False, bind=test_engine
)


@pytest.fixture(scope="session")
def setup_test_db():
	"""Create all tables before tests and drop them after"""
	Base.metadata.create_all(bind=test_engine)
	yield
	Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(setup_test_db):
	"""Create a new database session for each test"""
	session = TestSessionLocal()
	try:
		yield session
	finally:
		session.close()


@pytest.fixture
def clean_db(db_session):
	"""Clean all data from tables between tests"""
	# Delete all data from tables
	for table in reversed(Base.metadata.sorted_tables):
		db_session.execute(table.delete())
	db_session.commit()
	yield
	# Clean up after test
	for table in reversed(Base.metadata.sorted_tables):
		db_session.execute(table.delete())
	db_session.commit()


@pytest.fixture
def client(db_session, clean_db):
	"""Create a TestClient with test database session"""

	def override_get_db():
		try:
			yield db_session
		finally:
			pass

	app.dependency_overrides[get_db] = override_get_db

	with TestClient(app) as test_client:
		yield test_client

	app.dependency_overrides.clear()
