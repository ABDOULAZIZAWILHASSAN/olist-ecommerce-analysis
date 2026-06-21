"""
database.py
===========
Handles all SQLite database operations for the Olist E-Commerce Analysis:
  - Creating the database and applying the schema
  - Loading raw CSV files into the database tables
  - Providing a reusable connection context manager

Usage:
    from src.database import DatabaseManager
    with DatabaseManager('database/olist.db') as db:
        db.initialize()
        db.load_all_csv('data/raw')
"""

import sqlite3
import csv
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional

# Configure module-level logger
logger = logging.getLogger(__name__)

# Mapping from CSV filename (without extension) to table name
CSV_TABLE_MAP = {
    "olist_customers_dataset":      "customers",
    "olist_orders_dataset":         "orders",
    "olist_order_items_dataset":    "order_items",
    "olist_products_dataset":       "products",
    "olist_sellers_dataset":        "sellers",
    "olist_order_payments_dataset": "order_payments",
    "olist_order_reviews_dataset":  "order_reviews",
}


class DatabaseManager:
    """Manages the SQLite connection and all data-loading operations."""

    def __init__(self, db_path: str | Path):
        """
        Initialise the manager with the path to the SQLite database file.

        Args:
            db_path: Absolute or relative path to the .db file.
                     The file will be created if it does not exist.
        """
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "DatabaseManager":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Open a new connection and enable WAL mode for performance."""
        logger.info("Connecting to database: %s", self.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.execute("PRAGMA journal_mode = WAL;")
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._conn.row_factory = sqlite3.Row

    def close(self) -> None:
        """Commit any pending transaction and close the connection."""
        if self._conn:
            self._conn.commit()
            self._conn.close()
            self._conn = None
            logger.info("Database connection closed.")

    @property
    def conn(self) -> sqlite3.Connection:
        """Return the active connection, raising if not connected."""
        if self._conn is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._conn

    # ------------------------------------------------------------------
    # Schema initialisation
    # ------------------------------------------------------------------

    def initialize(self, schema_path: str | Path = "database/schema.sql") -> None:
        """
        Drop all existing tables and recreate them from the schema file.

        Args:
            schema_path: Path to the SQL DDL file.
        """
        schema_path = Path(schema_path)
        logger.info("Applying schema from: %s", schema_path)

        # Drop tables in reverse dependency order
        drop_order = [
            "order_reviews", "order_payments", "order_items",
            "orders", "sellers", "products", "customers",
        ]
        for table in drop_order:
            self.conn.execute(f"DROP TABLE IF EXISTS {table};")
        self.conn.commit()

        # Create fresh tables
        sql = schema_path.read_text(encoding="utf-8")
        self.conn.executescript(sql)
        logger.info("Schema applied successfully.")

    # ------------------------------------------------------------------
    # CSV loading
    # ------------------------------------------------------------------

    def load_csv(self, csv_path: Path, table_name: str) -> int:
        """
        Load a single CSV file into a database table using batched inserts.

        Strategy:
          1. Read the CSV header to build a parameterised INSERT statement.
          2. Insert rows in batches of 5,000 for performance.
          3. Return the total number of rows inserted.

        Args:
            csv_path:   Path to the .csv file.
            table_name: Target database table name.

        Returns:
            Number of rows successfully inserted.
        """
        logger.info("  Loading %s -> %s", csv_path.name, table_name)
        total_rows = 0
        batch_size = 5_000

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                logger.warning("  Skipping empty file: %s", csv_path.name)
                return 0

            columns = reader.fieldnames
            placeholders = ", ".join("?" * len(columns))
            col_list = ", ".join(columns)
            sql = f"INSERT OR IGNORE INTO {table_name} ({col_list}) VALUES ({placeholders})"

            batch: list[tuple] = []
            for row in reader:
                # Convert empty strings to None (NULL in SQLite)
                values = tuple(v if v != "" else None for v in row.values())
                batch.append(values)
                if len(batch) >= batch_size:
                    self.conn.executemany(sql, batch)
                    total_rows += len(batch)
                    batch = []

            # Insert the remaining rows
            if batch:
                self.conn.executemany(sql, batch)
                total_rows += len(batch)

        self.conn.commit()
        logger.info("  Inserted %d rows into %s.", total_rows, table_name)
        return total_rows

    def load_all_csv(self, data_dir: str | Path) -> dict[str, int]:
        """
        Load all 7 Olist CSV files from a directory into their tables.

        Loading order respects foreign key dependencies:
          customers -> orders -> order_items, order_payments, order_reviews
          products  -> order_items
          sellers   -> order_items

        Args:
            data_dir: Directory containing the raw CSV files.

        Returns:
            Dictionary mapping table_name -> rows_inserted.
        """
        data_dir = Path(data_dir)
        # Load in FK-safe order
        load_order = [
            "olist_customers_dataset",
            "olist_products_dataset",
            "olist_sellers_dataset",
            "olist_orders_dataset",
            "olist_order_items_dataset",
            "olist_order_payments_dataset",
            "olist_order_reviews_dataset",
        ]

        results: dict[str, int] = {}
        for stem in load_order:
            table = CSV_TABLE_MAP[stem]
            csv_path = data_dir / f"{stem}.csv"
            if not csv_path.exists():
                logger.warning("CSV not found, skipping: %s", csv_path)
                results[table] = 0
                continue
            results[table] = self.load_csv(csv_path, table)

        return results

    # ------------------------------------------------------------------
    # Query helper
    # ------------------------------------------------------------------

    def execute_query(self, sql: str) -> list[dict]:
        """
        Execute a SELECT query and return results as a list of dicts.

        Args:
            sql: SQL SELECT statement.

        Returns:
            List of row dictionaries (column_name -> value).
        """
        cursor = self.conn.execute(sql)
        columns = [d[0] for d in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


@contextmanager
def get_connection(db_path: str | Path):
    """
    Context manager that yields an open DatabaseManager.

    Example:
        with get_connection('database/olist.db') as db:
            results = db.execute_query('SELECT COUNT(*) FROM orders')
    """
    manager = DatabaseManager(db_path)
    manager.connect()
    try:
        yield manager
    finally:
        manager.close()
