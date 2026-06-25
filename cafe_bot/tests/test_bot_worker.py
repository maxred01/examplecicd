import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["CUSTOMER_BOT_TOKEN"] = "test:token"
os.environ["WORKER_BOT_TOKEN"] = "test:token"
os.environ["WORKER_CHAT_ID"] = "12345"
os.environ["SERVER_URL"] = "http://localhost:8000"
os.environ["SECRET_TOKEN"] = "test_secret"

from cafe_bot.bot_worker import format_order


def test_format_order_default_header():
    order = {
        "id": 1,
        "username": "alice",
        "product_name": "Капучино",
        "variant_label": "M (240 мл)",
        "price": 280,
    }
    result = format_order(order)
    assert "📦 *Новый заказ*" in result
    assert "#1" in result
    assert "alice" in result
    assert "Капучино" in result
    assert "M (240 мл)" in result
    assert "280" in result


def test_format_order_custom_header():
    order = {
        "id": 42,
        "username": "",
        "product_name": "Латте",
        "variant_label": "L (360 мл)",
        "price": 360,
    }
    result = format_order(order, header="✅ *Принят*")
    assert "✅ *Принят*" in result
    assert "#42" in result
    assert "Гость" in result
    assert "Латте" in result
    assert "360" in result


def test_format_order_empty_username_shows_guest():
    order = {
        "id": 5,
        "username": "",
        "product_name": "Эспрессо",
        "variant_label": "S (30 мл)",
        "price": 150,
    }
    result = format_order(order)
    assert "Гость" in result
