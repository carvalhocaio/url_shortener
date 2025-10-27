"""
Unit tests for GET /peek/{url_key} endpoint
"""

from datetime import datetime

from fastapi import status


def test_peek_returns_target_url(client):
	"""Test that peek endpoint returns the correct target URL"""
	target_url = "https://example.com/test-peek"

	# Create a URL
	create_response = client.post("/url", json={"target_url": target_url})
	assert create_response.status_code == status.HTTP_201_CREATED
	created_data = create_response.json()
	url_key = created_data["url"].split("/")[-1]

	# Peek at the URL
	peek_response = client.get(f"/peek/{url_key}")
	assert peek_response.status_code == status.HTTP_200_OK

	peek_data = peek_response.json()
	assert peek_data["target_url"] == target_url
	assert peek_data["key"] == url_key


def test_peek_returns_all_required_fields(client):
	"""Test that peek returns all required fields"""
	target_url = "https://example.com/all-fields"

	# Create a URL
	create_response = client.post("/url", json={"target_url": target_url})
	created_data = create_response.json()
	url_key = created_data["url"].split("/")[-1]

	# Peek at the URL
	peek_response = client.get(f"/peek/{url_key}")
	peek_data = peek_response.json()

	# Verify all fields are present
	assert "key" in peek_data
	assert "target_url" in peek_data
	assert "is_active" in peek_data
	assert "clicks" in peek_data
	assert "created_at" in peek_data

	# Verify field types and values
	assert peek_data["key"] == url_key
	assert peek_data["target_url"] == target_url
	assert peek_data["is_active"] is True
	assert peek_data["clicks"] == 0
	assert isinstance(peek_data["created_at"], str)  # ISO format datetime


def test_peek_does_not_increment_clicks(client):
	"""Test that peeking at a URL does NOT increment the click counter"""
	target_url = "https://example.com/no-increment"

	# Create a URL
	create_response = client.post("/url", json={"target_url": target_url})
	created_data = create_response.json()
	url_key = created_data["url"].split("/")[-1]

	# Initial state: 0 clicks
	peek_response1 = client.get(f"/peek/{url_key}")
	assert peek_response1.json()["clicks"] == 0

	# Peek multiple times
	for _ in range(5):
		peek_response = client.get(f"/peek/{url_key}")
		assert peek_response.status_code == status.HTTP_200_OK

	# Verify clicks counter is still 0
	peek_response_final = client.get(f"/peek/{url_key}")
	assert peek_response_final.json()["clicks"] == 0


def test_peek_vs_redirect_click_behavior(client):
	"""Test that peek doesn't increment clicks but redirect does"""
	target_url = "https://example.com/click-behavior"

	# Create a URL
	create_response = client.post("/url", json={"target_url": target_url})
	created_data = create_response.json()
	url_key = created_data["url"].split("/")[-1]

	# Peek first - should not increment
	peek_response1 = client.get(f"/peek/{url_key}")
	assert peek_response1.json()["clicks"] == 0

	# Redirect (actual visit) - should increment
	redirect_response = client.get(f"/{url_key}", follow_redirects=False)
	assert redirect_response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

	# Peek again - should show 1 click now
	peek_response2 = client.get(f"/peek/{url_key}")
	assert peek_response2.json()["clicks"] == 1

	# Another redirect
	client.get(f"/{url_key}", follow_redirects=False)

	# Peek should show 2 clicks
	peek_response3 = client.get(f"/peek/{url_key}")
	assert peek_response3.json()["clicks"] == 2


def test_peek_works_with_inactive_url(client):
	"""Test that peek returns data even for inactive (deleted) URLs"""
	target_url = "https://example.com/inactive-url"

	# Create a URL
	create_response = client.post("/url", json={"target_url": target_url})
	created_data = create_response.json()
	url_key = created_data["url"].split("/")[-1]
	secret_key = created_data["admin_url"].split("/")[-1]

	# Delete the URL (soft delete)
	delete_response = client.delete(f"/admin/{secret_key}")
	assert delete_response.status_code == status.HTTP_200_OK

	# Redirect should now fail (404)
	redirect_response = client.get(f"/{url_key}", follow_redirects=False)
	assert redirect_response.status_code == status.HTTP_404_NOT_FOUND

	# But peek should still work and show is_active=False
	peek_response = client.get(f"/peek/{url_key}")
	assert peek_response.status_code == status.HTTP_200_OK

	peek_data = peek_response.json()
	assert peek_data["key"] == url_key
	assert peek_data["target_url"] == target_url
	assert peek_data["is_active"] is False


def test_peek_returns_404_for_nonexistent_url(client):
	"""Test that peek returns 404 for URLs that don't exist"""
	nonexistent_key = "NOTFOUND123"

	peek_response = client.get(f"/peek/{nonexistent_key}")

	assert peek_response.status_code == status.HTTP_404_NOT_FOUND
	assert "doesn't exist" in peek_response.json()["detail"]


def test_peek_with_custom_key(client):
	"""Test peek works with custom URL keys"""
	target_url = "https://example.com/custom"
	custom_key = "my-custom-key"

	# Create URL with custom key
	create_response = client.post(
		"/url", json={"target_url": target_url, "custom_key": custom_key}
	)
	assert create_response.status_code == status.HTTP_201_CREATED

	# Peek at custom key
	peek_response = client.get(f"/peek/{custom_key}")
	assert peek_response.status_code == status.HTTP_200_OK

	peek_data = peek_response.json()
	assert peek_data["key"] == custom_key
	assert peek_data["target_url"] == target_url


def test_peek_created_at_is_valid_datetime(client):
	"""Test that created_at field contains a valid datetime"""
	target_url = "https://example.com/datetime-test"

	# Create a URL
	create_response = client.post("/url", json={"target_url": target_url})
	created_data = create_response.json()
	url_key = created_data["url"].split("/")[-1]

	# Peek at the URL
	peek_response = client.get(f"/peek/{url_key}")
	peek_data = peek_response.json()

	# Verify created_at is a valid ISO datetime string
	created_at_str = peek_data["created_at"]
	assert isinstance(created_at_str, str)

	# Parse the datetime (will raise if invalid format)
	created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
	assert isinstance(created_at, datetime)

	# Verify it's a recent timestamp (within last minute)
	from datetime import timedelta, timezone

	now = datetime.now(timezone.utc)
	time_diff = now - created_at.replace(tzinfo=timezone.utc)
	assert time_diff < timedelta(minutes=1)


def test_peek_does_not_require_authentication(client):
	"""Test that peek endpoint is publicly accessible without secret key"""
	target_url = "https://example.com/public-peek"

	# Create a URL
	create_response = client.post("/url", json={"target_url": target_url})
	created_data = create_response.json()
	url_key = created_data["url"].split("/")[-1]

	# Peek should work without any authentication/secret_key
	peek_response = client.get(f"/peek/{url_key}")
	assert peek_response.status_code == status.HTTP_200_OK
	assert peek_response.json()["target_url"] == target_url
