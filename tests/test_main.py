from fastapi.testclient import TestClient

from thunderstore_query_service.main import app

client = TestClient(app)


def test_example():
    """Test the main entry point."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
