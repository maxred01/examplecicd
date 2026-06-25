import sqlite3
import time

DB_PATH = "cafe.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            emoji TEXT NOT NULL,
            position INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            image_url TEXT DEFAULT '',
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            label TEXT NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT DEFAULT '',
            product_name TEXT NOT NULL,
            variant_label TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at REAL NOT NULL
        )
    """)

    if c.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
        seed_menu(c)

    conn.commit()
    conn.close()


def seed_menu(c):
    categories = [
        ("Кофе", "☕", 0),
        ("Выпечка", "🥐", 1),
        ("Чай", "🍵", 2),
        ("Десерты", "🍰", 3),
        ("Холодные напитки", "🧊", 4),
    ]
    c.executemany("INSERT INTO categories (name, emoji, position) VALUES (?, ?, ?)", categories)

    coffee_id = c.execute("SELECT id FROM categories WHERE name='Кофе'").fetchone()[0]
    pastries_id = c.execute("SELECT id FROM categories WHERE name='Выпечка'").fetchone()[0]
    tea_id = c.execute("SELECT id FROM categories WHERE name='Чай'").fetchone()[0]
    desserts_id = c.execute("SELECT id FROM categories WHERE name='Десерты'").fetchone()[0]
    cold_id = c.execute("SELECT id FROM categories WHERE name='Холодные напитки'").fetchone()[0]

    products = [
        (coffee_id, "Эспрессо", "Классический итальянский эспрессо"),
        (coffee_id, "Капучино", "Эспрессо с молочной пенкой"),
        (coffee_id, "Латте", "Нежный кофе с большим количеством молока"),
        (coffee_id, "Раф-кофе", "Сливочный раф с ванилью"),
        (coffee_id, "Флэт уайт", "Двойной эспрессо с микропенкой"),
        (coffee_id, "Американо", "Эспрессо, разбавленный горячей водой"),
        (pastries_id, "Круассан", "Свежий масляный круассан"),
        (pastries_id, "Багет", "Хрустящий французский багет"),
        (pastries_id, "Чизкейк", "Нежный чизкейк Нью-Йорк"),
        (pastries_id, "Маффин", "Шоколадный маффин"),
        (pastries_id, "Сэндвич", "Сэндвич с курицей и авокадо"),
        (tea_id, "Чёрный чай", "Ароматный чёрный чай Цейлон"),
        (tea_id, "Зелёный чай", "Японский зелёный чай Сенча"),
        (tea_id, "Травяной чай", "Мятный травяной микс"),
        (tea_id, "Матча", "Японский чай матча латте"),
        (desserts_id, "Тирамису", "Классический итальянский тирамису"),
        (desserts_id, "Панна-котта", "Ванильная панна-котта с ягодами"),
        (desserts_id, "Медовик", "Домашний медовый торт"),
        (cold_id, "Лимонад", "Домашний лимонад с мятой"),
        (cold_id, "Айс-латте", "Холодный латте со льдом"),
        (cold_id, "Смузи", "Ягодный смузи"),
        (cold_id, "Мilk-шейк", "Шоколадный молочный коктейль"),
    ]
    c.executemany("INSERT INTO products (category_id, name, description) VALUES (?, ?, ?)", products)

    variants_map = {
        "Эспрессо": [("S (30 мл)", 150), ("D (60 мл)", 220)],
        "Капучино": [("S (180 мл)", 220), ("M (240 мл)", 280), ("L (360 мл)", 340)],
        "Латте": [("S (180 мл)", 240), ("M (240 мл)", 300), ("L (360 мл)", 360)],
        "Раф-кофе": [("S (180 мл)", 300), ("M (240 мл)", 360)],
        "Флэт уайт": [("M (160 мл)", 280)],
        "Американо": [("S (200 мл)", 180), ("M (300 мл)", 240), ("L (400 мл)", 300)],
        "Круассан": [("1 шт", 180)],
        "Багет": [("1 шт", 120)],
        "Чизкейк": [("1 кусок", 350)],
        "Маффин": [("1 шт", 200)],
        "Сэндвич": [("1 шт", 280)],
        "Чёрный чай": [("S (200 мл)", 160), ("M (300 мл)", 220)],
        "Зелёный чай": [("S (200 мл)", 180), ("M (300 мл)", 240)],
        "Травяной чай": [("S (200 мл)", 180), ("M (300 мл)", 240)],
        "Матча": [("S (200 мл)", 260), ("M (300 мл)", 320)],
        "Тирамису": [("1 кусок", 380)],
        "Панна-котта": [("1 порция", 340)],
        "Медовик": [("1 кусок", 320)],
        "Лимонад": [("S (300 мл)", 240), ("M (500 мл)", 320)],
        "Айс-латте": [("M (350 мл)", 300), ("L (500 мл)", 380)],
        "Смузи": [("M (300 мл)", 280)],
        "Milk-шейк": [("M (350 мл)", 320), ("L (500 мл)", 400)],
    }

    for product_name, variants in variants_map.items():
        product = c.execute("SELECT id FROM products WHERE name=?", (product_name,)).fetchone()
        if product:
            for label, price in variants:
                c.execute("INSERT INTO variants (product_id, label, price) VALUES (?, ?, ?)",
                          (product[0], label, price))


def get_categories():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM categories ORDER BY position").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_products(category_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM products WHERE category_id=?", (category_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_variants(product_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM variants WHERE product_id=?", (product_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_variant(variant_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM variants WHERE id=?", (variant_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_product(product_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_order(user_id, username, product_name, variant_label, price):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (user_id, username, product_name, variant_label, price, status, created_at) "
        "VALUES (?, ?, ?, ?, ?, 'pending', ?)",
        (user_id, username, product_name, variant_label, price, time.time()),
    )
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id


def update_order_status(order_id, status):
    conn = get_conn()
    conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()


def get_order(order_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
