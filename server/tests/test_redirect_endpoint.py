"""
Unit tests for GET /{url_key} endpoint
"""

from fastapi import status


def test_redirect_to_target_url(client):
	"""Test that accessing shortened URL redirects to target URL"""
	target_url = "https://www.example.com/test-redirect"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	assert create_response.status_code == status.HTTP_201_CREATED

	data = create_response.json()
	url_key = data["url"].split("/")[-1]

	# Access shortened URL (don't follow redirects to check status code)
	redirect_response = client.get(f"/{url_key}", follow_redirects=False)

	assert redirect_response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
	assert redirect_response.headers["location"] == target_url


def test_redirect_increments_click_count(client):
	"""Test that accessing shortened URL increments click count"""
	target_url = "https://www.example.com/test-clicks"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	url_key = data["url"].split("/")[-1]
	secret_key = data["admin_url"].split("/")[-1]

	# Initial clicks should be 0
	assert data["clicks"] == 0

	# Access shortened URL
	client.get(f"/{url_key}", follow_redirects=False)

	# Check clicks increased
	admin_response = client.get(f"/admin/{secret_key}")
	assert admin_response.json()["clicks"] == 1


def test_redirect_with_nonexistent_key_returns_404(client):
	"""Test that accessing non-existent URL key returns 404"""
	response = client.get("/nonexistent-key-12345")

	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert "doesn't exist" in response.json()["detail"]


def test_redirect_multiple_times_increments_correctly(client):
	"""Test that multiple accesses increment click count correctly"""
	target_url = "https://www.example.com/multiple-clicks"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	url_key = data["url"].split("/")[-1]
	secret_key = data["admin_url"].split("/")[-1]

	# Access multiple times
	for i in range(5):
		redirect_response = client.get(f"/{url_key}", follow_redirects=False)
		assert (
			redirect_response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
		)

	# Verify clicks
	admin_response = client.get(f"/admin/{secret_key}")
	assert admin_response.json()["clicks"] == 5


def test_inactive_url_returns_404(client):
	"""Test that accessing inactive (deleted) URL returns 404"""
	target_url = "https://www.example.com/to-be-deleted"

	# Create and delete URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	url_key = data["url"].split("/")[-1]
	secret_key = data["admin_url"].split("/")[-1]

	# Delete URL
	delete_response = client.delete(f"/admin/{secret_key}")
	assert delete_response.status_code == status.HTTP_200_OK

	# Try to access deleted URL
	response = client.get(f"/{url_key}")
	assert response.status_code == status.HTTP_404_NOT_FOUND
