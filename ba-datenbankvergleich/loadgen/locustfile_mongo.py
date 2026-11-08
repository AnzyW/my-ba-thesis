"""
Locust Lastprofil V1 für MongoDB
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript bildet ein erstes E-Commerce-nahes Lastprofil für MongoDB ab.
Es enthält dieselben fachlichen Operationen wie das PostgreSQL-Lastprofil,
wird aber dokumentenorientiert umgesetzt.

Abgebildete Operationen:
- Produktliste / Produktsuche
- Produktdetail abrufen
- Preis- und Bestandsabfrage
- Warenkorb lesen
- Warenkorb ändern
- Checkout-nahe Transaktion

Wichtig:
Dieses Skript testet direkt die Datenbankebene. Es wird bewusst kein HttpUser
verwendet, da keine HTTP-API und kein vollständiger Online-Shop untersucht wird.
"""

from __future__ import annotations

import random
import time
from datetime import datetime, timezone

from locust import User, between, task
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError


# ============================================================
# Konfiguration
# ============================================================

MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0&directConnection=true"
DATABASE_NAME = "ecommerce"

MAX_CHECKOUT_RETRIES = 3
CHECKOUT_RETRY_SLEEP_SECONDS = 0.05

# ============================================================
# Hilfsfunktion
# ============================================================

def now_utc() -> datetime:
    """
    Gibt einen UTC-Zeitstempel zurück.
    MongoDB speichert Python datetime-Werte als BSON Date.
    """
    return datetime.now(timezone.utc)


# ============================================================
# Locust User
# ============================================================

