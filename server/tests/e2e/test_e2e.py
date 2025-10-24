"""
End-to-end test for URL shortener application.

This test covers the complete flow:
1. List root endpoint
2. Create a new shortened URL
3. Access the shortened URL and verify redirect
4. Check admin endpoint to verify click count
5. Access shortened URL again to increment clicks
6. Verify click count increased
7. Delete the shortened URL
8. Verify deleted URL returns 404
"""


def test_url_shortener_complete_flow(client):
    """Test the complete E2E flow of URL shortener"""

    # 1. Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.text

    # 2. Create a new shortened URL
    target_url = "https://www.example.com/very/long/url/path"
    create_response = client.post(
        "/url",
        json={"target_url": target_url}
    )
    assert create_response.status_code == 200

    data = create_response.json()
    assert data["target_url"] == target_url
    assert data["is_active"] is True
    assert data["clicks"] == 0
    assert "url" in data
    assert "admin_url" in data

    # Extract the URL key and secret key from the response
    shortened_url = data["url"]
    admin_url = data["admin_url"]
    url_key = shortened_url.split("/")[-1]
    secret_key = admin_url.split("/")[-1]

    # 3. Access the shortened URL (should redirect)
    redirect_response = client.get(f"/{url_key}", follow_redirects=False)
    assert redirect_response.status_code == 307  # Temporary redirect
    assert redirect_response.headers["location"] == target_url

    # 4. Check admin endpoint - should show 1 click
    admin_response = client.get(f"/admin/{secret_key}")
    assert admin_response.status_code == 200

    admin_data = admin_response.json()
    assert admin_data["target_url"] == target_url
    assert admin_data["clicks"] == 1
    assert admin_data["is_active"] is True

    # 5. Access shortened URL again to increment clicks
    redirect_response_2 = client.get(f"/{url_key}", follow_redirects=False)
    assert redirect_response_2.status_code == 307
    assert redirect_response_2.headers["location"] == target_url

    # 6. Verify click count increased to 2
    admin_response_2 = client.get(f"/admin/{secret_key}")
    assert admin_response_2.status_code == 200

    admin_data_2 = admin_response_2.json()
    assert admin_data_2["clicks"] == 2

    # 7. Delete the shortened URL
    delete_response = client.delete(f"/admin/{secret_key}")
    assert delete_response.status_code == 200
    assert "Successfully deleted" in delete_response.json()["detail"]

    # 8. Verify deleted URL returns 404
    not_found_response = client.get(f"/{url_key}")
    assert not_found_response.status_code == 404
    assert "doesn't exist" in not_found_response.json()["detail"]

    # Also verify admin endpoint returns 404 for deleted URL
    admin_not_found = client.get(f"/admin/{secret_key}")
    assert admin_not_found.status_code == 404


def test_invalid_url_returns_400(client):
    """Test that creating a shortened URL with invalid URL returns 400"""
    response = client.post(
        "/url",
        json={"target_url": "not-a-valid-url"}
    )
    assert response.status_code == 400
    assert "not valid" in response.json()["detail"]


def test_nonexistent_url_key_returns_404(client):
    """Test that accessing a non-existent URL key returns 404"""
    response = client.get("/nonexistent123")
    assert response.status_code == 404
    assert "doesn't exist" in response.json()["detail"]


def test_nonexistent_secret_key_returns_404(client):
    """Test that accessing admin with non-existent secret key returns 404"""
    response = client.get("/admin/nonexistent_secret_key_123")
    assert response.status_code == 404
    assert "doesn't exist" in response.json()["detail"]
