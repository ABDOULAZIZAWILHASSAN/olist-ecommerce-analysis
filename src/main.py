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

Run from the project root:
    python src/main.py

Dependencies:
    pip install -r requirements.txt
"""

import sys
import time
import logging
from pathlib import Path

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
# Pipeline entry point
# ---------------------------------------------------------------------------

def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    start_time = time.time()

    logger.info("=" * 60)
    logger.info("  Olist E-Commerce Analysis Pipeline")
    logger.info("=" * 60)

    # ------------------------------------------------------------------
    # Step 1: Initialise database
    # ------------------------------------------------------------------
    logger.info("\n[Step 1/3] Initialising database: %s", DB_PATH)
    with DatabaseManager(DB_PATH) as db:
        db.initialize(SCHEMA_PATH)

        # ------------------------------------------------------------------
        # Step 2: Load CSV data
        # ------------------------------------------------------------------
        logger.info("\n[Step 2/3] Loading CSV data from: %s", DATA_DIR)
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
        logger.info("\n[Step 3/3] Running analysis queries...")
        results = run_all_analyses(db)

    # ------------------------------------------------------------------
    # Generate charts
    # ------------------------------------------------------------------
    logger.info("\nGenerating charts...")
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    create_all_charts(results, CHARTS_DIR)

    elapsed = time.time() - start_time
    logger.info("\n" + "=" * 60)
    logger.info("  Pipeline complete in %.1f seconds.", elapsed)
    logger.info("  Charts  -> %s", CHARTS_DIR)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
