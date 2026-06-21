-- =============================================================
-- File        : database/queries.sql
-- Description : 10 business analysis queries for the Olist
--               Brazilian E-Commerce dataset.  Each query is
--               documented with its purpose and expected output.
-- =============================================================

-- ================================================================
-- QUERY 1: Monthly Revenue Trend
-- Purpose : Track total revenue and number of orders month-by-month
--           to identify growth trends and seasonality.
-- Returns : year_month (YYYY-MM), total_revenue, total_orders
-- ================================================================
SELECT
    strftime('%Y-%m', o.order_purchase_timestamp)   AS year_month,
    ROUND(SUM(oi.price + oi.freight_value), 2)       AS total_revenue,
    COUNT(DISTINCT o.order_id)                        AS total_orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
  AND o.order_purchase_timestamp IS NOT NULL
GROUP BY year_month
ORDER BY year_month;


-- ================================================================
-- QUERY 2: Top 10 Product Categories by Revenue
-- Purpose : Identify best-performing product categories to guide
--           inventory and marketing decisions.
-- Returns : product_category_name, total_revenue, total_orders
-- ================================================================
SELECT
    COALESCE(p.product_category_name, 'Unknown')      AS product_category_name,
    ROUND(SUM(oi.price), 2)                            AS total_revenue,
    COUNT(DISTINCT oi.order_id)                        AS total_orders,
    ROUND(AVG(oi.price), 2)                            AS avg_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o   ON oi.order_id   = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY product_category_name
ORDER BY total_revenue DESC
LIMIT 10;


-- ================================================================
-- QUERY 3: Sales Distribution by Brazilian State
-- Purpose : Reveal geographic concentration of sales to support
--           regional marketing and logistics planning.
-- Returns : customer_state, total_orders, total_revenue
-- ================================================================
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id)                         AS total_orders,
    ROUND(SUM(oi.price + oi.freight_value), 2)         AS total_revenue,
    ROUND(AVG(oi.price + oi.freight_value), 2)         AS avg_order_value
FROM customers c
JOIN orders     o  ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id  = oi.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY c.customer_state
ORDER BY total_orders DESC;


-- ================================================================
-- QUERY 4: Payment Method Usage
-- Purpose : Understand how customers prefer to pay — informs
--           checkout UX and partnership decisions with payment gateways.
-- Returns : payment_type, total_transactions, total_value, pct_share
-- ================================================================
SELECT
    payment_type,
    COUNT(*)                                           AS total_transactions,
    ROUND(SUM(payment_value), 2)                       AS total_value,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_share
FROM order_payments
WHERE payment_type != 'not_defined'
GROUP BY payment_type
ORDER BY total_transactions DESC;


-- ================================================================
-- QUERY 5: Delivery Time Analysis by Category
-- Purpose : Measure average days from purchase to delivery per
--           product category to highlight logistics pain points.
-- Returns : product_category_name, avg_delivery_days, total_orders
-- ================================================================
SELECT
    COALESCE(p.product_category_name, 'Unknown')       AS product_category_name,
    ROUND(
        AVG(
            julianday(o.order_delivered_customer_date) -
            julianday(o.order_purchase_timestamp)
        ), 1
    )                                                   AS avg_delivery_days,
    COUNT(DISTINCT o.order_id)                          AS total_orders
FROM orders o
JOIN order_items oi ON o.order_id  = oi.order_id
JOIN products   p  ON oi.product_id = p.product_id
WHERE o.order_delivered_customer_date IS NOT NULL
  AND o.order_purchase_timestamp IS NOT NULL
  AND o.order_status = 'delivered'
GROUP BY product_category_name
HAVING total_orders >= 50
ORDER BY avg_delivery_days DESC
LIMIT 15;


