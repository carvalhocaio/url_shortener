from fastapi import HTTPException, Request, status
from starlette.datastructures import URL

from app import models, schemas
from app.core.config import get_settings
from app.core.database import SessionLocal


def get_db():
	"""Database session dependency"""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def raise_bad_request(message: str):
	"""Raise HTTP 400 Bad Request exception"""
	raise HTTPException(
		status_code=status.HTTP_400_BAD_REQUEST, detail=message
	)


def raise_not_found(request: Request):
	"""Raise HTTP 404 Not Found exception"""
	message = f"URL '{request.url}' doesn't exist"
	raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


def get_admin_info(db_url: models.URL, app) -> schemas.URLInfo:
	"""
	Enrich URL model with admin info (shortened url and admin url).

	Args:
		db_url: URL model from database
		app: FastAPI application instance (needed for url_path_for)

	Returns:
		URLInfo schema with enriched data
	"""
	base_url = URL(get_settings().base_url)
	admin_endpoint = app.url_path_for(
		"administration info",
		secret_key=db_url.secret_key,
	)
	db_url.url = str(base_url.replace(path=db_url.key))
	db_url.admin_url = str(base_url.replace(path=admin_endpoint))
	return db_url
