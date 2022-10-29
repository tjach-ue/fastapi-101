import pytest
from fastapi.testclient import TestClient

from src.a_helloworld.app.main import app


@pytest.fixture
def client():
    client = TestClient(app)
    return client


def test_root_endpoint_with_get(client):
    resp = client.get("/")
    assert resp.status_code == 200
    msg = "Hello World"
    expected = {"message": msg}
    assert resp.json() == expected


def test_root_custom_endpoint_with_get(client):
    name = "John"
    resp = client.get(f"/hello/{name}")
    assert resp.status_code == 200
    msg = f"Hello {name}"
    expected = {"message": msg}
    assert resp.json() == expected


def test_root_endpoint_only_get(client):
    resp = client.post("/")
    assert resp.status_code == 405
    assert resp.json() == {"detail": "Method Not Allowed"}