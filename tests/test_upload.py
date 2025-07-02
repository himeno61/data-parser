import io
import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_upload_success(client):
    data = {
        "file": (io.BytesIO(b"test data"), "test.txt")
    }
    response = client.post("/upload", content_type="multipart/form-data", data=data)
    assert response.status_code == 202
    assert "is being processed" in response.get_json()["status"]

def test_upload_missing_file(client):
    response = client.post("/upload", content_type="multipart/form-data", data={})
    assert response.status_code == 400
