"""
PostgreSQL CSV Seed Script V2
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript lädt die gemeinsame synthetische Datengrundlage aus dem Ordner
data/ in PostgreSQL. Dadurch verwenden PostgreSQL und MongoDB dieselben
fachlichen Testdaten.

Voraussetzung:
Vorher muss scripts/generate_dataset.py ausgeführt worden sein.
"""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

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


def to_bool(value: str) -> bool:
    """
    Wandelt CSV-Boolean-Werte in Python-Boolean-Werte um.
    """
    return value.lower() == "true"


# ============================================================
# Datenbankoperationen
# ============================================================

def reset_database(cur) -> None:
    """
    Leert alle Tabellen und setzt automatisch erzeugte IDs zurück.
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


def load_categories(cur) -> None:
    rows = read_csv("categories.csv")

    data = [
        (
            int(row["category_id"]),
            row["name"],
            row["created_at"],
        )
        for row in rows
    ]

    cur.executemany(
        """
        INSERT INTO categories
            (category_id, name, created_at)
        VALUES
            (%s, %s, %s);
        """,
        data,
    )


def load_products(cur) -> None:
    rows = read_csv("products.csv")

    data = [
        (
            int(row["product_id"]),
            row["sku"],
            row["name"],
            int(row["category_id"]),
            row["brand"],
            Decimal(row["price"]),
            to_bool(row["active"]),
            row["created_at"],
        )
        for row in rows
    ]

    cur.executemany(
        """
        INSERT INTO products
            (product_id, sku, name, category_id, brand, price, active, created_at)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s);
        """,
        data,
    )


def load_inventory(cur) -> None:
    rows = read_csv("inventory.csv")

    data = [
        (
            int(row["product_id"]),
            int(row["stock"]),
            row["updated_at"],
        )
        for row in rows
    ]

    cur.executemany(
        """
        INSERT INTO inventory
            (product_id, stock, updated_at)
        VALUES
            (%s, %s, %s);
        """,
        data,
    )


def load_customers(cur) -> None:
    rows = read_csv("customers.csv")

    data = [
        (
            int(row["customer_id"]),
            row["email"],
            row["created_at"],
        )
        for row in rows
    ]

    cur.executemany(
        """
        INSERT INTO customers
            (customer_id, email, created_at)
        VALUES
            (%s, %s, %s);
        """,
        data,
    )


def load_carts(cur) -> None:
    rows = read_csv("carts.csv")

    data = [
        (
            int(row["cart_id"]),
            int(row["customer_id"]),
            row["status"],
            row["created_at"],
            row["updated_at"],
        )
        for row in rows
    ]

    cur.executemany(
        """
        INSERT INTO carts
            (cart_id, customer_id, status, created_at, updated_at)
        VALUES
            (%s, %s, %s, %s, %s);
        """,
        data,
    )


def load_cart_items(cur) -> None:
    rows = read_csv("cart_items.csv")

    data = [
        (
            int(row["cart_id"]),
            int(row["product_id"]),
            int(row["quantity"]),
            Decimal(row["unit_price"]),
            row["updated_at"],
        )
        for row in rows
    ]

    cur.executemany(
        """
        INSERT INTO cart_items
            (cart_id, product_id, quantity, unit_price, updated_at)
        VALUES
            (%s, %s, %s, %s, %s);
        """,
        data,
    )


def load_orders(cur) -> None:
    rows = read_csv("orders.csv")

    if not rows:
        return

    data = [
        (
            int(row["order_id"]),
            int(row["customer_id"]),
            int(row["cart_id"]),
            row["created_at"],
            Decimal(row["total_amount"]),
            row["status"],
        )
        for row in rows
    ]

    cur.executemany(
        """
        INSERT INTO orders
            (order_id, customer_id, cart_id, created_at, total_amount, status)
        VALUES
            (%s, %s, %s, %s, %s, %s);
        """,
        data,
    )


def load_order_items(cur) -> None:
    rows = read_csv("order_items.csv")

    if not rows:
        return

    data = [
        (
            int(row["order_item_id"]),
            int(row["order_id"]),
            int(row["product_id"]),
            int(row["quantity"]),
            Decimal(row["unit_price"]),
        )
        for row in rows
    ]

    cur.executemany(
        """
        INSERT INTO order_items
            (order_item_id, order_id, product_id, quantity, unit_price)
        VALUES
            (%s, %s, %s, %s, %s);
        """,
        data,
    )


def update_sequences(cur) -> None:
    """
    Aktualisiert PostgreSQL-Sequenzen nach explizit eingefügten IDs.
    Das verhindert spätere Konflikte, wenn neue Datensätze ohne explizite ID
    eingefügt werden, zum Beispiel Bestellungen im Lasttest.
    """
    sequence_updates = [
        ("products", "product_id"),
        ("customers", "customer_id"),
        ("carts", "cart_id"),
        ("orders", "order_id"),
        ("order_items", "order_item_id"),
    ]

    for table_name, id_column in sequence_updates:
        cur.execute(
            f"""
            SELECT setval(
                pg_get_serial_sequence('{table_name}', '{id_column}'),
                COALESCE((SELECT MAX({id_column}) FROM {table_name}), 1),
                (SELECT COUNT(*) > 0 FROM {table_name})
            );
            """
        )


def print_counts(cur) -> None:
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

    print("\nDatensatzübersicht PostgreSQL:")

    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        print(f"- {table}: {count}")


# ============================================================
# Hauptprogramm
# ============================================================

def main() -> None:
    print("Verbinde mit PostgreSQL...")
    print(f"Lade CSV-Daten aus: {DATA_DIR}")

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            print("Leere bestehende Tabellen...")
            reset_database(cur)

            print("Lade Kategorien...")
            load_categories(cur)

            print("Lade Produkte...")
            load_products(cur)

            print("Lade Bestände...")
            load_inventory(cur)

            print("Lade Kunden...")
            load_customers(cur)

            print("Lade Warenkörbe...")
            load_carts(cur)

            print("Lade Warenkorbpositionen...")
            load_cart_items(cur)

            print("Lade initiale Bestellungen...")
            load_orders(cur)

            print("Lade initiale Bestellpositionen...")
            load_order_items(cur)

            print("Aktualisiere Sequenzen...")
            update_sequences(cur)

            conn.commit()

            print_counts(cur)

    print("\nPostgreSQL CSV Seed erfolgreich abgeschlossen.")


if __name__ == "__main__":
    main()