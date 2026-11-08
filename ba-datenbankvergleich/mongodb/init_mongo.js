// ============================================================
// MongoDB Init Script V1
// Bachelorarbeit: Datenbankleistung bei hoher Last im E-Commerce
// Ziel: Vereinfachtes E-Commerce-nahes Dokumentmodell für Lasttests
// ============================================================

// Datenbank auswählen
db = db.getSiblingDB("ecommerce");

// ============================================================
// 1. Bestehende Collections löschen
// ============================================================

// Die Collections werden gelöscht, damit der Versuch reproduzierbar
// mit einer leeren Datenbank gestartet werden kann.

db.categories.drop();
db.products.drop();
db.customers.drop();
db.carts.drop();
db.orders.drop();

// ============================================================
// 2. Collections anlegen
// ============================================================

// Kategorien
db.createCollection("categories");

// Produkte
// Hinweis:
// Der Bestand wird bei MongoDB direkt im Produktdokument eingebettet.
// Dadurch kann eine Produktdetailabfrage inklusive Preis und Bestand
// aus einem Dokument gelesen werden.
db.createCollection("products");

// Kunden
db.createCollection("customers");

// Warenkörbe
// Hinweis:
// Warenkorbpositionen werden als eingebettetes Array gespeichert.
// Dadurch kann ein Warenkorb inklusive Positionen in einer Operation
// gelesen werden.
db.createCollection("carts");

// Bestellungen
// Hinweis:
// Bestellpositionen werden ebenfalls eingebettet gespeichert.
// Eine Bestellung besteht damit aus einem Bestelldokument mit
// mehreren Positionen.
db.createCollection("orders");

// ============================================================
// 3. Indexe für das Lastprofil
// ============================================================

// ------------------------------------------------------------
// Kategorien
// ------------------------------------------------------------

db.categories.createIndex(
    { name: 1 },
    { name: "idx_categories_name" }
);

// ------------------------------------------------------------
// Produkte
// ------------------------------------------------------------

// Eindeutige Artikelnummer
db.products.createIndex(
    { sku: 1 },
    {
        unique: true,
        name: "idx_products_sku_unique"
    }
);

// Produktliste / Produktsuche nach Kategorie und Preisbereich
db.products.createIndex(
    { category_id: 1, price: 1 },
    { name: "idx_products_category_price" }
);

// Produktabfragen nur aktiver Produkte
db.products.createIndex(
    { active: 1, category_id: 1 },
    { name: "idx_products_active_category" }
);

// ------------------------------------------------------------
// Kunden
// ------------------------------------------------------------

// Eindeutige E-Mail-Adresse
db.customers.createIndex(
    { email: 1 },
    {
        unique: true,
        name: "idx_customers_email_unique"
    }
);

// ------------------------------------------------------------
// Warenkörbe
// ------------------------------------------------------------

// Aktiver Warenkorb eines Kunden
db.carts.createIndex(
    { customer_id: 1, status: 1 },
    { name: "idx_carts_customer_status" }
);

// Suche nach Produkten innerhalb von Warenkorbpositionen
db.carts.createIndex(
    { "items.product_id": 1 },
    { name: "idx_carts_items_product" }
);

// ------------------------------------------------------------
// Bestellungen
// ------------------------------------------------------------

// Bestellungen eines Kunden nach Erstellungszeit
db.orders.createIndex(
    { customer_id: 1, created_at: -1 },
    { name: "idx_orders_customer_created" }
);

// Suche nach Produkten innerhalb von Bestellpositionen
db.orders.createIndex(
    { "items.product_id": 1 },
    { name: "idx_orders_items_product" }
);

// ============================================================
// 4. Dokumentstruktur V1 als Kommentar
// ============================================================

/*
Beispiel: products

{
    _id: 1,
    sku: "SKU-000001",
    name: "Product 1",
    category_id: 1,
    brand: "Brand A",
    price: 29.99,
    active: true,
    inventory: {
        stock: 250,
        updated_at: ISODate("2026-01-01T00:00:00Z")
    },
    created_at: ISODate("2026-01-01T00:00:00Z")
}

Beispiel: customers

{
    _id: 1,
    email: "customer1@example.com",
    created_at: ISODate("2026-01-01T00:00:00Z")
}

Beispiel: carts

{
    _id: 1,
    customer_id: 1,
    status: "active",
    created_at: ISODate("2026-01-01T00:00:00Z"),
    updated_at: ISODate("2026-01-01T00:00:00Z"),
    items: [
        {
            product_id: 1,
            quantity: 2,
            unit_price: 29.99,
            updated_at: ISODate("2026-01-01T00:00:00Z")
        }
    ]
}

Beispiel: orders

{
    _id: 1,
    customer_id: 1,
    cart_id: 1,
    created_at: ISODate("2026-01-01T00:00:00Z"),
    total_amount: 59.98,
    status: "created",
    items: [
        {
            product_id: 1,
            quantity: 2,
            unit_price: 29.99
        }
    ]
}
*/

// ============================================================
// Ende MongoDB Init Script V1
// ============================================================

print("MongoDB init script completed successfully.");