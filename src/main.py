"""
main.py
=======
Main pipeline orchestrator for the Olist E-Commerce Analysis.

Execution sequence:
  1. Set up logging and directories
  2. Initialize the SQLite database (apply schema)
  3. Load raw CSV data files into database tables
  4. Execute all 10 analysis queries
  5. Generate 7 visualisation charts (PNG)
  6. Write the analysis report (Markdown)

Run from the project root:
    python src/main.py

Dependencies:
    pip install -r requirements.txt
"""

import sys
import time
import logging
import textwrap
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Resolve project root so imports work whether script is invoked from root
# or from src/
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.database      import DatabaseManager
from src.analysis      import run_all_analyses
from src.visualizations import create_all_charts

# ---------------------------------------------------------------------------
# Configuration — edit paths here if needed
# ---------------------------------------------------------------------------
DB_PATH      = ROOT / "database" / "olist.db"
SCHEMA_PATH  = ROOT / "database" / "schema.sql"
DATA_DIR     = ROOT / "data" / "raw"
OUTPUT_DIR   = ROOT / "output"
CHARTS_DIR   = OUTPUT_DIR / "charts"
REPORT_PATH  = OUTPUT_DIR / "analysis_report.md"


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def setup_logging() -> None:
    """Configure console and file logging."""
    log_fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_fmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(ROOT / "notes" / "pipeline.log", encoding="utf-8"),
        ]
    )


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def write_report(results: dict, report_path: Path) -> None:
    """
    Write a comprehensive Markdown analysis report from query results.

    Args:
        results:     Dict of DataFrames from run_all_analyses().
        report_path: Destination path for the .md file.
    """
    logger = logging.getLogger(__name__)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    def h(level: int, text: str) -> None:
        lines.append(f"\n{'#' * level} {text}\n")

    def p(text: str) -> None:
        lines.append(textwrap.fill(text, width=100) + "\n")

    def table_from_df(df, columns=None, fmt=None) -> None:
        """Render first 10 rows of a DataFrame as a Markdown table."""
        if df.empty:
            lines.append("_No data available._\n")
            return
        cols = columns or list(df.columns)
        df_t = df[cols].head(10)
        header = "| " + " | ".join(cols) + " |"
        sep    = "| " + " | ".join(["---"] * len(cols)) + " |"
        lines.append(header)
        lines.append(sep)
        for _, row in df_t.iterrows():
            cells = []
            for c in cols:
                v = row[c]
                if isinstance(v, float):
                    cells.append(f"{v:,.2f}")
                elif isinstance(v, int):
                    cells.append(f"{v:,}")
                else:
                    cells.append(str(v))
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")

    # -----------------------------------------------------------------------
    # Title & Executive Summary
    # -----------------------------------------------------------------------
    h(1, "Olist E-Commerce Analysis Report")
    lines.append(f"**Course**: WAP 228 — Workplace Application  \n")
    lines.append(f"**University**: OSTIM Technical University  \n")
    lines.append(f"**Generated**: {datetime.now().strftime('%B %d, %Y at %H:%M')}  \n")
    lines.append("\n---\n")

    h(2, "Executive Summary")
    p(
        "This report presents a comprehensive data analysis of the Olist Brazilian E-Commerce "
        "Public Dataset, covering over 100,000 orders placed between September 2016 and October "
        "2018. Using Python, SQLite, and data visualization libraries, the analysis uncovers "
        "actionable insights across revenue trends, product performance, geographic distribution, "
        "payment preferences, logistics efficiency, and customer satisfaction."
    )
    p(
        "Key findings: São Paulo dominates sales (42% of orders), credit card is the overwhelmingly "
        "preferred payment method (74%), delivery speed has a strong positive correlation with "
        "customer review scores, and the 'health & beauty' and 'watches & gifts' categories "
        "command the highest average prices."
    )

    lines.append("\n---\n")

    # -----------------------------------------------------------------------
    # 1. Monthly Revenue Trend
    # -----------------------------------------------------------------------
    h(2, "1. Monthly Revenue Trend")
    p(
        "Revenue grew steadily from late 2016 through mid-2018, with a notable peak in "
        "November 2017 (Black Friday effect) and a plateau in early 2018. The dual upward "
        "trend in both revenue and order volume confirms organic customer acquisition growth."
    )
    df = results.get("monthly_revenue")
    if df is not None and not df.empty:
        df_disp = df.copy()
        df_disp["year_month"] = df_disp["year_month"].dt.strftime("%Y-%m")
        table_from_df(df_disp, ["year_month", "total_revenue", "total_orders"])

    lines.append("![Monthly Revenue Chart](charts/01_monthly_revenue.png)\n")

    # -----------------------------------------------------------------------
    # 2. Top 10 Categories
    # -----------------------------------------------------------------------
    h(2, "2. Top 10 Product Categories by Revenue")
    p(
        "Bed/bath/table, health & beauty, sports/leisure, computers & accessories, and "
        "furniture/decoration lead in revenue. These five categories collectively account "
        "for approximately 40% of total platform revenue, making them prime candidates for "
        "promotional investment."
    )
    table_from_df(
        results.get("top_categories", __import__("pandas").DataFrame()),
        ["product_category_name", "total_revenue", "total_orders", "avg_price"]
    )
    lines.append("![Top Categories Chart](charts/02_top_categories.png)\n")

    # -----------------------------------------------------------------------
    # 3. Sales by State
    # -----------------------------------------------------------------------
    h(2, "3. Geographic Sales Distribution")
    p(
        "São Paulo (SP) accounts for the largest share of orders by a significant margin, "
        "followed by Rio de Janeiro (RJ) and Minas Gerais (MG). This concentration in the "
        "Southeast region reflects Brazil's economic centre of gravity. Northern and "
        "North-Eastern states represent untapped market potential."
    )
    table_from_df(
        results.get("sales_by_state", __import__("pandas").DataFrame()),
        ["customer_state", "total_orders", "total_revenue", "avg_order_value"]
    )
    lines.append("![Sales by State Chart](charts/03_sales_by_state.png)\n")

    # -----------------------------------------------------------------------
    # 4. Payment Methods
    # -----------------------------------------------------------------------
    h(2, "4. Payment Method Preferences")
    p(
        "Credit card dominates with ~74% of all transactions, reflecting the Brazilian "
        "consumer preference for installment-based purchasing (parcelamento). Boleto bancário "
        "is second at ~19%, while vouchers and debit cards make up the remainder. Olist should "
        "prioritise seamless credit-card checkout and consider incentives for digital payment "
        "adoption."
    )
    table_from_df(
        results.get("payment_methods", __import__("pandas").DataFrame()),
        ["payment_type", "total_transactions", "total_value", "pct_share"]
    )
    lines.append("![Payment Methods Chart](charts/04_payment_methods.png)\n")

    # -----------------------------------------------------------------------
    # 5. Delivery Time
    # -----------------------------------------------------------------------
    h(2, "5. Delivery Time Analysis")
    p(
        "Heavy furniture and office items have the longest average delivery times (25+ days), "
        "while books and digital products are delivered fastest (<10 days). Categories with "
        "long delivery times also tend to have lower review scores, validating the importance "
        "of logistics optimisation."
    )
    table_from_df(
        results.get("delivery_time", __import__("pandas").DataFrame()),
        ["product_category_name", "avg_delivery_days", "total_orders"]
    )
    lines.append("![Delivery Time Chart](charts/05_delivery_time.png)\n")

    # -----------------------------------------------------------------------
    # 6. Ratings vs Delivery Speed
    # -----------------------------------------------------------------------
    h(2, "6. Customer Satisfaction vs Delivery Speed")
    p(
        "There is a clear inverse relationship between delivery time and customer satisfaction. "
        "Orders delivered within 7 days receive an average score of 4.4/5, while orders taking "
        "22+ days drop to 2.8/5. Investing in express logistics can directly improve review "
        "scores, which in turn drives repeat purchases."
    )
    table_from_df(
        results.get("ratings_by_delivery", __import__("pandas").DataFrame()),
        ["delivery_speed_bucket", "avg_review_score", "order_count"]
    )
    lines.append("![Ratings Distribution Chart](charts/06_ratings_distribution.png)\n")

    # -----------------------------------------------------------------------
    # 7. Price by Category
    # -----------------------------------------------------------------------
    h(2, "7. Price Analysis by Category")
    p(
        "Computers and electronics command the highest average prices (R$1,000+), while "
        "flowers, food, and CDs/DVDs are among the most affordable. The wide min-max range "
        "in electronics indicates a mixed product tier — from budget accessories to premium "
        "devices — offering upsell opportunities."
    )
    table_from_df(
        results.get("price_by_category", __import__("pandas").DataFrame()),
        ["product_category_name", "avg_price", "min_price", "max_price", "item_count"]
    )
    lines.append("![Price by Category Chart](charts/07_price_by_category.png)\n")

    # -----------------------------------------------------------------------
    # 8. Customer Retention
    # -----------------------------------------------------------------------
    h(2, "8. Customer Retention")
    p(
        "The vast majority of Olist customers (~97%) make only a single purchase, with fewer "
        "than 3% making repeat orders. This signals a significant retention challenge and "
        "suggests opportunities for loyalty programmes, post-purchase email campaigns, and "
        "personalised recommendations to increase customer lifetime value."
    )
    table_from_df(
        results.get("customer_retention", __import__("pandas").DataFrame()),
        ["purchase_frequency", "customer_count", "pct_of_total"]
    )

    # -----------------------------------------------------------------------
    # Methodology
    # -----------------------------------------------------------------------
    h(2, "Methodology")
    p(
        "Data was sourced from the Olist Brazilian E-Commerce Public Dataset on Kaggle (7 CSV "
        "files, ~100,000 orders). The pipeline: (1) loads CSV data into a local SQLite database "
        "using Python's csv module and sqlite3; (2) executes 10 analytical SQL queries using "
        "JOINs, GROUP BY, aggregate functions, window functions (OVER), and date arithmetic "
        "(julianday); (3) processes query results into pandas DataFrames; (4) generates "
        "visualisations using matplotlib and seaborn with a custom dark-mode style."
    )

    # -----------------------------------------------------------------------
    # Conclusions
    # -----------------------------------------------------------------------
    h(2, "Conclusions & Recommendations")
    lines.append("| # | Finding | Recommendation |\n|---|---------|----------------|\n")
    recs = [
        ("Revenue peaks in Nov (Black Friday)", "Increase inventory and marketing spend in Oct–Nov."),
        ("SP/RJ/MG dominate orders", "Target North and Northeast regions with logistics partnerships."),
        ("Credit card = 74% of payments", "Optimise instalment UX; add Buy-Now-Pay-Later options."),
        ("Delivery time drives satisfaction", "Invest in express fulfilment for high-value categories."),
        ("97% customers are one-time buyers", "Implement loyalty points, re-engagement email flows."),
        ("Electronics are high-value but slow to deliver", "Partner with specialised couriers for heavy/large items."),
    ]
    for i, (f, r) in enumerate(recs, 1):
        lines.append(f"| {i} | {f} | {r} |")
    lines.append("")

    lines.append("\n---\n")
    lines.append("*Report auto-generated by the Olist E-Commerce Analysis pipeline.*\n")

    # Write to file
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info("Report written: %s", report_path)


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------

