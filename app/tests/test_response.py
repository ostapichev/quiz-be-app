from fastapi import status
from fastapi.testclient import TestClient


def test_response(client: TestClient) -> None:
    response = client.get("/api/response")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["status_code"] == status.HTTP_200_OK
    assert data["detail"] == "ok"
    assert data["result"] == "working"

    assert isinstance(data["status_code"], int)
    assert isinstance(data["detail"], str)
    assert isinstance(data["result"], str)


def test_error_response(client: TestClient) -> None:
    response = client.get("/not-found")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert isinstance(response.status_code, int)
