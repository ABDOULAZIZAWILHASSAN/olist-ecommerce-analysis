"""
analysis.py
===========
Executes the 10 business analysis SQL queries against the Olist SQLite
database and returns results as labelled pandas DataFrames.

All queries are defined in ``database/queries.sql``; the raw SQL is
also embedded here so the module is self-contained and runnable without
an external file dependency.

Usage:
    from src.analysis import run_all_analyses
    from src.database import DatabaseManager

    with DatabaseManager('database/olist.db') as db:
        results = run_all_analyses(db)
        print(results['monthly_revenue'].head())
"""

import logging
import pandas as pd
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.database import DatabaseManager

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Portuguese → English category name translation map
# (built from product_category_name_translation.csv)
# ---------------------------------------------------------------------------

_PT_TO_EN: dict[str, str] = {
    "beleza_saude": "Health & Beauty",
    "informatica_acessorios": "Computers & Accessories",
    "automotivo": "Auto",
    "cama_mesa_banho": "Bed, Bath & Table",
    "moveis_decoracao": "Furniture & Decor",
    "esporte_lazer": "Sports & Leisure",
    "perfumaria": "Perfumery",
    "utilidades_domesticas": "Housewares",
    "telefonia": "Telephony",
    "relogios_presentes": "Watches & Gifts",
    "alimentos_bebidas": "Food & Drink",
    "bebes": "Baby",
    "papelaria": "Stationery",
    "tablets_impressao_imagem": "Tablets & Printing",
    "brinquedos": "Toys",
    "telefonia_fixa": "Fixed Telephony",
    "ferramentas_jardim": "Garden Tools",
    "fashion_bolsas_e_acessorios": "Fashion Bags & Accessories",
    "eletroportateis": "Small Appliances",
    "consoles_games": "Consoles & Games",
    "audio": "Audio",
    "fashion_calcados": "Fashion Shoes",
    "cool_stuff": "Cool Stuff",
    "malas_acessorios": "Luggage & Accessories",
    "climatizacao": "Air Conditioning",
    "construcao_ferramentas_construcao": "Construction Tools",
    "moveis_cozinha_area_de_servico_jantar_e_jardim": "Kitchen & Garden Furniture",
    "construcao_ferramentas_jardim": "Garden Construction Tools",
    "fashion_roupa_masculina": "Men's Fashion",
    "pet_shop": "Pet Shop",
    "moveis_escritorio": "Office Furniture",
    "market_place": "Marketplace",
    "eletronicos": "Electronics",
    "eletrodomesticos": "Home Appliances",
    "artigos_de_festas": "Party Supplies",
    "casa_conforto": "Home Comfort",
    "construcao_ferramentas_ferramentas": "Tools & Hardware",
    "agro_industria_e_comercio": "Agro Industry & Commerce",
    "moveis_colchao_e_estofado": "Mattress & Upholstery",
    "livros_tecnicos": "Technical Books",
    "casa_construcao": "Home Construction",
    "instrumentos_musicais": "Musical Instruments",
    "moveis_sala": "Living Room Furniture",
    "construcao_ferramentas_iluminacao": "Lighting & Construction",
    "industria_comercio_e_negocios": "Industry & Commerce",
    "alimentos": "Food",
    "artes": "Arts",
    "moveis_quarto": "Bedroom Furniture",
    "livros_interesse_geral": "General Books",
    "construcao_ferramentas_seguranca": "Safety & Construction",
    "fashion_underwear_e_moda_praia": "Fashion Underwear & Beachwear",
    "fashion_esporte": "Fashion Sport",
    "sinalizacao_e_seguranca": "Signaling & Security",
    "pcs": "Computers (PCs)",
    "artigos_de_natal": "Christmas Supplies",
    "fashion_roupa_feminina": "Women's Fashion",
    "eletrodomesticos_2": "Home Appliances 2",
    "livros_importados": "Imported Books",
    "bebidas": "Drinks",
    "cine_foto": "Cinema & Photo",
    "la_cuisine": "La Cuisine",
    "musica": "Music",
    "casa_conforto_2": "Home Comfort 2",
    "portateis_casa_forno_e_cafe": "Small Appliances (Oven & Coffee)",
    "cds_dvds_musicais": "CDs & DVDs",
    "dvds_blu_ray": "DVDs & Blu-Ray",
    "flores": "Flowers",
    "artes_e_artesanato": "Arts & Crafts",
    "fraldas_higiene": "Diapers & Hygiene",
    "fashion_roupa_infanto_juvenil": "Children's Fashion",
    "seguros_e_servicos": "Insurance & Services",
    "Unknown": "Unknown",
}


