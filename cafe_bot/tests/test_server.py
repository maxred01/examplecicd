import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["CUSTOMER_BOT_TOKEN"] = "test:token"
os.environ["WORKER_BOT_TOKEN"] = "test:token"
os.environ["WORKER_CHAT_ID"] = "12345"
os.environ["SERVER_URL"] = "http://localhost:8000"
os.environ["SECRET_TOKEN"] = "test_secret"

from server import app
from database import init_db, get_conn


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test_cafe.db")
    monkeypatch.setattr("database.DB_PATH", db_path)
    init_db()
    yield


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_index_page(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_get_categories(client):
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 5


def test_get_products(client):
    resp = client.get("/api/products/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_variants(client):
    resp = client.get("/api/variants/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_place_order(client):
    resp = client.post("/api/order", json={
        "variant_id": 1,
        "user_id": 12345,
        "username": "test_user",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert "order_id" in data


def test_place_order_missing_fields(client):
    resp = client.post("/api/order", json={})
    assert resp.status_code == 400


def test_place_order_invalid_variant(client):
    resp = client.post("/api/order", json={
        "variant_id": 99999,
        "user_id": 123,
    })
    assert resp.status_code == 404


def test_css_route(client):
    resp = client.get("/style.css")
    assert resp.status_code == 200


def test_js_route(client):
    resp = client.get("/app.js")
    assert resp.status_code == 200
