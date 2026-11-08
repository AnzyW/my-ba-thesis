"""
Gemeinsamer Testdaten-Generator V1
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript erzeugt eine gemeinsame, reproduzierbare Datengrundlage
für PostgreSQL und MongoDB. Beide Datenbanksysteme sollen später dieselben
fachlichen Daten laden, damit der empirische Vergleich nicht durch
unterschiedliche Zufallsdaten verfälscht wird.

Erzeugte Dateien:
- data/categories.csv
- data/products.csv
- data/inventory.csv
- data/customers.csv
- data/carts.csv
- data/cart_items.csv
- data/orders.csv
- data/order_items.csv

Standardmäßig wird ein kleiner Testdatensatz erzeugt.
Für den späteren vollständigen Versuch kann das Profil "full" verwendet werden.
"""

from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


# ============================================================
# Konfiguration
# ============================================================

RANDOM_SEED = 42
FIXED_TIMESTAMP = "2026-01-01T00:00:00Z"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class DatasetConfig:
    category_count: int
    product_count: int
    customer_count: int
    cart_count: int
    min_stock: int = 50
    max_stock: int = 500
    min_cart_items: int = 1
    max_cart_items: int = 3


SMALL_CONFIG = DatasetConfig(
    category_count=5,
    product_count=1_000,
    customer_count=100,
    cart_count=100,
)

MEDIUM_CONFIG = DatasetConfig(
    category_count=25,
    product_count=50_000,
    customer_count=5_000,
    cart_count=5_000,
)

FULL_CONFIG = DatasetConfig(
    category_count=50,
    product_count=200_000,
    customer_count=20_000,
    cart_count=20_000,
)


# ============================================================
# CSV-Hilfsfunktionen
# ============================================================

