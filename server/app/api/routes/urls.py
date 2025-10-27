import validators
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import schemas
from app.api import crud
from app.api.deps import (
	get_admin_info,
	get_db,
	raise_bad_request,
	raise_not_found,
)

router = APIRouter()


@router.get("/")
def read_root():
	"""Welcome endpoint"""
	return "Welcome to the URL shortener API :)"


@router.post(
	"/url",
	response_model=schemas.URLInfo,
	status_code=status.HTTP_201_CREATED,
)
def create_url(
	url: schemas.URLBase, request: Request, db: Session = Depends(get_db)
):
	"""
	Create a shortened URL.

	Args:
		url: URLBase with target_url and optional custom_key
		request: FastAPI request object
		db: Database session

	Returns:
		URLInfo with shortened URL details

	Raises:
		400: Invalid URL or custom key format
		409: Custom key already in use
	"""
	if not validators.url(url.target_url):
		raise_bad_request(message="Your provided URL is not valid")

	db_url = crud.create_db_url(db=db, url=url)

	# If db_url is None, it means the custom key is already taken
	if db_url is None:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail=f"Custom key '{url.custom_key}' is already in use",
		)

	return get_admin_info(db_url, request.app)


@router.get("/{url_key}")
def forward_to_target_url(
	url_key: str,
	request: Request,
	db: Session = Depends(get_db),
):
	"""
	Redirect to the original URL.

	Args:
		url_key: Short URL key
		request: FastAPI request object
		db: Database session

	Returns:
		RedirectResponse to the original URL

	Raises:
		404: URL key not found or inactive
	"""
	if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
		crud.update_db_clicks(db=db, db_url=db_url)
		return RedirectResponse(db_url.target_url)
	else:
		raise_not_found(request)