-- ================================================================
-- QUERY 6: Customer Satisfaction by Delivery Speed
-- Purpose : Quantify the relationship between fast delivery and
--           high review scores — validates investment in logistics.
-- Returns : delivery_speed_bucket, avg_review_score, order_count
-- ================================================================
SELECT
    CASE
        WHEN julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp) <= 7
             THEN '0-7 days (Fast)'
        WHEN julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp) <= 14
             THEN '8-14 days (Normal)'
        WHEN julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp) <= 21
             THEN '15-21 days (Slow)'
        ELSE '22+ days (Very Slow)'
    END                                                 AS delivery_speed_bucket,
    ROUND(AVG(r.review_score), 2)                       AS avg_review_score,
    COUNT(DISTINCT o.order_id)                          AS order_count
FROM orders o
JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_delivered_customer_date IS NOT NULL
  AND o.order_purchase_timestamp IS NOT NULL
  AND o.order_status = 'delivered'
GROUP BY delivery_speed_bucket
ORDER BY avg_review_score DESC;


-- ================================================================
-- QUERY 7: Top 10 Seller Performance
-- Purpose : Identify the highest-revenue sellers for partnership
--           prioritisation and seller success programs.
-- Returns : seller_id, seller_city, seller_state, total_revenue, total_orders
-- ================================================================
SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,
    ROUND(SUM(oi.price), 2)                            AS total_revenue,
    COUNT(DISTINCT oi.order_id)                        AS total_orders,
    ROUND(AVG(r.review_score), 2)                      AS avg_review_score
FROM sellers s
JOIN order_items   oi ON s.seller_id  = oi.seller_id
JOIN orders        o  ON oi.order_id  = o.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY s.seller_id, s.seller_city, s.seller_state
ORDER BY total_revenue DESC
LIMIT 10;


-- ================================================================
-- QUERY 8: Seasonal Patterns — Monthly Order Volume
-- Purpose : Detect which months have peak demand to align
--           inventory levels, staffing, and promotions.
-- Returns : month_name, avg_monthly_orders, avg_monthly_revenue
-- ================================================================
SELECT
    CASE strftime('%m', o.order_purchase_timestamp)
        WHEN '01' THEN 'January'
        WHEN '02' THEN 'February'
        WHEN '03' THEN 'March'
        WHEN '04' THEN 'April'
        WHEN '05' THEN 'May'
        WHEN '06' THEN 'June'
        WHEN '07' THEN 'July'
        WHEN '08' THEN 'August'
        WHEN '09' THEN 'September'
        WHEN '10' THEN 'October'
        WHEN '11' THEN 'November'
        WHEN '12' THEN 'December'
    END                                                AS month_name,
    strftime('%m', o.order_purchase_timestamp)         AS month_num,
    COUNT(DISTINCT o.order_id)                         AS total_orders,
    ROUND(AVG(oi.price + oi.freight_value), 2)         AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
  AND o.order_purchase_timestamp IS NOT NULL
GROUP BY month_num
ORDER BY month_num;


-- ================================================================
-- QUERY 9: Customer Retention — Repeat Purchase Rate
-- Purpose : Measure how many customers make more than one purchase,
--           a key indicator of loyalty and lifetime value.
-- Returns : purchase_frequency, customer_count, pct_of_total
-- ================================================================
SELECT
    purchase_count                                      AS purchase_frequency,
    COUNT(*)                                            AS customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_total
FROM (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id)                      AS purchase_count
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY c.customer_unique_id
) sub
GROUP BY purchase_count
ORDER BY purchase_count;


-- ================================================================
-- QUERY 10: Price Analysis by Category
-- Purpose : Understand the price positioning across categories —
--           reveals premium vs. budget market segments.
-- Returns : product_category_name, avg_price, min_price, max_price, item_count
-- ================================================================
SELECT
    COALESCE(p.product_category_name, 'Unknown')       AS product_category_name,
    ROUND(AVG(oi.price), 2)                            AS avg_price,
    ROUND(MIN(oi.price), 2)                            AS min_price,
    ROUND(MAX(oi.price), 2)                            AS max_price,
    ROUND(
        AVG(oi.price) - (SELECT AVG(price) FROM order_items), 2
    )                                                  AS diff_from_global_avg,
    COUNT(*)                                           AS item_count
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders   o ON oi.order_id   = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY product_category_name
HAVING item_count >= 30
ORDER BY avg_price DESC
LIMIT 15;
