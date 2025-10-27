"""
Unit tests for DELETE /admin/{secret_key} endpoint
"""

from fastapi import status


def test_delete_url_success(client):
	"""Test that DELETE /admin/{secret_key} executes successfully"""
	target_url = "https://www.example.com/to-delete"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Delete URL
	response = client.delete(f"/admin/{secret_key}")

	assert response.status_code == status.HTTP_200_OK
	assert "detail" in response.json()
	assert "Successfully deleted" in response.json()["detail"]


def test_delete_url_returns_success_message(client):
	"""Test that delete returns a success message with target URL"""
	target_url = "https://www.example.com/delete-message-test"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Delete URL
	response = client.delete(f"/admin/{secret_key}")

	assert response.status_code == status.HTTP_200_OK
	detail_message = response.json()["detail"]
	assert target_url in detail_message
	assert "Successfully deleted" in detail_message


def test_delete_nonexistent_url_returns_404(client):
	"""Test that deleting non-existent URL returns 404"""
	response = client.delete("/admin/nonexistent_secret_key_xyz")

	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert "doesn't exist" in response.json()["detail"]


def test_delete_url_makes_it_inaccessible(client):
	"""Test that deleted URL becomes inaccessible via redirect endpoint"""
	target_url = "https://www.example.com/check-inaccessible"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	url_key = data["url"].split("/")[-1]
	secret_key = data["admin_url"].split("/")[-1]

	# Verify URL works before deletion
	redirect_response = client.get(f"/{url_key}", follow_redirects=False)
	assert redirect_response.status_code == status.HTTP_307_TEMPORARY_REDIRECT

	# Delete URL
	delete_response = client.delete(f"/admin/{secret_key}")
	assert delete_response.status_code == status.HTTP_200_OK

	# Verify URL no longer works
	response = client.get(f"/{url_key}")
	assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_url_makes_admin_inaccessible(client):
	"""Test that deleted URL's admin endpoint becomes inaccessible"""
	target_url = "https://www.example.com/admin-inaccessible"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Verify admin works before deletion
	admin_response = client.get(f"/admin/{secret_key}")
	assert admin_response.status_code == status.HTTP_200_OK

	# Delete URL
	delete_response = client.delete(f"/admin/{secret_key}")
	assert delete_response.status_code == status.HTTP_200_OK

	# Verify admin no longer works
	response = client.get(f"/admin/{secret_key}")
	assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_already_deleted_url_returns_404(client):
	"""Test that deleting an already deleted URL returns 404"""
	target_url = "https://www.example.com/double-delete"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	secret_key = data["admin_url"].split("/")[-1]

	# Delete URL first time
	first_delete = client.delete(f"/admin/{secret_key}")
	assert first_delete.status_code == status.HTTP_200_OK

	# Try to delete again
	second_delete = client.delete(f"/admin/{secret_key}")
	assert second_delete.status_code == status.HTTP_404_NOT_FOUND


def test_delete_preserves_click_history(client):
	"""Test that deletion happens after clicks are recorded (implicit test)"""
	target_url = "https://www.example.com/clicks-before-delete"

	# Create shortened URL
	create_response = client.post("/url", json={"target_url": target_url})
	data = create_response.json()
	url_key = data["url"].split("/")[-1]
	secret_key = data["admin_url"].split("/")[-1]

	# Access URL to generate clicks
	client.get(f"/{url_key}", follow_redirects=False)
	client.get(f"/{url_key}", follow_redirects=False)

	# Verify clicks before deletion
	admin_response = client.get(f"/admin/{secret_key}")
	assert admin_response.json()["clicks"] == 2

	# Delete URL should succeed
	delete_response = client.delete(f"/admin/{secret_key}")
	assert delete_response.status_code == status.HTTP_200_OK
