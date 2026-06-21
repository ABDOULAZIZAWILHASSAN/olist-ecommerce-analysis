"""
visualizations.py
=================
Creates 7 professional publication-quality charts from the Olist
analysis DataFrames and saves them as 300-dpi PNG files.

Chart catalogue:
  01_monthly_revenue.png      — dual-axis line chart (revenue + orders)
  02_top_categories.png       — horizontal bar chart
  03_sales_by_state.png       — vertical bar chart (top 15 states)
  04_payment_methods.png      — donut pie chart
  05_delivery_time.png        — horizontal bar chart
  06_ratings_distribution.png — grouped bar chart (score vs delivery speed)
  07_price_by_category.png    — horizontal bar chart with error bands

Usage:
    from src.visualizations import create_all_charts
    create_all_charts(results, output_dir=Path('output/charts'))
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib
matplotlib.use("Agg")   # Non-interactive backend — no GUI window needed
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global style
# ---------------------------------------------------------------------------

# Brand-consistent colour palette
PALETTE_MAIN   = "#2C7BE5"
PALETTE_ACCENT = "#E63757"
PALETTE_GOLD   = "#F6C90E"
PALETTE_GREEN  = "#00B887"
BG_COLOR       = "#0f1117"
TEXT_COLOR      = "#E0E0E0"
GRID_COLOR      = "#2a2d3a"

_COLORS = [
    "#2C7BE5", "#E63757", "#00B887", "#F6C90E",
    "#9B59B6", "#1ABC9C", "#E67E22", "#3498DB",
    "#E91E63", "#FF5722",
]


def _apply_dark_style() -> None:
    """Apply a cohesive dark-mode stylesheet to all subsequent figures."""
    plt.rcParams.update({
        "figure.facecolor":  BG_COLOR,
        "axes.facecolor":    "#181b26",
        "axes.edgecolor":    GRID_COLOR,
        "axes.labelcolor":   TEXT_COLOR,
        "axes.titlecolor":   TEXT_COLOR,
        "axes.titlesize":    14,
        "axes.titleweight":  "bold",
        "axes.labelsize":    11,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "xtick.color":       TEXT_COLOR,
        "ytick.color":       TEXT_COLOR,
        "xtick.labelsize":   9,
        "ytick.labelsize":   9,
        "grid.color":        GRID_COLOR,
        "grid.linestyle":    "--",
        "grid.linewidth":    0.6,
        "legend.facecolor":  "#1e2130",
        "legend.edgecolor":  GRID_COLOR,
        "legend.labelcolor": TEXT_COLOR,
        "text.color":        TEXT_COLOR,
        "figure.dpi":        120,
        "savefig.dpi":       300,
        "savefig.bbox":      "tight",
        "savefig.facecolor": BG_COLOR,
        "font.family":       "DejaVu Sans",
    })


def _save(fig: plt.Figure, path: Path) -> None:
    """Save a figure and log the result."""
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    logger.info("  Saved chart: %s", path.name)


# ---------------------------------------------------------------------------
# Chart functions
# ---------------------------------------------------------------------------

def create_monthly_revenue(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Chart 01 — Monthly Revenue Trend.
    Dual-axis line chart: revenue (left axis) and order count (right axis).
    """
    if df.empty:
        logger.warning("No data for monthly revenue chart.")
        return

    _apply_dark_style()
    fig, ax1 = plt.subplots(figsize=(14, 6))
    fig.suptitle("Monthly Revenue & Order Volume (2016–2018)",
                 fontsize=16, fontweight="bold", color=TEXT_COLOR, y=1.01)

    # Revenue line
    ax1.fill_between(df["year_month"], df["total_revenue"],
                     alpha=0.25, color=PALETTE_MAIN)
    ax1.plot(df["year_month"], df["total_revenue"],
             color=PALETTE_MAIN, linewidth=2.5, label="Revenue (BRL)", zorder=3)
    ax1.set_xlabel("Month", fontsize=11)
    ax1.set_ylabel("Total Revenue (BRL)", color=PALETTE_MAIN, fontsize=11)
    ax1.tick_params(axis="y", labelcolor=PALETTE_MAIN)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"R${x/1_000:.0f}k"))
    ax1.grid(True, axis="y")

    # Order count line on secondary axis
    ax2 = ax1.twinx()
    ax2.plot(df["year_month"], df["total_orders"],
             color=PALETTE_ACCENT, linewidth=2, linestyle="--",
             label="Orders", zorder=3)
    ax2.set_ylabel("Number of Orders", color=PALETTE_ACCENT, fontsize=11)
    ax2.tick_params(axis="y", labelcolor=PALETTE_ACCENT)
    ax2.set_facecolor("none")
    for spine in ax2.spines.values():
        spine.set_visible(False)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.xticks(rotation=45, ha="right")
    _save(fig, output_dir / "01_monthly_revenue.png")


