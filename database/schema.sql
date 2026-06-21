-- =============================================================
-- File        : database/schema.sql
-- Description : DDL for the Olist E-Commerce SQLite database.
--               Creates 7 tables with foreign key relationships
--               and performance indexes.
-- =============================================================

PRAGMA foreign_keys = ON;

-- -------------------------
-- 1. Customers
-- -------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id             TEXT PRIMARY KEY,
    customer_unique_id      TEXT NOT NULL,
    customer_zip_code_prefix TEXT,
    customer_city           TEXT,
    customer_state          TEXT
);

-- -------------------------
-- 2. Orders
-- -------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id                TEXT PRIMARY KEY,
    customer_id             TEXT NOT NULL,
    order_status            TEXT,
    order_purchase_timestamp TEXT,
    order_approved_at        TEXT,
    order_delivered_carrier_date TEXT,
    order_delivered_customer_date TEXT,
    order_estimated_delivery_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

-- -------------------------
-- 3. Order Items
-- -------------------------
CREATE TABLE IF NOT EXISTS order_items (
    order_id            TEXT NOT NULL,
    order_item_id       INTEGER NOT NULL,
    product_id          TEXT NOT NULL,
    seller_id           TEXT NOT NULL,
    shipping_limit_date TEXT,
    price               REAL,
    freight_value       REAL,
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id) REFERENCES orders (order_id)
);

-- -------------------------
-- 4. Products
-- -------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id                  TEXT PRIMARY KEY,
    product_category_name       TEXT,
    product_name_lenght         INTEGER,
    product_description_lenght  INTEGER,
    product_photos_qty          INTEGER,
    product_weight_g            REAL,
    product_length_cm           REAL,
    product_height_cm           REAL,
    product_width_cm            REAL
);

-- -------------------------
-- 5. Sellers
-- -------------------------
CREATE TABLE IF NOT EXISTS sellers (
    seller_id               TEXT PRIMARY KEY,
    seller_zip_code_prefix  TEXT,
    seller_city             TEXT,
    seller_state            TEXT
);

-- -------------------------
-- 6. Order Payments
-- -------------------------
CREATE TABLE IF NOT EXISTS order_payments (
    order_id              TEXT NOT NULL,
    payment_sequential    INTEGER NOT NULL,
    payment_type          TEXT,
    payment_installments  INTEGER,
    payment_value         REAL,
    PRIMARY KEY (order_id, payment_sequential),
    FOREIGN KEY (order_id) REFERENCES orders (order_id)
);

-- -------------------------
-- 7. Order Reviews
-- -------------------------
CREATE TABLE IF NOT EXISTS order_reviews (
    review_id               TEXT PRIMARY KEY,
    order_id                TEXT NOT NULL,
    review_score            INTEGER,
    review_comment_title    TEXT,
    review_comment_message  TEXT,
    review_creation_date    TEXT,
    review_answer_timestamp TEXT,
    FOREIGN KEY (order_id) REFERENCES orders (order_id)
);

-- -------------------------
-- Indexes for query performance
-- -------------------------
CREATE INDEX IF NOT EXISTS idx_orders_customer    ON orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status      ON orders (order_status);
CREATE INDEX IF NOT EXISTS idx_orders_purchase    ON orders (order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_items_order        ON order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_items_product      ON order_items (product_id);
CREATE INDEX IF NOT EXISTS idx_items_seller       ON order_items (seller_id);
CREATE INDEX IF NOT EXISTS idx_payments_order     ON order_payments (order_id);
CREATE INDEX IF NOT EXISTS idx_reviews_order      ON order_reviews (order_id);
