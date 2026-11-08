"""
Locust Lastprofil V1 für PostgreSQL
Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce

Ziel:
Dieses Skript bildet ein erstes E-Commerce-nahes Lastprofil für PostgreSQL ab.
Es enthält mehrere datenbanknahe Operationen mit Gewichtungen.

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
from decimal import Decimal

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


# ============================================================
# Locust User
# ============================================================

class PostgreSqlEcommerceUser(User):
    """
    Simuliert datenbanknahe E-Commerce-Operationen gegen PostgreSQL.

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
        Jeder Locust-User erhält eine eigene PostgreSQL-Verbindung.
        """
        self.conn = psycopg.connect(**DB_CONFIG, autocommit=True)

        with self.conn.cursor() as cur:
            cur.execute("SELECT MAX(product_id) FROM products;")
            self.max_product_id = cur.fetchone()[0]

            cur.execute("SELECT MAX(category_id) FROM categories;")
            self.max_category_id = cur.fetchone()[0]

            cur.execute("SELECT MAX(customer_id) FROM customers;")
            self.max_customer_id = cur.fetchone()[0]

    def on_stop(self) -> None:
        """
        Schließt die Datenbankverbindung beim Stoppen des simulierten Nutzers.
        """
        if hasattr(self, "conn"):
            self.conn.close()

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
            request_type="POSTGRES",
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

            min_price = Decimal(random.randint(500, 20_000)) / Decimal("100")
            max_price = min_price + Decimal(random.randint(1_000, 20_000)) / Decimal("100")

            query = """
                SELECT
                    p.product_id,
                    p.sku,
                    p.name,
                    p.price,
                    i.stock
                FROM products p
                JOIN inventory i
                    ON p.product_id = i.product_id
                WHERE p.active = TRUE
                  AND p.category_id = %s
                  AND p.price BETWEEN %s AND %s
                ORDER BY p.price
                LIMIT 20;
            """

            with self.conn.cursor() as cur:
                cur.execute(query, (category_id, min_price, max_price))
                rows = cur.fetchall()

            return len(rows)

        self.measure("product_list", operation)

    # ========================================================
    # 2. Produktdetail
    # Gewichtung: 25 %
    # ========================================================

    @task(25)
    def product_detail(self) -> None:
        """
        Ruft ein einzelnes Produkt inklusive Bestand ab.
        """

        def operation() -> int:
            product_id = random.randint(1, self.max_product_id)

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

            with self.conn.cursor() as cur:
                cur.execute(query, (product_id,))
                row = cur.fetchone()

            if row is None:
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

            query = """
                SELECT
                    p.price,
                    i.stock
                FROM products p
                JOIN inventory i
                    ON p.product_id = i.product_id
                WHERE p.product_id = %s
                  AND p.active = TRUE;
            """

            with self.conn.cursor() as cur:
                cur.execute(query, (product_id,))
                row = cur.fetchone()

            if row is None:
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
        Liest einen aktiven Warenkorb inklusive Positionen.
        """

        def operation() -> int:
            customer_id = random.randint(1, self.max_customer_id)

            query = """
                SELECT
                    c.cart_id,
                    c.customer_id,
                    c.status,
                    ci.product_id,
                    ci.quantity,
                    ci.unit_price
                FROM carts c
                LEFT JOIN cart_items ci
                    ON c.cart_id = ci.cart_id
                WHERE c.customer_id = %s
                  AND c.status = 'active';
            """

            with self.conn.cursor() as cur:
                cur.execute(query, (customer_id,))
                rows = cur.fetchall()

            return len(rows)

        self.measure("cart_read", operation)

    # ========================================================
    # 5. Warenkorb ändern
    # Gewichtung: 15 %
    # ========================================================

    @task(15)
    def cart_update(self) -> None:
        """
        Fügt einem aktiven Warenkorb ein Produkt hinzu oder erhöht die Menge.
        """

        def operation() -> int:
            product_id = random.randint(1, self.max_product_id)

            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT cart_id
                    FROM carts
                    WHERE status = 'active'
                    ORDER BY random()
                    LIMIT 1;
                    """
                )
                cart_row = cur.fetchone()

                if cart_row is None:
                    raise RuntimeError("No active cart available")

                cart_id = cart_row[0]

                cur.execute(
                    """
                    SELECT price
                    FROM products
                    WHERE product_id = %s
                      AND active = TRUE;
                    """,
                    (product_id,),
                )
                price_row = cur.fetchone()

                if price_row is None:
                    raise RuntimeError(f"Product not found for cart update: {product_id}")

                unit_price = price_row[0]
                quantity = random.randint(1, 3)

                cur.execute(
                    """
                    INSERT INTO cart_items
                        (cart_id, product_id, quantity, unit_price, updated_at)
                    VALUES
                        (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (cart_id, product_id)
                    DO UPDATE SET
                        quantity = cart_items.quantity + EXCLUDED.quantity,
                        unit_price = EXCLUDED.unit_price,
                        updated_at = CURRENT_TIMESTAMP;
                    """,
                    (cart_id, product_id, quantity, unit_price),
                )

                cur.execute(
                    """
                    UPDATE carts
                    SET updated_at = CURRENT_TIMESTAMP
                    WHERE cart_id = %s;
                    """,
                    (cart_id,),
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

        Ablauf:
        - aktiven Warenkorb mit Positionen auswählen
        - Bestand prüfen
        - Bestellung anlegen
        - Bestellpositionen anlegen
        - Bestand reduzieren
        - Warenkorb auf checked_out setzen
        - neuen aktiven Warenkorb für denselben Kunden anlegen

        Dadurch wird verhindert, dass im Laufe eines längeren Tests alle
        aktiven Warenkörbe vollständig verschwinden.
        """

        def operation() -> int:
            with self.conn.transaction():
                with self.conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            c.cart_id,
                            c.customer_id
                        FROM carts c
                        WHERE c.status = 'active'
                          AND EXISTS (
                              SELECT 1
                              FROM cart_items ci
                              WHERE ci.cart_id = c.cart_id
                          )
                        ORDER BY random()
                        LIMIT 1
                        FOR UPDATE SKIP LOCKED;
                        """
                    )

                    cart_row = cur.fetchone()

                    if cart_row is None:
                        raise RuntimeError("No active cart with items available for checkout")

                    cart_id, customer_id = cart_row

                    cur.execute(
                        """
                        SELECT
                            ci.product_id,
                            ci.quantity,
                            ci.unit_price,
                            i.stock
                        FROM cart_items ci
                        JOIN inventory i
                            ON ci.product_id = i.product_id
                        WHERE ci.cart_id = %s
                        FOR UPDATE OF i;
                        """,
                        (cart_id,),
                    )

                    items = cur.fetchall()

                    if not items:
                        raise RuntimeError(f"Cart has no items: {cart_id}")

                    for product_id, quantity, unit_price, stock in items:
                        if stock < quantity:
                            raise RuntimeError(
                                f"Not enough stock for product {product_id}: stock={stock}, quantity={quantity}"
                            )

                    total_amount = sum(
                        quantity * unit_price
                        for product_id, quantity, unit_price, stock in items
                    )

                    cur.execute(
                        """
                        INSERT INTO orders
                            (customer_id, cart_id, total_amount, status, created_at)
                        VALUES
                            (%s, %s, %s, 'created', CURRENT_TIMESTAMP)
                        RETURNING order_id;
                        """,
                        (customer_id, cart_id, total_amount),
                    )

                    order_id = cur.fetchone()[0]

                    for product_id, quantity, unit_price, stock in items:
                        cur.execute(
                            """
                            INSERT INTO order_items
                                (order_id, product_id, quantity, unit_price)
                            VALUES
                                (%s, %s, %s, %s);
                            """,
                            (order_id, product_id, quantity, unit_price),
                        )

                        cur.execute(
                            """
                            UPDATE inventory
                            SET
                                stock = stock - %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE product_id = %s
                              AND stock >= %s;
                            """,
                            (quantity, product_id, quantity),
                        )

                        if cur.rowcount != 1:
                            raise RuntimeError(f"Inventory update failed for product {product_id}")

                    cur.execute(
                        """
                        UPDATE carts
                        SET
                            status = 'checked_out',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE cart_id = %s;
                        """,
                        (cart_id,),
                    )

                    cur.execute(
                        """
                        INSERT INTO carts
                            (customer_id, status, created_at, updated_at)
                        VALUES
                            (%s, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
                        """,
                        (customer_id,),
                    )

            return 1

        self.measure("checkout", operation)