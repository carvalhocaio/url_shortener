from sqlalchemy.orm import Session

from app import models, schemas
from app.utils import keygen


def create_db_url(db: Session, url: schemas.URLBase) -> models.URL:
	# Use custom key if provided, otherwise generate random key
	if url.custom_key:
		# Custom key is already validated by Pydantic schema
		# Just need to check if it's available
		if not keygen.is_key_available(db, url.custom_key):
			# This will be handled by the endpoint with HTTPException
			# Return None to signal key is taken
			return None
		key = url.custom_key
	else:
		key = keygen.create_unique_random_key(db)

	secret_key = f"{key}_{keygen.create_random_key(length=8)}"
	db_url = models.URL(
		target_url=url.target_url,
		key=key,
		secret_key=secret_key,
	)

	db.add(db_url)
	db.commit()
	db.refresh(db_url)

	return db_url


def get_db_url_by_key(db: Session, url_key: str) -> models.URL:
	return (
		db.query(models.URL)
		.filter(models.URL.key == url_key, models.URL.is_active)
		.first()
	)


def get_db_url_for_peek(db: Session, url_key: str) -> models.URL:
	"""
	Get URL by key for peek operation (returns even if inactive).

	Args:
		db: Database session
		url_key: URL key

	Returns:
		URL model if exists, None otherwise
	"""
	return db.query(models.URL).filter(models.URL.key == url_key).first()


def key_exists_in_db(db: Session, key: str) -> bool:
	"""
	Check if a key exists in the database (regardless of is_active status).

	Args:
		db: Database session
		key: URL key to check

	Returns:
		True if key exists, False otherwise
	"""
	return (
		db.query(models.URL).filter(models.URL.key == key).first() is not None
	)


def get_db_url_by_secret_key(db: Session, secret_key: str) -> models.URL:
	return (
		db.query(models.URL)
		.filter(models.URL.secret_key == secret_key, models.URL.is_active)
		.first()
	)


def update_db_clicks(db: Session, db_url: schemas.URL) -> models.URL:
	db_url.clicks += 1
	db.commit()
	db.refresh(db_url)
	return db_url


def deactivate_db_url_by_secret_key(
	db: Session, secret_key: str
) -> models.URL:
	db_url = get_db_url_by_secret_key(db, secret_key)
	if db_url:
		db_url.is_active = False
		db.commit()
		db.refresh(db_url)

	return db_url
