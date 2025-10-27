from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class URLBase(BaseModel):
	target_url: str
	custom_key: Optional[str] = Field(
		None,
		min_length=3,
		max_length=50,
		pattern=r"^[a-zA-Z0-9_-]+$",
		description="Custom URL key (alphanumeric, hyphens, underscores)",
	)

	@field_validator("custom_key")
	@classmethod
	def validate_custom_key_not_reserved(
		cls, v: Optional[str]
	) -> Optional[str]:
		if v is None:
			return v

		# List of reserved keywords
		reserved = {
			"admin",
			"api",
			"url",
			"static",
			"docs",
			"redoc",
			"openapi",
			"health",
			"metrics",
		}

		if v.lower() in reserved:
			raise ValueError(f"'{v}' is a reserved keyword and cannot be used")

		return v


class URL(BaseModel):
	"""URL response schema (without custom_key, as it becomes the key)"""

	target_url: str
	is_active: bool
	clicks: int

	model_config = {"from_attributes": True}


class URLInfo(URL):
	url: str
	admin_url: str


class URLPeek(BaseModel):
	"""Schema for peeking at a shortened URL without redirecting"""

	key: str
	target_url: str
	is_active: bool
	clicks: int
	created_at: datetime

	model_config = {"from_attributes": True}
