import pytest
from fastapi.testclient import TestClient

from app.main import app


class FakeRedis:
    pass


@pytest.fixture
def client() -> TestClient:
    app.state.redis = FakeRedis()
    return TestClient(app)
