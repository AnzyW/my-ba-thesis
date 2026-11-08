"""
Locust Smoke Test für MongoDB
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript prüft, ob Locust direkte Datenbankoperationen gegen MongoDB
ausführen und messen kann.

Getestet wird zunächst nur:
- Produktdetail inklusive eingebettetem Bestand abrufen

Der Test ist noch kein vollständiges Lastprofil.
"""

from __future__ import annotations

import random
import time

from locust import User, between, task
from pymongo import MongoClient


MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0&directConnection=true"
DATABASE_NAME = "ecommerce"

PRODUCT_MIN_ID = 1
PRODUCT_MAX_ID = 1_000


class MongoProductUser(User):
    """
    Simuliert einen Nutzer, der wiederholt Produktdetails aus MongoDB abruft.

    Es wird bewusst kein HttpUser verwendet, weil der Versuch nicht eine
    HTTP-API, sondern direkt die Datenbankebene untersucht.
    """

    wait_time = between(0.1, 0.5)

    def on_start(self) -> None:
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]
        self.products = self.db.products

    def on_stop(self) -> None:
        if hasattr(self, "client"):
            self.client.close()

    @task
    def product_detail(self) -> None:
        product_id = random.randint(PRODUCT_MIN_ID, PRODUCT_MAX_ID)

        start_time = time.perf_counter()
        exception = None
        response_length = 0

        try:
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

            response_length = 1

        except Exception as exc:
            exception = exc

        response_time_ms = (time.perf_counter() - start_time) * 1000

        self.environment.events.request.fire(
            request_type="MONGO",
            name="product_detail",
            response_time=response_time_ms,
            response_length=response_length,
            exception=exception,
            context={},
        )