def translate_categories(df: pd.DataFrame, col: str = "product_category_name") -> pd.DataFrame:
    """Translate Portuguese category names to English in-place."""
    if col in df.columns:
        df = df.copy()
        df[col] = df[col].map(lambda x: _PT_TO_EN.get(str(x), str(x).replace("_", " ").title()))
    return df



# ---------------------------------------------------------------------------
# Individual query functions
# ---------------------------------------------------------------------------

def query_monthly_revenue(db: "DatabaseManager") -> pd.DataFrame:
    """
    Query 1 — Monthly Revenue Trend.
    Returns monthly revenue and order volume across the full dataset period.
    """
    sql = """
    SELECT
        strftime('%Y-%m', o.order_purchase_timestamp)   AS year_month,
        ROUND(SUM(oi.price + oi.freight_value), 2)       AS total_revenue,
        COUNT(DISTINCT o.order_id)                        AS total_orders
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
      AND o.order_purchase_timestamp IS NOT NULL
    GROUP BY year_month
    ORDER BY year_month
    """
    df = pd.DataFrame(db.execute_query(sql))
    if not df.empty:
        df["year_month"] = pd.to_datetime(df["year_month"], format="%Y-%m")
    logger.info("Query 1 (monthly_revenue): %d rows", len(df))
    return df


def query_top_categories(db: "DatabaseManager") -> pd.DataFrame:
    """
    Query 2 — Top 10 Product Categories by Revenue.
    Returns the highest-grossing categories.
    """
    sql = """
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
    LIMIT 10
    """
    df = pd.DataFrame(db.execute_query(sql))
    if not df.empty:
        df = translate_categories(df)
    logger.info("Query 2 (top_categories): %d rows", len(df))
    return df


def query_sales_by_state(db: "DatabaseManager") -> pd.DataFrame:
    """
    Query 3 — Sales Distribution by Brazilian State.
    Shows which states generate the most orders and revenue.
    """
    sql = """
    SELECT
        c.customer_state,
        COUNT(DISTINCT o.order_id)                         AS total_orders,
        ROUND(SUM(oi.price + oi.freight_value), 2)         AS total_revenue,
        ROUND(AVG(oi.price + oi.freight_value), 2)         AS avg_order_value
    FROM customers c
    JOIN orders      o  ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id    = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY c.customer_state
    ORDER BY total_orders DESC
    """
    df = pd.DataFrame(db.execute_query(sql))
    logger.info("Query 3 (sales_by_state): %d rows", len(df))
    return df


def query_payment_methods(db: "DatabaseManager") -> pd.DataFrame:
    """
    Query 4 — Payment Method Usage.
    Breaks down transaction count and total value by payment type.
    """
    sql = """
    SELECT
        payment_type,
        COUNT(*)                                           AS total_transactions,
        ROUND(SUM(payment_value), 2)                       AS total_value,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_share
    FROM order_payments
    WHERE payment_type != 'not_defined'
    GROUP BY payment_type
    ORDER BY total_transactions DESC
    """
    df = pd.DataFrame(db.execute_query(sql))
    logger.info("Query 4 (payment_methods): %d rows", len(df))
    return df


def query_delivery_time(db: "DatabaseManager") -> pd.DataFrame:
    """
    Query 5 — Average Delivery Time by Category.
    Highlights the slowest and fastest shipping product categories.
    """
    sql = """
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
    JOIN order_items oi ON o.order_id   = oi.order_id
    JOIN products   p  ON oi.product_id = p.product_id
    WHERE o.order_delivered_customer_date IS NOT NULL
      AND o.order_purchase_timestamp IS NOT NULL
      AND o.order_status = 'delivered'
    GROUP BY product_category_name
    HAVING total_orders >= 50
    ORDER BY avg_delivery_days DESC
    LIMIT 15
    """
    df = pd.DataFrame(db.execute_query(sql))
    if not df.empty:
        df = translate_categories(df)
    logger.info("Query 5 (delivery_time): %d rows", len(df))
    return df


def query_ratings_distribution(db: "DatabaseManager") -> pd.DataFrame:
    """
    Query 6 — Customer Satisfaction by Delivery Speed.
    Buckets orders by delivery speed and shows average review score per bucket.
    """
    sql = """
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
    ORDER BY avg_review_score DESC
    """
    df = pd.DataFrame(db.execute_query(sql))
    logger.info("Query 6 (ratings_distribution): %d rows", len(df))
    return df