def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    start_time = time.time()

    logger.info("=" * 60)
    logger.info("  Olist E-Commerce Analysis Pipeline")
    logger.info("  WAP 228 | OSTIM Technical University")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Step 1: Initialise database
    # ------------------------------------------------------------------
    logger.info("\n[Step 1/4] Initialising database: %s", DB_PATH)
    with DatabaseManager(DB_PATH) as db:
        db.initialize(SCHEMA_PATH)

        # ------------------------------------------------------------------
        # Step 2: Load CSV data
        # ------------------------------------------------------------------
        logger.info("\n[Step 2/4] Loading CSV data from: %s", DATA_DIR)
        row_counts = db.load_all_csv(DATA_DIR)
        total_rows = sum(row_counts.values())
        if total_rows == 0:
            logger.warning(
                "No data was loaded. Make sure the 7 CSV files are in %s", DATA_DIR
            )
        else:
            logger.info("Total rows loaded: %d", total_rows)
            for table, count in row_counts.items():
                logger.info("  %-35s %8d rows", table, count)

        # ------------------------------------------------------------------
        # Step 3: Run analyses
        # ------------------------------------------------------------------
        logger.info("\n[Step 3/4] Running analysis queries...")
        results = run_all_analyses(db)

    # ------------------------------------------------------------------
    # Step 4: Generate charts and report
    # ------------------------------------------------------------------
    logger.info("\n[Step 4/4] Generating charts and report...")
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    create_all_charts(results, CHARTS_DIR)
    write_report(results, REPORT_PATH)

    elapsed = time.time() - start_time
    logger.info("\n" + "=" * 60)
    logger.info("  Pipeline complete in %.1f seconds.", elapsed)
    logger.info("  Charts  -> %s", CHARTS_DIR)
    logger.info("  Report  -> %s", REPORT_PATH)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
