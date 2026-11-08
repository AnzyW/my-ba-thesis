"""
PostgreSQL Seed Script V1
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript erzeugt einen kleinen, reproduzierbaren Testdatensatz
für PostgreSQL. Es dient zunächst nur zur technischen Prüfung des
Schemas und der Datenbankverbindung.

Später kann derselbe Ansatz auf den vollständigen Datensatz skaliert werden.
"""

from decimal import Decimal
import random
import psycopg


# ============================================================
# Konfiguration
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "ecommerce",
    "user": "ba_user",
    "password": "ba_password",
}

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

def reset_database(cur):
    """
    Leert alle Tabellen und setzt die automatisch erzeugten IDs zurück.
    Die Reihenfolge ist wichtig, da Tabellen über Fremdschlüssel verbunden sind.
    """
    cur.execute("""
        TRUNCATE TABLE
            order_items,
            orders,
            cart_items,
            carts,
            inventory,
            products,
            customers,
            categories
        RESTART IDENTITY CASCADE;
    """)


def insert_categories(cur):
    categories = [
        (category_id, f"Category {category_id}")
        for category_id in range(1, CATEGORY_COUNT + 1)
    ]

    cur.executemany(
        """
        INSERT INTO categories (category_id, name)
        VALUES (%s, %s);
        """,
        categories,
    )


def generate_products():
    products = []
    inventory = []
    product_prices = {}

    for product_id in range(1, PRODUCT_COUNT + 1):
        sku = f"SKU-{product_id:06d}"
        name = f"Product {product_id}"
        category_id = random.randint(1, CATEGORY_COUNT)
        brand = f"Brand {random.randint(1, 20)}"

        price = Decimal(random.randint(500, 50_000)) / Decimal("100")
        active = True

        stock = random.randint(MIN_STOCK, MAX_STOCK)

        products.append(
            (
                product_id,
                sku,
                name,
                category_id,
                brand,
                price,
                active,
            )
        )

        inventory.append(
            (
                product_id,
                stock,
            )
        )

        product_prices[product_id] = price

    return products, inventory, product_prices


def insert_products_and_inventory(cur):
    products, inventory, product_prices = generate_products()

    cur.executemany(
        """
        INSERT INTO products
            (product_id, sku, name, category_id, brand, price, active)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s);
        """,
        products,
    )

    cur.executemany(
        """
        INSERT INTO inventory
            (product_id, stock)
        VALUES
            (%s, %s);
        """,
        inventory,
    )

    return product_prices


def insert_customers(cur):
    customers = [
        (
            customer_id,
            f"customer{customer_id}@example.com",
        )
        for customer_id in range(1, CUSTOMER_COUNT + 1)
    ]

    cur.executemany(
        """
        INSERT INTO customers
            (customer_id, email)
        VALUES
            (%s, %s);
        """,
        customers,
    )


def insert_carts_and_cart_items(cur, product_prices):
    carts = []
    cart_items = []

    for cart_id in range(1, CART_COUNT + 1):
        customer_id = cart_id
        status = "active"

        carts.append(
            (
                cart_id,
                customer_id,
                status,
            )
        )

        item_count = random.randint(MIN_CART_ITEMS, MAX_CART_ITEMS)
        product_ids = random.sample(range(1, PRODUCT_COUNT + 1), item_count)

        for product_id in product_ids:
            quantity = random.randint(1, 3)
            unit_price = product_prices[product_id]

            cart_items.append(
                (
                    cart_id,
                    product_id,
                    quantity,
                    unit_price,
                )
            )

    cur.executemany(
        """
        INSERT INTO carts
            (cart_id, customer_id, status)
        VALUES
            (%s, %s, %s);
        """,
        carts,
    )

    cur.executemany(
        """
        INSERT INTO cart_items
            (cart_id, product_id, quantity, unit_price)
        VALUES
            (%s, %s, %s, %s);
        """,
        cart_items,
    )


def print_counts(cur):
    tables = [
        "categories",
        "products",
        "inventory",
        "customers",
        "carts",
        "cart_items",
        "orders",
        "order_items",
    ]

    print("\nDatensatzübersicht:")

    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        print(f"- {table}: {count}")


# ============================================================
# Hauptprogramm
# ============================================================

def main():
    random.seed(RANDOM_SEED)

    print("Verbinde mit PostgreSQL...")

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            print("Leere bestehende Tabellen...")
            reset_database(cur)

            print("Füge Kategorien ein...")
            insert_categories(cur)

            print("Füge Produkte und Bestände ein...")
            product_prices = insert_products_and_inventory(cur)

            print("Füge Kunden ein...")
            insert_customers(cur)

            print("Füge Warenkörbe und Warenkorbpositionen ein...")
            insert_carts_and_cart_items(cur, product_prices)

            conn.commit()

            print_counts(cur)

    print("\nPostgreSQL Seed erfolgreich abgeschlossen.")


if __name__ == "__main__":
    main()