"""
Unit tests for GET /admin/{secret_key} endpoint
"""

from fastapi import status


def test_admin_info_returns_all_required_fields(client):
	"""Test that GET /admin/{secret_key} returns all required fields"""
	target_url = "https://www.example.com/admin-test"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Get admin info
	response = client.get(f"/admin/{secret_key}")

	assert response.status_code == status.HTTP_200_OK

	admin_data = response.json()

	# Validate all required fields are present
	assert "target_url" in admin_data
	assert "is_active" in admin_data
	assert "clicks" in admin_data
	assert "url" in admin_data
	assert "admin_url" in admin_data

	# Validate field values
	assert admin_data["target_url"] == target_url
	assert admin_data["is_active"] is True
	assert admin_data["clicks"] == 0
	assert isinstance(admin_data["url"], str)
	assert isinstance(admin_data["admin_url"], str)


def test_admin_info_shows_correct_click_count(client):
	"""Test that admin info shows correct click count after redirects"""
	target_url = "https://www.example.com/click-tracking"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	url_key = data["url"].split("/")[-1]
	secret_key = data["admin_url"].split("/")[-1]

	# Access URL 3 times
	for _ in range(3):
		client.get(f"/{url_key}", follow_redirects=False)

	# Check admin info
	response = client.get(f"/admin/{secret_key}")

	assert response.status_code == status.HTTP_200_OK
	assert response.json()["clicks"] == 3


def test_admin_info_with_nonexistent_secret_key_returns_404(client):
	"""Test that accessing admin with non-existent secret key returns 404"""
	response = client.get("/admin/nonexistent_secret_key_xyz123")

	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert "doesn't exist" in response.json()["detail"]


def test_admin_info_shows_is_active_true(client):
	"""Test that admin info shows is_active as true for active URLs"""
	target_url = "https://www.example.com/active-url"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Get admin info
	response = client.get(f"/admin/{secret_key}")

	assert response.status_code == status.HTTP_200_OK
	assert response.json()["is_active"] is True


def test_admin_info_after_deletion_returns_404(client):
	"""Test that admin info returns 404 after URL is deleted"""
	target_url = "https://www.example.com/to-delete"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Delete URL
	delete_response = client.delete(f"/admin/{secret_key}")
	assert delete_response.status_code == status.HTTP_200_OK

	# Try to get admin info
	response = client.get(f"/admin/{secret_key}")
	assert response.status_code == status.HTTP_404_NOT_FOUND


def test_admin_info_url_field_is_valid(client):
	"""Test that the 'url' field in admin info is a valid shortened URL"""
	target_url = "https://www.example.com/url-validation"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Get admin info
	response = client.get(f"/admin/{secret_key}")
	admin_data = response.json()

	# Extract url_key from url field
	url_key = admin_data["url"].split("/")[-1]

	# Verify the URL works
	redirect_response = client.get(f"/{url_key}", follow_redirects=False)
	assert redirect_response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


def test_admin_info_admin_url_field_is_valid(client):
	"""Test that the 'admin_url' field in admin info points back to itself"""
	target_url = "https://www.example.com/admin-url-validation"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Get admin info
	response = client.get(f"/admin/{secret_key}")
	admin_data = response.json()

	# The admin_url should contain the same secret_key
	assert secret_key in admin_data["admin_url"]
