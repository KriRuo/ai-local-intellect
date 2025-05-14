import pytest
from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_get_posts():
    response = client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "data" in data
    assert isinstance(data["data"], list)
    if data["data"]:
        post = data["data"][0]
        assert "id" in post
        assert "title" in post
        assert "content" in post
        assert "timestamp" in post

def test_save_and_list_and_delete_saved_post():
    # Get a post to save
    response = client.get("/api/posts")
    assert response.status_code == 200
    posts = response.json()["data"]
    if not posts:
        pytest.skip("No posts available to save.")
    post_id = posts[0]["id"]

    # Save the post
    save_resp = client.post("/api/saved", json={"post_id": post_id})
    assert save_resp.status_code == 200
    saved = save_resp.json()
    assert saved["post_id"] == post_id
    assert "saved_at" in saved
    assert "post" in saved
    # List saved posts
    list_resp = client.get("/api/saved")
    assert list_resp.status_code == 200
    saved_list = list_resp.json()
    assert any(item["post_id"] == post_id for item in saved_list)
    # Delete the saved post
    del_resp = client.delete(f"/api/saved/{post_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["detail"] == "Deleted"
    # Ensure it's gone
    list_resp2 = client.get("/api/saved")
    assert list_resp2.status_code == 200
    saved_list2 = list_resp2.json()
    assert not any(item["post_id"] == post_id for item in saved_list2) 