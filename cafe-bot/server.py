import os
import hashlib
import hmac
import time
import threading
import requests
from flask import Flask, request, jsonify, send_from_directory
from database import (
    init_db, get_categories, get_products, get_variants,
    get_variant, get_product, create_order
)
from config import CUSTOMER_BOT_TOKEN, WORKER_BOT_TOKEN, WORKER_CHAT_ID

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MINIAPP_DIR = os.path.join(BASE_DIR, "static", "miniapp")

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(MINIAPP_DIR, "index.html")


@app.route("/style.css")
def css():
    return send_from_directory(MINIAPP_DIR, "style.css")


@app.route("/app.js")
def js():
    return send_from_directory(MINIAPP_DIR, "app.js")


@app.route("/api/categories")
def api_categories():
    return jsonify(get_categories())


@app.route("/api/products/<int:category_id>")
def api_products(category_id):
    return jsonify(get_products(category_id))


@app.route("/api/variants/<int:product_id>")
def api_variants(product_id):
    return jsonify(get_variants(product_id))


@app.route("/api/order", methods=["POST"])
def api_order():
    data = request.json
    if not data:
        return jsonify({"ok": False, "error": "No JSON body"}), 400

    variant_id = data.get("variant_id")
    user_id = data.get("user_id")
    username = data.get("username", "")

    if not variant_id or not user_id:
        return jsonify({"ok": False, "error": "Missing variant_id or user_id"}), 400

    variant = get_variant(variant_id)
    if not variant:
        return jsonify({"ok": False, "error": "Variant not found"}), 404

    product = get_product(variant["product_id"])
    if not product:
        return jsonify({"ok": False, "error": "Product not found"}), 404

    order_id = create_order(
        user_id=user_id,
        username=username,
        product_name=product["name"],
        variant_label=variant["label"],
        price=variant["price"],
    )

    threading.Thread(
        target=notify_worker,
        args=(order_id, user_id, username, product["name"], variant["label"], variant["price"]),
        daemon=True,
    ).start()

    return jsonify({
        "ok": True,
        "order_id": order_id,
        "product": product["name"],
        "variant": variant["label"],
        "price": variant["price"],
    })


def notify_worker(order_id, user_id, username, product_name, variant_label, price):
    text = (
        f"📦 *Новый заказ #{order_id}*\n\n"
        f"👤 {username or 'Гость'}\n"
        f"☕ {product_name}\n"
        f"📏 {variant_label}\n"
        f"💰 {price} ₽\n"
    )
    kb = {
        "inline_keyboard": [
            [
                {"text": "✅ Принять", "callback_data": f"accept_{order_id}"},
                {"text": "❌ Отказать", "callback_data": f"decline_{order_id}"},
            ]
        ]
    }
    try:
        url = f"https://api.telegram.org/bot{WORKER_BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": WORKER_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
            "reply_markup": kb,
        }, timeout=10)
    except Exception as e:
        print(f"[WARN] Не удалось уведомить работника: {e}")


def send_message(chat_id, text, parse_mode="Markdown"):
    try:
        url = f"https://api.telegram.org/bot{WORKER_BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }, timeout=10)
    except Exception as e:
        print(f"[WARN] send_message to {chat_id}: {e}")


if __name__ == "__main__":
    init_db()
    print("🌐 Сервер: http://0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)
