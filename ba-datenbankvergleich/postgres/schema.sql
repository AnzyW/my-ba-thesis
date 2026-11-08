-- ============================================================
-- PostgreSQL Schema V1
-- Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce
-- Ziel: Vereinfachtes E-Commerce-nahes Datenmodell für Lasttests
-- ============================================================

DROP TABLE IF EXISTS order_items;
-- Alte Tabellen löschen, damit das Schema reproduzierbar neu aufgebaut werden kann.
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS carts;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS categories;

-- ============================================================
-- 1. Kategorien
-- ============================================================

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. Produkte
-- ============================================================

CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(category_id),
    brand VARCHAR(100),
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. Bestand
-- ============================================================

CREATE TABLE inventory (
    product_id BIGINT PRIMARY KEY REFERENCES products(product_id),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 4. Kunden
-- ============================================================

CREATE TABLE customers (
    customer_id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. Warenkörbe
-- ============================================================

CREATE TABLE carts (
    cart_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT carts_status_check
        CHECK (status IN ('active', 'checked_out', 'abandoned'))
);

-- ============================================================
-- 6. Warenkorbpositionen
-- ============================================================

CREATE TABLE cart_items (
    cart_id BIGINT NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (cart_id, product_id)
);

-- ============================================================
-- 7. Bestellungen
-- ============================================================

CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    cart_id BIGINT REFERENCES carts(cart_id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'created',

    CONSTRAINT orders_status_check
        CHECK (status IN ('created', 'paid', 'cancelled'))
);

-- ============================================================
-- 8. Bestellpositionen
-- ============================================================

CREATE TABLE order_items (
    order_item_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

-- ============================================================
-- 9. Indexe für das Lastprofil
-- ============================================================

-- Produktliste / Produktsuche nach Kategorie und Preisbereich
CREATE INDEX idx_products_category_price
    ON products(category_id, price);

-- Produktabfragen nur aktiver Produkte
CREATE INDEX idx_products_active_category
    ON products(active, category_id);

-- Zugriff auf Bestandsdaten
CREATE INDEX idx_inventory_product
    ON inventory(product_id);

-- Aktiver Warenkorb eines Kunden
CREATE INDEX idx_carts_customer_status
    ON carts(customer_id, status);

-- Warenkorbpositionen nach Produkt
CREATE INDEX idx_cart_items_product
    ON cart_items(product_id);

-- Bestellungen eines Kunden nach Erstellungszeit
CREATE INDEX idx_orders_customer_created
    ON orders(customer_id, created_at);

-- Bestellpositionen nach Produkt
CREATE INDEX idx_order_items_product
    ON order_items(product_id);

-- ============================================================
-- Ende Schema V1
-- ============================================================