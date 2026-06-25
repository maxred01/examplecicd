import pytest
from database import init_db, get_conn, get_categories, get_products, get_variants, get_variant, get_product, create_order, update_order_status, get_order
import os
import tempfile


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test_cafe.db")
    monkeypatch.setattr("database.DB_PATH", db_path)
    init_db()
    yield


def test_init_db_creates_tables():
    conn = get_conn()
    tables = [row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    conn.close()
    assert "categories" in tables
    assert "products" in tables
    assert "variants" in tables
    assert "orders" in tables


def test_seed_menu_populates_data():
    cats = get_categories()
    assert len(cats) == 5
    assert cats[0]["name"] == "Кофе"


def test_get_products():
    cats = get_categories()
    coffee_id = cats[0]["id"]
    products = get_products(coffee_id)
    assert len(products) > 0
    assert products[0]["category_id"] == coffee_id


def test_get_variants():
    cats = get_categories()
    products = get_products(cats[0]["id"])
    variants = get_variants(products[0]["id"])
    assert len(variants) > 0
    assert variants[0]["product_id"] == products[0]["id"]


def test_get_variant():
    cats = get_categories()
    products = get_products(cats[0]["id"])
    variants = get_variants(products[0]["id"])
    v = get_variant(variants[0]["id"])
    assert v is not None
    assert v["id"] == variants[0]["id"]


def test_get_product():
    cats = get_categories()
    products = get_products(cats[0]["id"])
    p = get_product(products[0]["id"])
    assert p is not None
    assert p["id"] == products[0]["id"]


def test_create_order():
    order_id = create_order(
        user_id=999,
        username="test_user",
        product_name="Капучино",
        variant_label="M (240 мл)",
        price=280,
    )
    assert order_id > 0
    order = get_order(order_id)
    assert order is not None
    assert order["user_id"] == 999
    assert order["status"] == "pending"


def test_update_order_status():
    order_id = create_order(1, "u", "Эспрессо", "S", 150)
    update_order_status(order_id, "accepted")
    order = get_order(order_id)
    assert order["status"] == "accepted"

    update_order_status(order_id, "completed")
    order = get_order(order_id)
    assert order["status"] == "completed"


def test_get_nonexistent():
    assert get_variant(99999) is None
    assert get_product(99999) is None
    assert get_order(99999) is None