def write_csv(filename: str, fieldnames: list[str], rows: list[dict]) -> None:
    """
    Schreibt eine CSV-Datei mit Header.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Geschrieben: {path.relative_to(PROJECT_ROOT)} ({len(rows)} Zeilen)")


def decimal_price_to_string(value: Decimal) -> str:
    """
    Gibt Preise mit zwei Nachkommastellen als String zurück.
    Dadurch bleiben die CSV-Daten für PostgreSQL und MongoDB identisch.
    """
    return f"{value:.2f}"


# ============================================================
# Datengenerierung
# ============================================================

def generate_categories(config: DatasetConfig) -> list[dict]:
    return [
        {
            "category_id": category_id,
            "name": f"Category {category_id}",
            "created_at": FIXED_TIMESTAMP,
        }
        for category_id in range(1, config.category_count + 1)
    ]


def generate_products_and_inventory(config: DatasetConfig) -> tuple[list[dict], list[dict], dict[int, str]]:
    products = []
    inventory = []
    product_prices: dict[int, str] = {}

    for product_id in range(1, config.product_count + 1):
        price = Decimal(random.randint(500, 50_000)) / Decimal("100")
        price_string = decimal_price_to_string(price)

        products.append(
            {
                "product_id": product_id,
                "sku": f"SKU-{product_id:06d}",
                "name": f"Product {product_id}",
                "category_id": random.randint(1, config.category_count),
                "brand": f"Brand {random.randint(1, 20)}",
                "price": price_string,
                "active": "true",
                "created_at": FIXED_TIMESTAMP,
            }
        )

        inventory.append(
            {
                "product_id": product_id,
                "stock": random.randint(config.min_stock, config.max_stock),
                "updated_at": FIXED_TIMESTAMP,
            }
        )

        product_prices[product_id] = price_string

    return products, inventory, product_prices


def generate_customers(config: DatasetConfig) -> list[dict]:
    return [
        {
            "customer_id": customer_id,
            "email": f"customer{customer_id}@example.com",
            "created_at": FIXED_TIMESTAMP,
        }
        for customer_id in range(1, config.customer_count + 1)
    ]


def generate_carts_and_cart_items(
    config: DatasetConfig,
    product_prices: dict[int, str],
) -> tuple[list[dict], list[dict]]:
    carts = []
    cart_items = []

    for cart_id in range(1, config.cart_count + 1):
        # Für die erste Version wird genau ein aktiver Warenkorb pro Kunde erzeugt.
        # Da cart_count <= customer_count gilt, ist diese Zuordnung eindeutig.
        customer_id = cart_id

        carts.append(
            {
                "cart_id": cart_id,
                "customer_id": customer_id,
                "status": "active",
                "created_at": FIXED_TIMESTAMP,
                "updated_at": FIXED_TIMESTAMP,
            }
        )

        item_count = random.randint(config.min_cart_items, config.max_cart_items)
        product_ids = random.sample(range(1, config.product_count + 1), item_count)

        for product_id in product_ids:
            cart_items.append(
                {
                    "cart_id": cart_id,
                    "product_id": product_id,
                    "quantity": random.randint(1, 3),
                    "unit_price": product_prices[product_id],
                    "updated_at": FIXED_TIMESTAMP,
                }
            )

    return carts, cart_items


def generate_empty_orders() -> tuple[list[dict], list[dict]]:
    """
    In der ersten Datengrundlage werden keine initialen Bestellungen erzeugt.
    Bestellungen entstehen später durch Checkout-Operationen im Lasttest.
    """
    return [], []


# ============================================================
# Hauptlogik
# ============================================================

def generate_dataset(config: DatasetConfig) -> None:
    random.seed(RANDOM_SEED)

    print("Erzeuge gemeinsamen Testdatensatz...")
    print(f"Seed: {RANDOM_SEED}")
    print(f"Zielordner: {DATA_DIR}")

    categories = generate_categories(config)
    products, inventory, product_prices = generate_products_and_inventory(config)
    customers = generate_customers(config)
    carts, cart_items = generate_carts_and_cart_items(config, product_prices)
    orders, order_items = generate_empty_orders()

    write_csv(
        "categories.csv",
        ["category_id", "name", "created_at"],
        categories,
    )

    write_csv(
        "products.csv",
        ["product_id", "sku", "name", "category_id", "brand", "price", "active", "created_at"],
        products,
    )

    write_csv(
        "inventory.csv",
        ["product_id", "stock", "updated_at"],
        inventory,
    )

    write_csv(
        "customers.csv",
        ["customer_id", "email", "created_at"],
        customers,
    )

    write_csv(
        "carts.csv",
        ["cart_id", "customer_id", "status", "created_at", "updated_at"],
        carts,
    )

    write_csv(
        "cart_items.csv",
        ["cart_id", "product_id", "quantity", "unit_price", "updated_at"],
        cart_items,
    )

    write_csv(
        "orders.csv",
        ["order_id", "customer_id", "cart_id", "created_at", "total_amount", "status"],
        orders,
    )

    write_csv(
        "order_items.csv",
        ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
        order_items,
    )

    print("\nDatensatz erfolgreich erzeugt.")
    print("Übersicht:")
    print(f"- Kategorien: {len(categories)}")
    print(f"- Produkte: {len(products)}")
    print(f"- Bestände: {len(inventory)}")
    print(f"- Kunden: {len(customers)}")
    print(f"- Warenkörbe: {len(carts)}")
    print(f"- Warenkorbpositionen: {len(cart_items)}")
    print(f"- Initiale Bestellungen: {len(orders)}")
    print(f"- Initiale Bestellpositionen: {len(order_items)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Erzeugt eine gemeinsame synthetische Datengrundlage für PostgreSQL und MongoDB."
    )

    parser.add_argument(
    "--profile",
    choices=["small", "medium", "full"],
    default="small",
    help="Datensatzprofil: small für Funktionstest, medium für größere Probeläufe, full für optionalen Hauptversuch.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.profile == "small":
        config = SMALL_CONFIG
    elif args.profile == "medium":
        config = MEDIUM_CONFIG
    elif args.profile == "full":
        config = FULL_CONFIG
    else:
        raise ValueError(f"Unbekanntes Profil: {args.profile}")

    generate_dataset(config)


if __name__ == "__main__":
    main()