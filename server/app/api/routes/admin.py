from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app import schemas
from app.api import crud
from app.api.deps import get_admin_info, get_db, raise_not_found

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
	"/{secret_key}",
	name="administration info",
	response_model=schemas.URLInfo,
)
def get_url_info(
	secret_key: str, request: Request, db: Session = Depends(get_db)
):
	"""
	Get URL information using admin secret key.

	Args:
		secret_key: Admin secret key for the URL
		request: FastAPI request object
		db: Database session

	Returns:
		URLInfo with full URL details

	Raises:
		404: Secret key not found or URL inactive
	"""
	if db_url := crud.get_db_url_by_secret_key(db, secret_key=secret_key):
		return get_admin_info(db_url, request.app)
	else:
		raise_not_found(request)


@router.delete("/{secret_key}")
def delete_url(
	secret_key: str, request: Request, db: Session = Depends(get_db)
):
	"""
	Delete (deactivate) a URL using admin secret key.

	Args:
		secret_key: Admin secret key for the URL
		request: FastAPI request object
		db: Database session

	Returns:
		Success message with deleted URL target

	Raises:
		404: Secret key not found or URL already inactive
	"""
	if db_url := crud.deactivate_db_url_by_secret_key(
		db, secret_key=secret_key
	):
		message = (
			f"Successfully deleted shortened URL for '{db_url.target_url}'"
		)
		return {"detail": message}
	else:
		raise_not_found(request)
