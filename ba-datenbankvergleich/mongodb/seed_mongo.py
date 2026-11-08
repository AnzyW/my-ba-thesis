"""
MongoDB CSV Seed Script V2
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript lädt die gemeinsame synthetische Datengrundlage aus dem Ordner
data/ in MongoDB. Dadurch verwenden PostgreSQL und MongoDB dieselben
fachlichen Testdaten.

Voraussetzung:
Vorher muss scripts/generate_dataset.py ausgeführt worden sein.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from pymongo import MongoClient


# ============================================================
# Konfiguration
# ============================================================

MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0&directConnection=true"
DATABASE_NAME = "ecommerce"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


# ============================================================
# CSV-Hilfsfunktionen
# ============================================================

def read_csv(filename: str) -> list[dict[str, str]]:
    """
    Liest eine CSV-Datei aus dem data/-Ordner.
    """
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"CSV-Datei nicht gefunden: {path}")

    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def parse_timestamp(value: str) -> datetime:
    """
    Wandelt einen ISO-Zeitstempel aus der CSV-Datei in ein datetime-Objekt um.
    Beispiel: 2026-01-01T00:00:00Z
    """
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def to_bool(value: str) -> bool:
    """
    Wandelt CSV-Boolean-Werte in Python-Boolean-Werte um.
    """
    return value.lower() == "true"


# ============================================================
# MongoDB-Operationen
# ============================================================

def reset_collections(db) -> None:
    """
    Leert alle relevanten Collections.
    Die Collections selbst bleiben erhalten.
    """
    db.categories.delete_many({})
    db.products.delete_many({})
    db.customers.delete_many({})
    db.carts.delete_many({})
    db.orders.delete_many({})


def ensure_indexes(db) -> None:
    """
    Legt die für das Lastprofil relevanten Indexe an.
    Dadurch bleibt das Seed-Skript robust, auch wenn init_mongo.js vorher
    nicht erneut ausgeführt wurde.
    """
    db.categories.create_index(
        [("name", 1)],
        name="idx_categories_name"
    )

    db.products.create_index(
        [("sku", 1)],
        unique=True,
        name="idx_products_sku_unique"
    )

    db.products.create_index(
        [("category_id", 1), ("price", 1)],
        name="idx_products_category_price"
    )

    db.products.create_index(
        [("active", 1), ("category_id", 1)],
        name="idx_products_active_category"
    )

    db.customers.create_index(
        [("email", 1)],
        unique=True,
        name="idx_customers_email_unique"
    )

    db.carts.create_index(
        [("customer_id", 1), ("status", 1)],
        name="idx_carts_customer_status"
    )

    db.carts.create_index(
        [("items.product_id", 1)],
        name="idx_carts_items_product"
    )

    db.orders.create_index(
        [("customer_id", 1), ("created_at", -1)],
        name="idx_orders_customer_created"
    )

    db.orders.create_index(
        [("items.product_id", 1)],
        name="idx_orders_items_product"
    )


# ============================================================
# Ladelogik
# ============================================================

def load_categories(db) -> None:
    rows = read_csv("categories.csv")

    documents = [
        {
            "_id": int(row["category_id"]),
            "name": row["name"],
            "created_at": parse_timestamp(row["created_at"]),
        }
        for row in rows
    ]

    if documents:
        db.categories.insert_many(documents)


def load_products(db) -> None:
    product_rows = read_csv("products.csv")
    inventory_rows = read_csv("inventory.csv")

    inventory_by_product_id = {
        int(row["product_id"]): {
            "stock": int(row["stock"]),
            "updated_at": parse_timestamp(row["updated_at"]),
        }
        for row in inventory_rows
    }

    documents = []

    for row in product_rows:
        product_id = int(row["product_id"])

        documents.append(
            {
                "_id": product_id,
                "sku": row["sku"],
                "name": row["name"],
                "category_id": int(row["category_id"]),
                "brand": row["brand"],
                "price": float(row["price"]),
                "active": to_bool(row["active"]),
                "inventory": inventory_by_product_id[product_id],
                "created_at": parse_timestamp(row["created_at"]),
            }
        )

    if documents:
        db.products.insert_many(documents)


def load_customers(db) -> None:
    rows = read_csv("customers.csv")

    documents = [
        {
            "_id": int(row["customer_id"]),
            "email": row["email"],
            "created_at": parse_timestamp(row["created_at"]),
        }
        for row in rows
    ]

    if documents:
        db.customers.insert_many(documents)


def load_carts(db) -> None:
    cart_rows = read_csv("carts.csv")
    cart_item_rows = read_csv("cart_items.csv")

    items_by_cart_id: dict[int, list[dict]] = defaultdict(list)

    for row in cart_item_rows:
        cart_id = int(row["cart_id"])

        items_by_cart_id[cart_id].append(
            {
                "product_id": int(row["product_id"]),
                "quantity": int(row["quantity"]),
                "unit_price": float(row["unit_price"]),
                "updated_at": parse_timestamp(row["updated_at"]),
            }
        )

    documents = []

    for row in cart_rows:
        cart_id = int(row["cart_id"])

        documents.append(
            {
                "_id": cart_id,
                "customer_id": int(row["customer_id"]),
                "status": row["status"],
                "created_at": parse_timestamp(row["created_at"]),
                "updated_at": parse_timestamp(row["updated_at"]),
                "items": items_by_cart_id[cart_id],
            }
        )

    if documents:
        db.carts.insert_many(documents)


def load_orders(db) -> None:
    order_rows = read_csv("orders.csv")
    order_item_rows = read_csv("order_items.csv")

    if not order_rows:
        return

    items_by_order_id: dict[int, list[dict]] = defaultdict(list)

    for row in order_item_rows:
        order_id = int(row["order_id"])

        items_by_order_id[order_id].append(
            {
                "product_id": int(row["product_id"]),
                "quantity": int(row["quantity"]),
                "unit_price": float(row["unit_price"]),
            }
        )

    documents = []

    for row in order_rows:
        order_id = int(row["order_id"])

        documents.append(
            {
                "_id": order_id,
                "customer_id": int(row["customer_id"]),
                "cart_id": int(row["cart_id"]),
                "created_at": parse_timestamp(row["created_at"]),
                "total_amount": float(row["total_amount"]),
                "status": row["status"],
                "items": items_by_order_id[order_id],
            }
        )

    if documents:
        db.orders.insert_many(documents)


# ============================================================
# Prüfung
# ============================================================

def print_counts(db) -> None:
    collections = [
        "categories",
        "products",
        "customers",
        "carts",
        "orders",
    ]

    print("\nDatensatzübersicht MongoDB:")

    for collection_name in collections:
        count = db[collection_name].count_documents({})
        print(f"- {collection_name}: {count}")

    cart_item_count = sum(
        len(cart.get("items", []))
        for cart in db.carts.find({}, {"items": 1})
    )

    order_item_count = sum(
        len(order.get("items", []))
        for order in db.orders.find({}, {"items": 1})
    )

    print(f"- cart_items eingebettet: {cart_item_count}")
    print(f"- order_items eingebettet: {order_item_count}")


# ============================================================
# Hauptprogramm
# ============================================================

def main() -> None:
    print("Verbinde mit MongoDB...")
    print(f"Lade CSV-Daten aus: {DATA_DIR}")

    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    print("Prüfe MongoDB-Verbindung...")
    client.admin.command("ping")

    print("Leere bestehende Collections...")
    reset_collections(db)

    print("Stelle Indexe sicher...")
    ensure_indexes(db)

    print("Lade Kategorien...")
    load_categories(db)

    print("Lade Produkte mit eingebettetem Bestand...")
    load_products(db)

    print("Lade Kunden...")
    load_customers(db)

    print("Lade Warenkörbe mit eingebetteten Positionen...")
    load_carts(db)

    print("Lade initiale Bestellungen...")
    load_orders(db)

    print_counts(db)

    client.close()

    print("\nMongoDB CSV Seed erfolgreich abgeschlossen.")


if __name__ == "__main__":
    main()