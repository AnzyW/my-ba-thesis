"""
MongoDB Seed Script V1
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript erzeugt einen kleinen, reproduzierbaren Testdatensatz
für MongoDB. Es dient zunächst zur technischen Prüfung der Datenbankverbindung,
der Collections, der Indexe und der dokumentenorientierten Datenstruktur.

Der Datensatz entspricht fachlich dem PostgreSQL-Testdatensatz:
- Kategorien
- Produkte mit eingebettetem Bestand
- Kunden
- aktive Warenkörbe mit eingebetteten Warenkorbpositionen
- noch keine initialen Bestellungen
"""

from decimal import Decimal
from datetime import datetime, timezone
import random
from pymongo import MongoClient


# ============================================================
# Konfiguration
# ============================================================

MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0&directConnection=true"
DATABASE_NAME = "ecommerce"

RANDOM_SEED = 42

CATEGORY_COUNT = 5
PRODUCT_COUNT = 1_000
CUSTOMER_COUNT = 100
CART_COUNT = 100

MIN_STOCK = 50
MAX_STOCK = 500

MIN_CART_ITEMS = 1
MAX_CART_ITEMS = 3


# ============================================================
# Hilfsfunktionen
# ============================================================

def now_utc():
    """
    Gibt einen UTC-Zeitstempel zurück.
    MongoDB speichert Python datetime-Werte als BSON Date.
    """
    return datetime.now(timezone.utc)


def reset_collections(db):
    """
    Leert alle relevanten Collections.
    Die Collections werden bewusst nicht gelöscht, damit vorhandene Indexe
    aus dem init_mongo.js-Skript erhalten bleiben können.
    """
    db.categories.delete_many({})
    db.products.delete_many({})
    db.customers.delete_many({})
    db.carts.delete_many({})
    db.orders.delete_many({})


def ensure_indexes(db):
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


def insert_categories(db):
    timestamp = now_utc()

    categories = [
        {
            "_id": category_id,
            "name": f"Category {category_id}",
            "created_at": timestamp
        }
        for category_id in range(1, CATEGORY_COUNT + 1)
    ]

    db.categories.insert_many(categories)


def generate_products():
    timestamp = now_utc()
    products = []
    product_prices = {}

    for product_id in range(1, PRODUCT_COUNT + 1):
        sku = f"SKU-{product_id:06d}"
        name = f"Product {product_id}"
        category_id = random.randint(1, CATEGORY_COUNT)
        brand = f"Brand {random.randint(1, 20)}"

        price_decimal = Decimal(random.randint(500, 50_000)) / Decimal("100")
        price = float(price_decimal)

        active = True
        stock = random.randint(MIN_STOCK, MAX_STOCK)

        products.append(
            {
                "_id": product_id,
                "sku": sku,
                "name": name,
                "category_id": category_id,
                "brand": brand,
                "price": price,
                "active": active,
                "inventory": {
                    "stock": stock,
                    "updated_at": timestamp
                },
                "created_at": timestamp
            }
        )

        product_prices[product_id] = price

    return products, product_prices


def insert_products(db):
    products, product_prices = generate_products()
    db.products.insert_many(products)
    return product_prices


def insert_customers(db):
    timestamp = now_utc()

    customers = [
        {
            "_id": customer_id,
            "email": f"customer{customer_id}@example.com",
            "created_at": timestamp
        }
        for customer_id in range(1, CUSTOMER_COUNT + 1)
    ]

    db.customers.insert_many(customers)


def insert_carts(db, product_prices):
    timestamp = now_utc()
    carts = []

    for cart_id in range(1, CART_COUNT + 1):
        customer_id = cart_id
        item_count = random.randint(MIN_CART_ITEMS, MAX_CART_ITEMS)
        product_ids = random.sample(range(1, PRODUCT_COUNT + 1), item_count)

        items = []

        for product_id in product_ids:
            quantity = random.randint(1, 3)
            unit_price = product_prices[product_id]

            items.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "updated_at": timestamp
                }
            )

        carts.append(
            {
                "_id": cart_id,
                "customer_id": customer_id,
                "status": "active",
                "created_at": timestamp,
                "updated_at": timestamp,
                "items": items
            }
        )

    db.carts.insert_many(carts)


def print_counts(db):
    collections = [
        "categories",
        "products",
        "customers",
        "carts",
        "orders",
    ]

    print("\nDatensatzübersicht:")

    for collection_name in collections:
        count = db[collection_name].count_documents({})
        print(f"- {collection_name}: {count}")

    cart_item_count = sum(
        len(cart.get("items", []))
        for cart in db.carts.find({}, {"items": 1})
    )

    print(f"- cart_items eingebettet: {cart_item_count}")


# ============================================================
# Hauptprogramm
# ============================================================

def main():
    random.seed(RANDOM_SEED)

    print("Verbinde mit MongoDB...")

    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    print("Prüfe MongoDB-Verbindung...")
    client.admin.command("ping")

    print("Leere bestehende Collections...")
    reset_collections(db)

    print("Stelle Indexe sicher...")
    ensure_indexes(db)

    print("Füge Kategorien ein...")
    insert_categories(db)

    print("Füge Produkte mit eingebettetem Bestand ein...")
    product_prices = insert_products(db)

    print("Füge Kunden ein...")
    insert_customers(db)

    print("Füge Warenkörbe mit eingebetteten Positionen ein...")
    insert_carts(db, product_prices)

    print_counts(db)

    client.close()

    print("\nMongoDB Seed erfolgreich abgeschlossen.")


if __name__ == "__main__":
    main()