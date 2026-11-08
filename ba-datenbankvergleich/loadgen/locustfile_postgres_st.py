"""
Locust Smoke Test für PostgreSQL
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript prüft zunächst nur, ob Locust erfolgreich direkte
Datenbankoperationen gegen PostgreSQL ausführen und messen kann.

Es wird bewusst nur eine einfache Operation getestet:
- Produktdetail inklusive Bestand abrufen

Der Test ist noch kein vollständiges Lastprofil.
Er dient nur als technischer Smoke-Test.
"""

from __future__ import annotations

import random
import time

import psycopg
from locust import User, between, task


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

PRODUCT_MIN_ID = 1
PRODUCT_MAX_ID = 1_000


# ============================================================
# Locust User
# ============================================================

class PostgreSqlProductUser(User):
    """
    Simuliert einen Nutzer, der wiederholt Produktdetails abruft.

    Wichtig:
    Wir verwenden hier bewusst keinen HttpUser, weil der Versuch nicht
    eine HTTP-API oder einen vollständigen Webshop misst, sondern direkt
    die Datenbankebene.
    """

    wait_time = between(0.1, 0.5)

    def on_start(self) -> None:
        """
        Wird beim Start eines simulierten Nutzers ausgeführt.
        Jeder Locust-User erhält eine eigene Datenbankverbindung.
        """
        self.conn = psycopg.connect(**DB_CONFIG)

    def on_stop(self) -> None:
        """
        Wird beim Stoppen eines simulierten Nutzers ausgeführt.
        Die Datenbankverbindung wird sauber geschlossen.
        """
        if hasattr(self, "conn"):
            self.conn.close()

    @task
    def product_detail(self) -> None:
        """
        Führt eine Produktdetailabfrage aus.

        Gemessen wird:
        - Antwortzeit der Datenbankoperation
        - Erfolg oder Fehler der Operation

        Die Messwerte werden über Locusts internes Event-System registriert.
        """
        product_id = random.randint(PRODUCT_MIN_ID, PRODUCT_MAX_ID)

        query = """
            SELECT
                p.product_id,
                p.sku,
                p.name,
                p.category_id,
                p.brand,
                p.price,
                i.stock
            FROM products p
            JOIN inventory i
                ON p.product_id = i.product_id
            WHERE p.product_id = %s
              AND p.active = TRUE;
        """

        start_time = time.perf_counter()
        exception = None
        response_length = 0

        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (product_id,))
                row = cur.fetchone()

                if row is None:
                    raise RuntimeError(f"Product not found: {product_id}")

                response_length = 1

        except Exception as exc:
            exception = exc

        response_time_ms = (time.perf_counter() - start_time) * 1000

        self.environment.events.request.fire(
            request_type="POSTGRES",
            name="product_detail",
            response_time=response_time_ms,
            response_length=response_length,
            exception=exception,
            context={},
        )