def query_price_by_category(db: "DatabaseManager") -> pd.DataFrame:
    """
    Query 10 — Price Analysis by Category.
    Returns average, min, and max price per product category.
    """
    sql = """
    SELECT
        COALESCE(p.product_category_name, 'Unknown')       AS product_category_name,
        ROUND(AVG(oi.price), 2)                            AS avg_price,
        ROUND(MIN(oi.price), 2)                            AS min_price,
        ROUND(MAX(oi.price), 2)                            AS max_price,
        COUNT(*)                                           AS item_count
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders   o ON oi.order_id   = o.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY product_category_name
    HAVING item_count >= 30
    ORDER BY avg_price DESC
    LIMIT 15
    """
    df = pd.DataFrame(db.execute_query(sql))
    if not df.empty:
        df = translate_categories(df)
    logger.info("Query 7 (price_by_category): %d rows", len(df))
    return df


def query_top_sellers(db: "DatabaseManager") -> pd.DataFrame:
    """
    Query 7 — Top Seller Performance.
    Returns the 10 sellers with the highest total revenue.
    """
    sql = """
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
    LIMIT 10
    """
    df = pd.DataFrame(db.execute_query(sql))
    logger.info("Query 8 (top_sellers): %d rows", len(df))
    return df


def query_seasonal_patterns(db: "DatabaseManager") -> pd.DataFrame:
    """
    Query 8 — Seasonal Order Patterns.
    Aggregates orders and average order value by calendar month.
    """
    sql = """
    SELECT
        CASE strftime('%m', o.order_purchase_timestamp)
            WHEN '01' THEN 'Jan' WHEN '02' THEN 'Feb' WHEN '03' THEN 'Mar'
            WHEN '04' THEN 'Apr' WHEN '05' THEN 'May' WHEN '06' THEN 'Jun'
            WHEN '07' THEN 'Jul' WHEN '08' THEN 'Aug' WHEN '09' THEN 'Sep'
            WHEN '10' THEN 'Oct' WHEN '11' THEN 'Nov' WHEN '12' THEN 'Dec'
        END                                                AS month_name,
        strftime('%m', o.order_purchase_timestamp)         AS month_num,
        COUNT(DISTINCT o.order_id)                         AS total_orders,
        ROUND(AVG(oi.price + oi.freight_value), 2)         AS avg_order_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
      AND o.order_purchase_timestamp IS NOT NULL
    GROUP BY month_num
    ORDER BY month_num
    """
    df = pd.DataFrame(db.execute_query(sql))
    logger.info("Query 9 (seasonal_patterns): %d rows", len(df))
    return df


def query_customer_retention(db: "DatabaseManager") -> pd.DataFrame:
    """
    Query 9 — Customer Retention (Repeat Purchases).
    Shows what percentage of customers make more than one purchase.
    """
    sql = """
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
    ORDER BY purchase_count
    """
    df = pd.DataFrame(db.execute_query(sql))
    if not df.empty:
        # Cast to int so report shows 1, 2, 3 not 1.00, 2.00, 3.00
        df["purchase_frequency"] = df["purchase_frequency"].astype(int)
        df["customer_count"]     = df["customer_count"].astype(int)
    logger.info("Query 10 (customer_retention): %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# Master runner
# ---------------------------------------------------------------------------

def run_all_analyses(db: "DatabaseManager") -> dict[str, pd.DataFrame]:
    """
    Execute all 10 analysis queries and return results as a labelled dict.

    Args:
        db: Open DatabaseManager instance.

    Returns:
        Dictionary mapping analysis_name -> DataFrame.
    """
    logger.info("Running all analysis queries...")
    results = {
        "monthly_revenue":    query_monthly_revenue(db),
        "top_categories":     query_top_categories(db),
        "sales_by_state":     query_sales_by_state(db),
        "payment_methods":    query_payment_methods(db),
        "delivery_time":      query_delivery_time(db),
        "ratings_by_delivery":query_ratings_distribution(db),
        "price_by_category":  query_price_by_category(db),
        "top_sellers":        query_top_sellers(db),
        "seasonal_patterns":  query_seasonal_patterns(db),
        "customer_retention": query_customer_retention(db),
    }
    logger.info("All analyses complete.")
    return results