def create_top_categories(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Chart 02 — Top 10 Product Categories by Revenue.
    Horizontal bar chart sorted by descending revenue.
    """
    if df.empty:
        logger.warning("No data for top categories chart.")
        return

    _apply_dark_style()
    df_plot = df.sort_values("total_revenue")
    # Prettify category names: replace underscores, title-case
    df_plot = df_plot.copy()
    df_plot["label"] = df_plot["product_category_name"].str.replace("_", " ").str.title()

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(
        df_plot["label"], df_plot["total_revenue"],
        color=[_COLORS[i % len(_COLORS)] for i in range(len(df_plot))],
        height=0.7, edgecolor="none"
    )
    # Value labels
    for bar in bars:
        w = bar.get_width()
        ax.text(w * 1.01, bar.get_y() + bar.get_height() / 2,
                f"R${w/1_000:.0f}k", va="center", ha="left",
                fontsize=9, color=TEXT_COLOR)

    ax.set_title("Top 10 Product Categories by Revenue", fontsize=14,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Total Revenue (BRL)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"R${x/1_000:.0f}k"))
    ax.grid(True, axis="x", alpha=0.4)
    ax.set_axisbelow(True)
    _save(fig, output_dir / "02_top_categories.png")


def create_sales_by_state(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Chart 03 — Sales Distribution by Brazilian State (top 15).
    Vertical bar chart coloured by order volume intensity.
    """
    if df.empty:
        logger.warning("No data for sales by state chart.")
        return

    _apply_dark_style()
    df_plot = df.head(15)

    fig, ax = plt.subplots(figsize=(13, 6))
    norm = plt.Normalize(df_plot["total_orders"].min(), df_plot["total_orders"].max())
    cmap = plt.cm.Blues
    colors = [cmap(norm(v) * 0.7 + 0.3) for v in df_plot["total_orders"]]

    bars = ax.bar(
        df_plot["customer_state"], df_plot["total_orders"],
        color=colors, edgecolor="none", width=0.7
    )
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h * 1.01,
                f"{h:,.0f}", ha="center", va="bottom", fontsize=8, color=TEXT_COLOR)

    ax.set_title("Top 15 States by Number of Orders", fontsize=14,
                 fontweight="bold", pad=12)
    ax.set_xlabel("Brazilian State")
    ax.set_ylabel("Number of Orders")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.grid(True, axis="y", alpha=0.4)
    ax.set_axisbelow(True)
    _save(fig, output_dir / "03_sales_by_state.png")


