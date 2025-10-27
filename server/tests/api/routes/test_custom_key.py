"""
Unit tests for custom URL key feature
"""

from fastapi import status


def test_create_url_with_custom_key(client):
	"""Test creating URL with a valid custom key"""
	target_url = "https://www.example.com/custom-test"
	custom_key = "my-custom-link"

	response = client.post(
		"/url", json={"target_url": target_url, "custom_key": custom_key}
	)

	assert response.status_code == status.HTTP_201_CREATED

	data = response.json()
	assert data["target_url"] == target_url
	assert custom_key in data["url"]
	assert data["is_active"] is True
	assert data["clicks"] == 0


def test_create_url_with_custom_key_already_exists(client):
	"""Test that creating URL with duplicate custom key returns 409"""
	target_url = "https://www.example.com/duplicate"
	custom_key = "duplicate-key"

	# Create first URL with custom key
	first_response = client.post(
		"/url", json={"target_url": target_url, "custom_key": custom_key}
	)
	assert first_response.status_code == status.HTTP_201_CREATED

	# Try to create second URL with same custom key
	second_response = client.post(
		"/url",
		json={
			"target_url": "https://www.example.com/another",
			"custom_key": custom_key,
		},
	)

	assert second_response.status_code == status.HTTP_409_CONFLICT
	assert "already in use" in second_response.json()["detail"]
	assert custom_key in second_response.json()["detail"]


def test_create_url_without_custom_key(client):
	"""Test that creating URL without custom key still works (random)"""
	target_url = "https://www.example.com/random"

	response = client.post("/url", json={"target_url": target_url})

	assert response.status_code == status.HTTP_201_CREATED
	data = response.json()
	assert data["target_url"] == target_url
	# Random key should be 5 characters
	url_key = data["url"].split("/")[-1]
	assert len(url_key) == 5


def test_custom_key_too_short(client):
	"""Test that custom key shorter than 3 chars returns 422"""
	target_url = "https://www.example.com/short"
	custom_key = "ab"  # Only 2 characters

	response = client.post(
		"/url", json={"target_url": target_url, "custom_key": custom_key}
	)

	assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_custom_key_too_long(client):
	"""Test that custom key longer than 50 chars returns 422"""
	target_url = "https://www.example.com/long"
	custom_key = "a" * 51  # 51 characters

	response = client.post(
		"/url", json={"target_url": target_url, "custom_key": custom_key}
	)

	assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_custom_key_invalid_characters(client):
	"""Test that custom key with invalid characters returns 422"""
	target_url = "https://www.example.com/invalid"

	invalid_keys = [
		"my link",  # Space
		"my@link",  # @
		"my#link",  # #
		"my.link",  # Dot
		"my/link",  # Slash
		"my\\link",  # Backslash
	]

	for custom_key in invalid_keys:
		response = client.post(
			"/url",
			json={"target_url": target_url, "custom_key": custom_key},
		)
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_custom_key_valid_characters(client):
	"""Test that custom key with valid characters works"""
	target_url = "https://www.example.com/valid"

	valid_keys = [
		"my-link",  # Hyphen
		"my_link",  # Underscore
		"MyLink123",  # Mixed case and numbers
		"link123",  # Numbers
		"UPPERCASE",  # Uppercase
	]

	for custom_key in valid_keys:
		response = client.post(
			"/url",
			json={"target_url": target_url, "custom_key": custom_key},
		)
		assert response.status_code == status.HTTP_201_CREATED


def test_custom_key_reserved_word(client):
	"""Test that reserved words cannot be used as custom keys"""
	target_url = "https://www.example.com/reserved"

	reserved_words = [
		"admin",
		"api",
		"url",
		"static",
		"docs",
		"redoc",
		"openapi",
		"Admin",  # Case insensitive
		"API",  # Case insensitive
	]

	for custom_key in reserved_words:
		response = client.post(
			"/url",
			json={"target_url": target_url, "custom_key": custom_key},
		)
		assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
		assert "reserved" in response.json()["detail"][0]["msg"].lower()


def test_custom_key_redirect_works(client):
	"""Test that redirect works with custom key"""
	target_url = "https://www.example.com/redirect-test"
	custom_key = "test-redirect"

	# Create URL with custom key
	create_response = client.post(
		"/url", json={"target_url": target_url, "custom_key": custom_key}
	)
	assert create_response.status_code == status.HTTP_201_CREATED

	# Test redirect
	redirect_response = client.get(f"/{custom_key}", follow_redirects=False)
	assert redirect_response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
	assert redirect_response.headers["location"] == target_url


def test_custom_key_admin_endpoint_works(client):
	"""Test that admin endpoint works with custom key"""
	target_url = "https://www.example.com/admin-test"
	custom_key = "test-admin"

	# Create URL with custom key
	create_response = client.post(
		"/url", json={"target_url": target_url, "custom_key": custom_key}
	)
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Test admin endpoint
	admin_response = client.get(f"/admin/{secret_key}")
	assert admin_response.status_code == status.HTTP_200_OK
	assert admin_response.json()["target_url"] == target_url


def test_custom_key_delete_works(client):
	"""Test that delete works with custom key"""
	target_url = "https://www.example.com/delete-test"
	custom_key = "test-delete"

	# Create URL with custom key
	create_response = client.post(
		"/url", json={"target_url": target_url, "custom_key": custom_key}
	)
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Delete URL
	delete_response = client.delete(f"/admin/{secret_key}")
	assert delete_response.status_code == status.HTTP_200_OK

	# Verify custom key is no longer accessible
	redirect_response = client.get(f"/{custom_key}")
	assert redirect_response.status_code == status.HTTP_404_NOT_FOUND


def test_custom_key_case_sensitive(client):
	"""Test that custom keys are case-sensitive"""
	target_url = "https://www.example.com/case-test"

	# Create with lowercase
	response1 = client.post(
		"/url", json={"target_url": target_url, "custom_key": "MyLink"}
	)
	assert response1.status_code == status.HTTP_201_CREATED

	# Create with different case should work (different keys)
	response2 = client.post(
		"/url", json={"target_url": target_url, "custom_key": "mylink"}
	)
	assert response2.status_code == status.HTTP_201_CREATED


def test_custom_key_cannot_be_reused_after_soft_deletion(client):
	"""Test that custom key cannot be reused after soft deletion"""
	target_url = "https://www.example.com/reuse-test"
	custom_key = "reusable-key"

	# Create URL with custom key
	create_response = client.post(
		"/url", json={"target_url": target_url, "custom_key": custom_key}
	)
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Delete URL (soft delete - marks as inactive)
	delete_response = client.delete(f"/admin/{secret_key}")
	assert delete_response.status_code == status.HTTP_200_OK

	# Try to reuse the same custom key - should fail (key still exists)
	reuse_response = client.post(
		"/url",
		json={
			"target_url": "https://www.example.com/new",
			"custom_key": custom_key,
		},
	)
	assert reuse_response.status_code == status.HTTP_409_CONFLICT
	assert "already in use" in reuse_response.json()["detail"]


def test_create_url_with_explicit_none_custom_key(client):
	"""Test creating URL with explicitly None custom_key"""
	target_url = "https://www.example.com/explicit-none"

	response = client.post(
		"/url", json={"target_url": target_url, "custom_key": None}
	)

	assert response.status_code == status.HTTP_201_CREATED
	data = response.json()
	assert data["target_url"] == target_url
	# Should generate random key when None is provided
	url_key = data["url"].split("/")[-1]
	assert len(url_key) == 5
