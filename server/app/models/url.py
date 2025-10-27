from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.core.database import Base


def utc_now():
	"""Return current UTC time as timezone-aware datetime."""
	return datetime.now(UTC)


class URL(Base):
	__tablename__ = "urls"

	id = Column(Integer, primary_key=True)
	key = Column(String, unique=True, index=True)
	secret_key = Column(String, unique=True, index=True)
	target_url = Column(String, index=True)
	is_active = Column(Boolean, default=True)
	clicks = Column(Integer, default=0)
	created_at = Column(DateTime, default=utc_now, nullable=False)