class MongoEcommerceUser(User):
    """
    Simuliert datenbanknahe E-Commerce-Operationen gegen MongoDB.

    Die Gewichtungen der Tasks orientieren sich am vorläufigen Lastprofil:

    - Produktliste / Produktsuche: 35 %
    - Produktdetail: 25 %
    - Preis- und Bestandsabfrage: 15 %
    - Warenkorb lesen: 5 %
    - Warenkorb ändern: 15 %
    - Checkout: 5 %
    """

    wait_time = between(0.1, 0.5)

    def on_start(self) -> None:
        """
        Wird beim Start eines simulierten Nutzers ausgeführt.
        Jeder Locust-User erhält einen eigenen MongoDB-Client.
        """
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]

        self.categories = self.db.categories
        self.products = self.db.products
        self.customers = self.db.customers
        self.carts = self.db.carts
        self.orders = self.db.orders

        self.max_product_id = self.products.find_one(
            sort=[("_id", -1)],
            projection={"_id": 1},
        )["_id"]

        self.max_category_id = self.categories.find_one(
            sort=[("_id", -1)],
            projection={"_id": 1},
        )["_id"]

        self.max_customer_id = self.customers.find_one(
            sort=[("_id", -1)],
            projection={"_id": 1},
        )["_id"]

    def on_stop(self) -> None:
        """
        Schließt den MongoDB-Client beim Stoppen des simulierten Nutzers.
        """
        if hasattr(self, "client"):
            self.client.close()

    # ========================================================
    # Mess-Hilfsfunktion
    # ========================================================

    def measure(self, name: str, operation) -> None:
        """
        Führt eine Operation aus und meldet Antwortzeit sowie Fehler an Locust.
        """
        start_time = time.perf_counter()
        exception = None
        response_length = 0

        try:
            response_length = operation()
        except Exception as exc:
            exception = exc

        response_time_ms = (time.perf_counter() - start_time) * 1000

        self.environment.events.request.fire(
            request_type="MONGO",
            name=name,
            response_time=response_time_ms,
            response_length=response_length,
            exception=exception,
            context={},
        )

    # ========================================================
    # 1. Produktliste / Produktsuche
    # Gewichtung: 35 %
    # ========================================================

    @task(35)
    def product_list(self) -> None:
        """
        Ruft eine Produktliste anhand von Kategorie und Preisbereich ab.
        """

        def operation() -> int:
            category_id = random.randint(1, self.max_category_id)

            min_price = random.randint(500, 20_000) / 100
            max_price = min_price + random.randint(1_000, 20_000) / 100

            cursor = self.products.find(
                {
                    "active": True,
                    "category_id": category_id,
                    "price": {
                        "$gte": min_price,
                        "$lte": max_price,
                    },
                },
                {
                    "_id": 1,
                    "sku": 1,
                    "name": 1,
                    "price": 1,
                    "inventory.stock": 1,
                },
            ).sort("price", ASCENDING).limit(20)

            rows = list(cursor)
            return len(rows)

        self.measure("product_list", operation)

    # ========================================================
    # 2. Produktdetail
    # Gewichtung: 25 %
    # ========================================================

    @task(25)
    def product_detail(self) -> None:
        """
        Ruft ein einzelnes Produkt inklusive eingebettetem Bestand ab.
        """

        def operation() -> int:
            product_id = random.randint(1, self.max_product_id)

            document = self.products.find_one(
                {
                    "_id": product_id,
                    "active": True,
                },
                {
                    "_id": 1,
                    "sku": 1,
                    "name": 1,
                    "category_id": 1,
                    "brand": 1,
                    "price": 1,
                    "inventory.stock": 1,
                },
            )

            if document is None:
                raise RuntimeError(f"Product not found: {product_id}")

            return 1

        self.measure("product_detail", operation)

    # ========================================================
    # 3. Preis- und Bestandsabfrage
    # Gewichtung: 15 %
    # ========================================================

    @task(15)
    def price_availability(self) -> None:
        """
        Prüft Preis und Bestand eines Produktes.
        """

        def operation() -> int:
            product_id = random.randint(1, self.max_product_id)

            document = self.products.find_one(
                {
                    "_id": product_id,
                    "active": True,
                },
                {
                    "_id": 1,
                    "price": 1,
                    "inventory.stock": 1,
                },
            )

            if document is None:
                raise RuntimeError(f"Price/availability not found: {product_id}")

            return 1

        self.measure("price_availability", operation)

    # ========================================================
    # 4. Warenkorb lesen
    # Gewichtung: 5 %
    # ========================================================

    @task(5)
    def cart_read(self) -> None:
        """
        Liest einen aktiven Warenkorb inklusive eingebetteter Positionen.
        """

        def operation() -> int:
            customer_id = random.randint(1, self.max_customer_id)

            document = self.carts.find_one(
                {
                    "customer_id": customer_id,
                    "status": "active",
                },
                {
                    "_id": 1,
                    "customer_id": 1,
                    "status": 1,
                    "items": 1,
                },
            )

            if document is None:
                return 0

            return len(document.get("items", []))

        self.measure("cart_read", operation)

    # ========================================================
    # 5. Warenkorb ändern
    # Gewichtung: 15 %
    # ========================================================

    @task(15)
    def cart_update(self) -> None:
        """
        Fügt einem aktiven Warenkorb ein Produkt hinzu oder erhöht die Menge.

        Da Warenkorbpositionen in MongoDB eingebettet gespeichert werden,
        wird zuerst versucht, eine vorhandene Position zu erhöhen.
        Falls das Produkt noch nicht im Warenkorb liegt, wird eine neue
        Position in das items-Array eingefügt.
        """

        def operation() -> int:
            customer_id = random.randint(1, self.max_customer_id)
            product_id = random.randint(1, self.max_product_id)
            quantity = random.randint(1, 3)
            timestamp = now_utc()

            cart = self.carts.find_one(
                {
                    "customer_id": customer_id,
                    "status": "active",
                },
                {
                    "_id": 1,
                },
            )

            if cart is None:
                raise RuntimeError(f"No active cart for customer {customer_id}")

            product = self.products.find_one(
                {
                    "_id": product_id,
                    "active": True,
                },
                {
                    "_id": 1,
                    "price": 1,
                },
            )

            if product is None:
                raise RuntimeError(f"Product not found for cart update: {product_id}")

            cart_id = cart["_id"]
            unit_price = product["price"]

            update_existing = self.carts.update_one(
                {
                    "_id": cart_id,
                    "status": "active",
                    "items.product_id": product_id,
                },
                {
                    "$inc": {
                        "items.$.quantity": quantity,
                    },
                    "$set": {
                        "items.$.unit_price": unit_price,
                        "items.$.updated_at": timestamp,
                        "updated_at": timestamp,
                    },
                },
            )

            if update_existing.modified_count == 0:
                self.carts.update_one(
                    {
                        "_id": cart_id,
                        "status": "active",
                    },
                    {
                        "$push": {
                            "items": {
                                "product_id": product_id,
                                "quantity": quantity,
                                "unit_price": unit_price,
                                "updated_at": timestamp,
                            }
                        },
                        "$set": {
                            "updated_at": timestamp,
                        },
                    },
                )

            return 1

        self.measure("cart_update", operation)

    # ========================================================
    # 6. Checkout-nahe Transaktion
    # Gewichtung: 5 %
    # ========================================================

    @task(5)
    def checkout(self) -> None:
        """
        Führt eine vereinfachte checkoutnahe Transaktion aus.

        Bei MongoDB können konkurrierende Schreibtransaktionen zu transienten
        Write Conflicts führen. Solche Fehler werden begrenzt erneut versucht,
        da MongoDB für TransientTransactionError explizit ein Retry der
        Operation beziehungsweise Transaktion vorsieht.

        Ablauf:
        - aktiven Warenkorb mit Positionen auswählen
        - Warenkorb temporär auf checking_out setzen
        - Bestand prüfen
        - Bestellung anlegen
        - Bestand reduzieren
        - Warenkorb auf checked_out setzen
        - neuen aktiven Warenkorb für denselben Kunden anlegen
        """

        def operation() -> int:
            last_exception = None

            for attempt in range(1, MAX_CHECKOUT_RETRIES + 1):
                timestamp = now_utc()

                try:
                    with self.client.start_session() as session:
                        with session.start_transaction():
                            candidate_cursor = self.carts.aggregate(
                                [
                                    {
                                        "$match": {
                                            "status": "active",
                                            "items.0": {"$exists": True},
                                        }
                                    },
                                    {
                                        "$sample": {
                                            "size": 1,
                                        }
                                    },
                                ],
                                session=session,
                            )

                            candidates = list(candidate_cursor)

                            if not candidates:
                                raise RuntimeError("No active cart with items available for checkout")

                            cart = candidates[0]
                            cart_id = cart["_id"]
                            customer_id = cart["customer_id"]
                            items = cart.get("items", [])

                            lock_result = self.carts.update_one(
                                {
                                    "_id": cart_id,
                                    "status": "active",
                                },
                                {
                                    "$set": {
                                        "status": "checking_out",
                                        "updated_at": timestamp,
                                    }
                                },
                                session=session,
                            )

                            if lock_result.modified_count != 1:
                                raise RuntimeError(f"Could not lock cart for checkout: {cart_id}")

                            product_ids = [item["product_id"] for item in items]

                            products_by_id = {
                                product["_id"]: product
                                for product in self.products.find(
                                    {
                                        "_id": {
                                            "$in": product_ids,
                                        }
                                    },
                                    {
                                        "_id": 1,
                                        "inventory.stock": 1,
                                    },
                                    session=session,
                                )
                            }

                            for item in items:
                                product_id = item["product_id"]
                                quantity = item["quantity"]

                                product = products_by_id.get(product_id)

                                if product is None:
                                    raise RuntimeError(f"Product not found during checkout: {product_id}")

                                stock = product.get("inventory", {}).get("stock", 0)

                                if stock < quantity:
                                    raise RuntimeError(
                                        f"Not enough stock for product {product_id}: stock={stock}, quantity={quantity}"
                                    )

                            total_amount = sum(
                                item["quantity"] * item["unit_price"]
                                for item in items
                            )

                            order_document = {
                                "customer_id": customer_id,
                                "cart_id": cart_id,
                                "created_at": timestamp,
                                "total_amount": total_amount,
                                "status": "created",
                                "items": [
                                    {
                                        "product_id": item["product_id"],
                                        "quantity": item["quantity"],
                                        "unit_price": item["unit_price"],
                                    }
                                    for item in items
                                ],
                            }

                            self.orders.insert_one(order_document, session=session)

                            for item in items:
                                product_id = item["product_id"]
                                quantity = item["quantity"]

                                update_result = self.products.update_one(
                                    {
                                        "_id": product_id,
                                        "inventory.stock": {
                                            "$gte": quantity,
                                        },
                                    },
                                    {
                                        "$inc": {
                                            "inventory.stock": -quantity,
                                        },
                                        "$set": {
                                            "inventory.updated_at": timestamp,
                                        },
                                    },
                                    session=session,
                                )

                                if update_result.modified_count != 1:
                                    raise RuntimeError(f"Inventory update failed for product {product_id}")

                            self.carts.update_one(
                                {
                                    "_id": cart_id,
                                },
                                {
                                    "$set": {
                                        "status": "checked_out",
                                        "updated_at": timestamp,
                                    }
                                },
                                session=session,
                            )

                            self.carts.insert_one(
                                {
                                    "customer_id": customer_id,
                                    "status": "active",
                                    "created_at": timestamp,
                                    "updated_at": timestamp,
                                    "items": [],
                                },
                                session=session,
                            )

                    return 1

                except PyMongoError as exc:
                    last_exception = exc

                    is_transient_transaction_error = (
                        hasattr(exc, "has_error_label")
                        and exc.has_error_label("TransientTransactionError")
                    )

                    if is_transient_transaction_error and attempt < MAX_CHECKOUT_RETRIES:
                        time.sleep(CHECKOUT_RETRY_SLEEP_SECONDS * attempt)
                        continue

                    raise RuntimeError(
                        f"MongoDB checkout transaction failed after {attempt} attempt(s): {exc}"
                    ) from exc

            raise RuntimeError(
                f"MongoDB checkout transaction failed after {MAX_CHECKOUT_RETRIES} attempts: {last_exception}"
            )

        self.measure("checkout", operation)