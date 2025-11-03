import sqlite3
import re
from typing import List, Tuple, Optional

DB_NAME = "inventory.db"

# -----------------------------
# Helpers
# -----------------------------
def normalize_product_name(raw: str) -> str:
    if not raw:
        return raw
    s = raw.strip()
    m = re.search(r'(\b\d+\s*(?:pcs?|p)\b)', s, flags=re.IGNORECASE)
    unit = None
    if m:
        num = re.search(r'\d+', m.group(1)).group(0)
        unit = f"{int(num)}PCS"
        s = (s[:m.start()] + s[m.end():]).strip()
        s = re.sub(r'\s+', ' ', s).strip()
        s = re.sub(r'[-–—]+\s*$', '', s).strip()
    end_unit = re.search(r'(\b\d+\s*PCS\b)$', s, flags=re.IGNORECASE)
    if end_unit:
        num = re.search(r'\d+', end_unit.group(1)).group(0)
        base = s[:end_unit.start()].strip()
        return f"{base} {int(num)}PCS"
    return f"{s} {unit}" if unit else s


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
    return cur.fetchone() is not None


def _get_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    return [row[1] for row in cur.fetchall()]


# -----------------------------
# Schema
# -----------------------------
CREATE_PRODUCTS_SQL = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    quantity INTEGER DEFAULT 0,
    production_date TEXT,
    expiration_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_SALES_SQL = """
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity INTEGER,
    seller_name TEXT,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id)
);
"""

CREATE_INGREDIENTS_SQL = """
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER DEFAULT 0,
    unit TEXT DEFAULT "",
    expiration_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

"""


def init_db():
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute(CREATE_PRODUCTS_SQL)
        cur.execute(CREATE_SALES_SQL)
        cur.execute(CREATE_INGREDIENTS_SQL)
        conn.commit()
    finally:
        conn.close()
    print("✅ Database ready.")


# -----------------------------
# Products CRUD
# -----------------------------
def add_product(name: str, category: Optional[str], quantity: int,
                production_date: Optional[str], expiration_date: Optional[str]) -> None:
    name = normalize_product_name(name)
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO products (name, category, quantity, production_date, expiration_date)
            VALUES (?, ?, ?, ?, ?);
        """, (name, category, quantity, production_date, expiration_date))
        conn.commit()
    finally:
        conn.close()
    print(f"✅ Product '{name}' added.")


def get_products() -> List[Tuple]:
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, category, quantity, production_date, expiration_date, created_at FROM products;")
        return cur.fetchall()
    finally:
        conn.close()


def update_product(product_id: int, name: Optional[str] = None, category: Optional[str] = None,
                   quantity: Optional[int] = None, production_date: Optional[str] = None,
                   expiration_date: Optional[str] = None) -> None:
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        fields, values = [], []
        if name is not None:
            fields.append("name=?")
            values.append(normalize_product_name(name))
        if category is not None:
            fields.append("category=?")
            values.append(category)
        if quantity is not None:
            fields.append("quantity=?")
            values.append(quantity)
        if production_date is not None:
            fields.append("production_date=?")
            values.append(production_date)
        if expiration_date is not None:
            fields.append("expiration_date=?")
            values.append(expiration_date)
        if not fields:
            return
        values.append(product_id)
        cur.execute(f"UPDATE products SET {', '.join(fields)} WHERE id=?;", values)
        conn.commit()
    finally:
        conn.close()
    print(f"✅ Product ID {product_id} updated.")


def delete_product(product_id: int) -> None:
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id=?;", (product_id,))
        conn.commit()
    finally:
        conn.close()
    print(f"🗑️ Product ID {product_id} deleted.")


# -----------------------------
# Sales CRUD
# -----------------------------
def add_sale(product_id: int, quantity: int, seller_name: str, sale_date: Optional[str] = None) -> int:
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        if sale_date:
            cur.execute(
                "INSERT INTO sales (product_id, quantity, seller_name, sale_date) VALUES (?, ?, ?, ?);",
                (product_id, quantity, seller_name, sale_date)
            )
        else:
            cur.execute(
                "INSERT INTO sales (product_id, quantity, seller_name) VALUES (?, ?, ?);",
                (product_id, quantity, seller_name)
            )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def get_sales() -> List[dict]:
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, product_id, quantity, seller_name, sale_date FROM sales;")
        return [
            {"id": r[0], "product_id": r[1], "quantity": r[2], "seller": r[3], "date": r[4]}
            for r in cur.fetchall()
        ]
    finally:
        conn.close()



# -----------------------------
# Ingredients CRUD
# -----------------------------
def add_ingredient(name: str, quantity: int, unit: str = "", expiration_date: Optional[str] = None) -> None:
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ingredients (name, quantity, unit, expiration_date) VALUES (?, ?, ?, ?);",
            (name, quantity, unit, expiration_date)
        )
        conn.commit()
    finally:
        conn.close()


def get_ingredients() -> List[dict]:
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, quantity, unit, expiration_date, created_at FROM ingredients;")
        return [
            {"id": r[0], "name": r[1], "quantity": r[2], "unit": r[3] or "", "expiration_date": r[4] or ""}
            for r in cur.fetchall()
        ]
    finally:
        conn.close()



def update_ingredient(ingredient_id: int, name: Optional[str] = None, quantity: Optional[int] = None,
                      unit: Optional[str] = None, expiration_date: Optional[str] = None) -> None:
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        fields, values = [], []
        if name is not None:
            fields.append("name=?")
            values.append(name)
        if quantity is not None:
            fields.append("quantity=?")
            values.append(quantity)
        if unit is not None:
            fields.append("unit=?")
            values.append(unit)
        if expiration_date is not None:
            fields.append("expiration_date=?")
            values.append(expiration_date)
        if not fields:
            return
        values.append(ingredient_id)
        cur.execute(f"UPDATE ingredients SET {', '.join(fields)} WHERE id=?;", values)
        conn.commit()
    finally:
        conn.close()


def delete_ingredient(ingredient_id: int) -> None:
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM ingredients WHERE id=?;", (ingredient_id,))
        conn.commit()
    finally:
        conn.close()
    print(f"🗑️ Ingredient ID {ingredient_id} deleted.")


# -----------------------------
# Run migration/setup
# -----------------------------
if __name__ == "__main__":
    init_db()
    print("✅ Inventory DB initialized.")
    print(get_products())
    print(get_sales())
    print(get_ingredients())
