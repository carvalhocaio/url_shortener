"""
Unit tests for POST /url endpoint
"""

from fastapi import status


def test_create_url_returns_all_required_fields(client):
	"""Test that POST /url returns all required fields"""
	target_url = "https://www.example.com/test"

	response = client.post("/url", json={"target_url": target_url})

	assert response.status_code == status.HTTP_200_OK

	data = response.json()

	# Validate all required fields are present
	assert "target_url" in data
	assert "is_active" in data
	assert "clicks" in data
	assert "url" in data
	assert "admin_url" in data

	# Validate field values
	assert data["target_url"] == target_url
	assert data["is_active"] is True
	assert data["clicks"] == 0
	assert isinstance(data["url"], str)
	assert isinstance(data["admin_url"], str)


def test_create_url_admin_url_is_accessible(client):
	"""Test that admin_url returned by POST /url is accessible"""
	target_url = "https://www.example.com/test"

	# Create URL
	create_response = client.post("/url", json={"target_url": target_url})
	assert create_response.status_code == status.HTTP_200_OK

	data = create_response.json()
	admin_url = data["admin_url"]

	# Extract secret_key from admin_url
	secret_key = admin_url.split("/")[-1]

	# Validate admin endpoint returns 200
	admin_response = client.get(f"/admin/{secret_key}")
	assert admin_response.status_code == status.HTTP_200_OK


def test_create_url_with_invalid_url_returns_400(client):
	"""Test that creating URL with invalid URL returns 400"""
	response = client.post("/url", json={"target_url": "not-a-valid-url"})

	assert response.status_code == status.HTTP_400_BAD_REQUEST
	assert "not valid" in response.json()["detail"]


def test_create_url_generates_unique_keys(client):
	"""Test that creating multiple URLs generates unique keys"""
	target_url_1 = "https://www.example.com/first"
	target_url_2 = "https://www.example.com/second"

	response1 = client.post("/url", json={"target_url": target_url_1})
	response2 = client.post("/url", json={"target_url": target_url_2})

	assert response1.status_code == status.HTTP_200_OK
	assert response2.status_code == status.HTTP_200_OK

	data1 = response1.json()
	data2 = response2.json()

	# Keys should be different
	url_key_1 = data1["url"].split("/")[-1]
	url_key_2 = data2["url"].split("/")[-1]
	assert url_key_1 != url_key_2

	# Secret keys should be different
	secret_key_1 = data1["admin_url"].split("/")[-1]
	secret_key_2 = data2["admin_url"].split("/")[-1]
	assert secret_key_1 != secret_key_2


def test_create_url_with_https(client):
	"""Test creating URL with HTTPS protocol"""
	target_url = "https://www.secure-example.com/path"

	response = client.post("/url", json={"target_url": target_url})

	assert response.status_code == status.HTTP_200_OK
	assert response.json()["target_url"] == target_url


def test_create_url_with_http(client):
	"""Test creating URL with HTTP protocol"""
	target_url = "http://www.example.com/path"

	response = client.post("/url", json={"target_url": target_url})

	assert response.status_code == status.HTTP_200_OK
	assert response.json()["target_url"] == target_url


def test_create_url_with_query_params(client):
	"""Test creating URL with query parameters"""
	target_url = "https://www.example.com/search?q=test&page=1"

	response = client.post("/url", json={"target_url": target_url})

	assert response.status_code == status.HTTP_200_OK
	assert response.json()["target_url"] == target_url