def create_payment_methods(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Chart 04 — Payment Method Breakdown.
    Donut pie chart showing percentage share of each payment type.
    """
    if df.empty:
        logger.warning("No data for payment methods chart.")
        return

    _apply_dark_style()
    labels = df["payment_type"].str.replace("_", " ").str.title()
    sizes  = df["pct_share"]
    colors = _COLORS[:len(df)]

    fig, ax = plt.subplots(figsize=(9, 7))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"width": 0.55, "edgecolor": BG_COLOR, "linewidth": 2},
        textprops={"color": TEXT_COLOR, "fontsize": 11},
        pctdistance=0.80
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color(BG_COLOR)
        at.set_fontweight("bold")

    # Centre annotation
    ax.text(0, 0, "Payment\nMethods", ha="center", va="center",
            fontsize=13, fontweight="bold", color=TEXT_COLOR)
    ax.set_title("Payment Method Distribution", fontsize=14,
                 fontweight="bold", pad=16)
    _save(fig, output_dir / "04_payment_methods.png")


def create_delivery_time(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Chart 05 — Avg Delivery Time by Product Category (top 15 slowest).
    Horizontal bar chart.
    """
    if df.empty:
        logger.warning("No data for delivery time chart.")
        return

    _apply_dark_style()
    df_plot = df.sort_values("avg_delivery_days").copy()
    df_plot["label"] = df_plot["product_category_name"].str.replace("_", " ").str.title()

    fig, ax = plt.subplots(figsize=(12, 7))
    norm = plt.Normalize(df_plot["avg_delivery_days"].min(), df_plot["avg_delivery_days"].max())
    cmap = plt.cm.RdYlGn_r
    colors = [cmap(norm(v)) for v in df_plot["avg_delivery_days"]]

    bars = ax.barh(df_plot["label"], df_plot["avg_delivery_days"],
                   color=colors, height=0.7, edgecolor="none")
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{w:.1f}d", va="center", ha="left", fontsize=9, color=TEXT_COLOR)

    ax.set_title("Average Delivery Time by Product Category (Top 15 Slowest)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Average Days from Purchase to Delivery")
    ax.grid(True, axis="x", alpha=0.4)
    ax.set_axisbelow(True)
    _save(fig, output_dir / "05_delivery_time.png")


def create_ratings_distribution(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Chart 06 — Customer Satisfaction vs Delivery Speed.
    Grouped bar chart: avg review score per delivery speed bucket.
    """
    if df.empty:
        logger.warning("No data for ratings chart.")
        return

    _apply_dark_style()
    # Sort by delivery speed (fast -> very slow)
    speed_order = ["0-7 days (Fast)", "8-14 days (Normal)",
                   "15-21 days (Slow)", "22+ days (Very Slow)"]
    df_plot = df.set_index("delivery_speed_bucket").reindex(speed_order).dropna()

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [PALETTE_GREEN, PALETTE_MAIN, PALETTE_GOLD, PALETTE_ACCENT][:len(df_plot)]
    bars = ax.bar(
        df_plot.index, df_plot["avg_review_score"],
        color=colors, width=0.55, edgecolor="none"
    )
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.02,
                f"{h:.2f}★", ha="center", va="bottom", fontsize=11,
                fontweight="bold", color=TEXT_COLOR)

    ax.set_ylim(0, 5.5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_title("Customer Review Score vs Delivery Speed",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Delivery Speed Bucket")
    ax.set_ylabel("Average Review Score (out of 5)")
    ax.grid(True, axis="y", alpha=0.4)
    ax.set_axisbelow(True)

    # Annotate order counts below bars
    for i, (_, row) in enumerate(df_plot.iterrows()):
        ax.text(i, 0.1, f"n={int(row['order_count']):,}",
                ha="center", va="bottom", fontsize=8, color="#888888")

    _save(fig, output_dir / "06_ratings_distribution.png")


def create_price_by_category(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Chart 07 — Price Analysis by Product Category (top 15 by avg price).
    Horizontal bar chart showing average price with min/max range marker.
    """
    if df.empty:
        logger.warning("No data for price chart.")
        return

    _apply_dark_style()
    df_plot = df.sort_values("avg_price").copy()
    df_plot["label"] = df_plot["product_category_name"].str.replace("_", " ").str.title()

    fig, ax = plt.subplots(figsize=(12, 8))
    y_pos = np.arange(len(df_plot))

    # Range bars (min to max)
    ax.barh(y_pos, df_plot["max_price"] - df_plot["min_price"],
            left=df_plot["min_price"],
            color=PALETTE_MAIN, alpha=0.2, height=0.5, label="Min–Max Range")
    # Average bars
    ax.barh(y_pos, df_plot["avg_price"], color=PALETTE_MAIN,
            height=0.35, label="Avg Price", zorder=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(df_plot["label"], fontsize=9)

    for i, row in enumerate(df_plot.itertuples()):
        ax.text(row.avg_price + 5, i, f"R${row.avg_price:.0f}",
                va="center", ha="left", fontsize=8, color=TEXT_COLOR)

    ax.set_title("Price Analysis by Product Category (Avg + Min/Max Range)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Price (BRL)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"R${x:,.0f}"))
    ax.grid(True, axis="x", alpha=0.4)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right")
    _save(fig, output_dir / "07_price_by_category.png")


# ---------------------------------------------------------------------------
# Master chart generator
# ---------------------------------------------------------------------------

def create_all_charts(results: dict, output_dir: Path | str) -> None:
    """
    Generate all 7 charts from the analysis results dictionary.

    Args:
        results:    Dict of DataFrames returned by run_all_analyses().
        output_dir: Directory where PNG files will be saved.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Generating charts into: %s", output_dir)

    create_monthly_revenue(results.get("monthly_revenue", pd.DataFrame()), output_dir)
    create_top_categories(results.get("top_categories", pd.DataFrame()), output_dir)
    create_sales_by_state(results.get("sales_by_state", pd.DataFrame()), output_dir)
    create_payment_methods(results.get("payment_methods", pd.DataFrame()), output_dir)
    create_delivery_time(results.get("delivery_time", pd.DataFrame()), output_dir)
    create_ratings_distribution(results.get("ratings_by_delivery", pd.DataFrame()), output_dir)
    create_price_by_category(results.get("price_by_category", pd.DataFrame()), output_dir)

    logger.info("All 7 charts generated successfully.")
