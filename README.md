# Olist E-Commerce Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.9-11557C)](https://matplotlib.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

An end-to-end data analysis pipeline for the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), covering 100,000+ real orders placed on the platform between 2016 and 2018.

---

## 📊 Project Overview

This project demonstrates:

| Skill | Implementation |
|-------|---------------|
| **SQL** | 10 complex queries with multi-table JOINs, GROUP BY, window functions, date arithmetic |
| **Python** | Modular pipeline: database.py → analysis.py → visualizations.py → main.py |
| **Data Analysis** | Revenue trends, geographic segmentation, customer satisfaction, retention |
| **Visualization** | 7 publication-quality charts using matplotlib + seaborn |
| **GitHub** | Meaningful commit history, clean structure, comprehensive README |

---

## 📁 Repository Structure

```
olist-ecommerce-analysis/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore                   # Excludes venv, DB, raw CSVs
├── database/
│   ├── schema.sql               # DDL for 7 tables + indexes
│   └── queries.sql              # 10 documented analysis queries
├── src/
│   ├── main.py                  # Pipeline orchestrator — run this
│   ├── database.py              # SQLite connection & CSV loading
│   ├── analysis.py              # SQL query execution → DataFrames
│   └── visualizations.py        # 7 chart generators
├── data/
│   └── raw/                     # Place the 7 Kaggle CSV files here
└── output/
    └── charts/                  # Generated PNG visualizations (7 files)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Kaggle account (to download the dataset)

### Step 1: Clone the Repository

```bash
git clone https://github.com/ABDOULAZIZAWILHASSAN/olist-ecommerce-analysis.git
cd olist-ecommerce-analysis
```

### Step 2: Create a Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Download the Dataset

1. Go to [https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
2. Download and extract the ZIP file
3. Place all 7 CSV files into `data/raw/`:

```
data/raw/
├── olist_customers_dataset.csv
├── olist_orders_dataset.csv
├── olist_order_items_dataset.csv
├── olist_products_dataset.csv
├── olist_sellers_dataset.csv
├── olist_order_payments_dataset.csv
└── olist_order_reviews_dataset.csv
```

### Step 4: Run the Analysis Pipeline

```bash
python src/main.py
```

**That's it.** The pipeline will:
1. ✅ Create the SQLite database (`database/olist.db`)
2. ✅ Load all 7 CSV files into structured tables
3. ✅ Execute all 10 analysis queries
4. ✅ Generate 7 professional charts in `output/charts/`

---

## 📈 Generated Outputs

### Charts (`output/charts/`)

| File | Description |
|------|-------------|
| `01_monthly_revenue.png` | Dual-axis line chart: revenue & order volume over time |
| `02_top_categories.png` | Top 10 product categories by total revenue |
| `03_sales_by_state.png` | Order distribution across Brazilian states |
| `04_payment_methods.png` | Payment type breakdown (donut chart) |
| `05_delivery_time.png` | Average delivery days by product category |
| `06_ratings_distribution.png` | Customer satisfaction score vs delivery speed |
| `07_price_by_category.png` | Avg/min/max price analysis by category |

---

## 🔍 SQL Analysis Queries

All 10 queries are in `database/queries.sql` with inline documentation:

| # | Query | SQL Features Used |
|---|-------|------------------|
| 1 | Monthly Revenue Trend | `strftime`, `SUM`, `COUNT DISTINCT`, `GROUP BY` |
| 2 | Top 10 Product Categories | Multi-table `JOIN`, `AVG`, `ORDER BY`, `LIMIT` |
| 3 | Sales by State | 3-way `JOIN`, geographic aggregation |
| 4 | Payment Method Usage | Window function: `SUM(...) OVER ()` |
| 5 | Delivery Time by Category | `julianday` date arithmetic, `HAVING` |
| 6 | Satisfaction vs Delivery Speed | `CASE WHEN` bucketing, `AVG` |
| 7 | Top Seller Performance | `LEFT JOIN`, multi-column `GROUP BY` |
| 8 | Seasonal Patterns | `CASE WHEN` month mapping |
| 9 | Customer Retention | Subquery, window function `OVER ()` |
| 10 | Price Analysis | Subquery scalar, `MIN`, `MAX`, `AVG` |

---

## 🧱 Architecture

```
[7 CSV Files] ──load──► [SQLite DB] ──query──► [DataFrames] ──► [Charts + Report]
   data/raw/            olist.db             pandas              output/
                        database.py          analysis.py         visualizations.py
                                                                 main.py (orchestrator)
```

**Technology Stack:**

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.8+ | Pipeline language |
| SQLite | Built-in | Lightweight relational database |
| sqlite3 | Built-in | Python DB-API 2.0 adapter |
| Pandas | 2.2 | Data manipulation & DataFrame operations |
| Matplotlib | 3.9 | Chart rendering |
| Seaborn | 0.13 | Statistical visualization styling |

---

## 💡 Key Insights

1. **São Paulo dominates** — SP accounts for ~42% of all orders; North/Northeast regions are underserved.
2. **Credit card is king** — 74% of transactions use credit card, with high average installment counts.
3. **Delivery time = Satisfaction** — Orders under 7 days avg 4.4/5 stars; 22+ days drops to 2.8/5.
4. **November spike** — Black Friday creates a clear revenue peak every year.
5. **97% one-time buyers** — Massive retention opportunity through loyalty initiatives.
6. **Electronics & computers** — Highest unit prices but also longest delivery times.

---

## 🧠 Project Development & Reflection

### Development Process
The project was developed using a structured data engineering approach:
1. **Data Ingestion**: Raw Kaggle CSVs were downloaded and loaded into pandas DataFrames.
2. **Database Architecture**: An SQLite relational database was designed with strict schemas, foreign keys, and indexes for optimized querying.
3. **ETL Pipeline**: Python scripts were written to clean, format, and load the raw data into the SQLite database.
4. **Analysis Execution**: 10 complex SQL queries were written and executed via Python's `sqlite3` adapter to extract business metrics.
5. **Visualization & Reporting**: Matplotlib and Seaborn were used to translate the queried data into professional charts and a Markdown report.
6. **Web Dashboard**: An enterprise-grade, glassmorphism-themed HTML dashboard was designed to showcase the final charts and insights.

### Challenging Parts
- **Data Integrity**: Handling missing values and ensuring referential integrity when inserting 100,000+ rows across 7 interconnected tables.
- **Complex Aggregations**: Writing SQL window functions and subqueries to calculate complex metrics like Customer Retention without crashing the lightweight SQLite database.
- **Data Translation**: The original dataset featured Portuguese category names, requiring a mapping dictionary in Python to translate them to English for professional presentation.

### What Was Learned
- How to architect and orchestrate an automated, modular data pipeline from raw file ingestion to final HTML rendering.
- Advanced SQL techniques for time-series analysis and cohort behavior.
- Best practices for presenting data visually, ensuring charts are not just accurate, but also aesthetically engaging and easy for stakeholders to understand.

### Role of the Technology Stack
- **Python**: Acted as the core orchestrator. It handled file I/O, managed the database connection, executed the SQL scripts, manipulated data via Pandas, and generated the visualizations.
- **SQL (SQLite)**: Served as the analytical engine. It was responsible for joining massive datasets, filtering, aggregating, and returning clean analytical views to Python, proving that database-level transformations are much more efficient than memory-level filtering.
- **GitHub**: Provided version control and project hosting. It allowed for safe, incremental feature development (via commits), tracked history, and served as the final public portfolio host to share the project with others.

---

## 📚 Resources

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/index.html)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Olist Dataset on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

## 📄 License

This project is licensed under the **MIT License**.


