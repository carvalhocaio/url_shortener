import secrets
import string

from sqlalchemy.orm import Session

from . import crud


def create_random_key(length: int = 5) -> str:
	chars = string.ascii_uppercase + string.digits
	return "".join(secrets.choice(chars) for _ in range(length))


def create_unique_random_key(db: Session) -> str:
	key = create_random_key()
	while crud.get_db_url_by_key(db, key):
		key = create_random_key()
	return key


def is_key_available(db: Session, key: str) -> bool:
	"""
	Check if a custom key is available (not already in use).

	This checks if the key exists in the database regardless of is_active
	status, since the key column has a UNIQUE constraint.

	Args:
		db: Database session
		key: Custom key to check

	Returns:
		True if available, False if already taken
	"""
	return not crud.key_exists_in_db(db, key)
