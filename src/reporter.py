from pathlib import Path
from typing import Dict, Any

import matplotlib.pyplot as plt
import pandas as pd


def load_database(csv_path: Path) -> pd.DataFrame:
    """
    Load and clean the consolidated database CSV.

    - Parses issue_date as datetime (dropping rows with invalid dates).
    - Ensures total_amount is numeric (dropping rows that cannot be parsed).
    - Returns a cleaned DataFrame.
    """
    if not csv_path.exists():
        print(f"Database CSV not found at {csv_path}")
        return pd.DataFrame()

    df = pd.read_csv(csv_path)
    if df.empty:
        return df

    # Parse dates
    df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce")
    df = df.dropna(subset=["issue_date"])

    # Ensure numeric total_amount
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")
    df = df.dropna(subset=["total_amount"])

    return df


def _filter_currency(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Filter dataframe to a single currency for plotting/stats if needed.

    Returns dict with:
    - df: filtered DataFrame
    - currency: selected currency (or None)
    - currencies: list of all currencies present
    - multi_currency: bool flag
    """
    result: Dict[str, Any] = {
        "df": df,
        "currency": None,
        "currencies": [],
        "multi_currency": False,
    }

    if df.empty or "currency" not in df.columns:
        return result

    currencies = sorted(df["currency"].dropna().unique().tolist())
    result["currencies"] = currencies

    if not currencies:
        return result

    if len(currencies) == 1:
        result["currency"] = currencies[0]
        return result

    # Multiple currencies: pick the most common for MVP
    mode_series = df["currency"].mode()
    if not mode_series.empty:
        main_currency = mode_series.iloc[0]
        filtered = df[df["currency"] == main_currency].copy()
    else:
        main_currency = currencies[0]
        filtered = df[df["currency"] == main_currency].copy()

    result.update(
        {
            "df": filtered,
            "currency": main_currency,
            "multi_currency": True,
        }
    )
    return result


def compute_monthly_spend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute monthly total spend from a cleaned DataFrame.

    Returns a DataFrame with columns:
    - month (Period[M])
    - total_amount
    """
    if df.empty:
        return pd.DataFrame(columns=["month", "total_amount"])

    df = df.copy()
    df["month"] = df["issue_date"].dt.to_period("M")
    monthly = (
        df.groupby("month", as_index=False)["total_amount"]
        .sum()
        .sort_values("month")
    )
    return monthly


def compute_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute high-level stats for the report.
    """
    stats: Dict[str, Any] = {"has_data": not df.empty}

    if df.empty:
        return stats

    # Currency handling
    currency_info = _filter_currency(df)
    filtered_df = currency_info["df"]

    stats["currency"] = currency_info["currency"]
    stats["currencies"] = currency_info["currencies"]
    stats["multi_currency"] = currency_info["multi_currency"]

    if filtered_df.empty:
        stats["has_data"] = False
        return stats

    # Period covered
    start_date = filtered_df["issue_date"].min()
    end_date = filtered_df["issue_date"].max()

    stats["start_date"] = start_date.date().isoformat()
    stats["end_date"] = end_date.date().isoformat()

    # Total spend
    total_spend = float(filtered_df["total_amount"].sum())
    stats["total_spend"] = total_spend

    # Monthly stats
    monthly = compute_monthly_spend(filtered_df)
    stats["average_monthly_spend"] = (
        float(monthly["total_amount"].mean()) if not monthly.empty else 0.0
    )

    if not monthly.empty:
        # month is a Period, convert to string for readability
        monthly["month_str"] = monthly["month"].astype(str)
        max_row = monthly.loc[monthly["total_amount"].idxmax()]
        min_row = monthly.loc[monthly["total_amount"].idxmin()]
        stats["max_month"] = {
            "month": str(max_row["month"]),
            "total_amount": float(max_row["total_amount"]),
        }
        stats["min_month"] = {
            "month": str(min_row["month"]),
            "total_amount": float(min_row["total_amount"]),
        }
    else:
        stats["max_month"] = None
        stats["min_month"] = None

    # Top vendors
    if "issuer_name" in filtered_df.columns:
        vendor_totals = (
            filtered_df.groupby("issuer_name", as_index=False)["total_amount"]
            .sum()
            .sort_values("total_amount", ascending=False)
        )
        top_vendors = vendor_totals.head(5)
        stats["top_vendors"] = [
            {
                "issuer_name": row["issuer_name"],
                "total_amount": float(row["total_amount"]),
            }
            for _, row in top_vendors.iterrows()
        ]
    else:
        stats["top_vendors"] = []

    # Biggest invoices
    cols = [
        col
        for col in ["doc_number", "issuer_name", "issue_date", "total_amount"]
        if col in filtered_df.columns
    ]
    largest = (
        filtered_df[cols]
        .sort_values("total_amount", ascending=False)
        .head(5)
    )
    biggest = []
    for _, row in largest.iterrows():
        item = {
            "doc_number": row.get("doc_number"),
            "issuer_name": row.get("issuer_name"),
            "issue_date": (
                row["issue_date"].date().isoformat()
                if "issue_date" in largest.columns
                else None
            ),
            "total_amount": float(row["total_amount"]),
        }
        biggest.append(item)
    stats["biggest_invoices"] = biggest

    return stats


def plot_monthly_spend(monthly_df: pd.DataFrame, output_path: Path) -> bool:
    """
    Plot monthly spend as a line chart.

    Returns True if a plot was generated, False otherwise.
    """
    if monthly_df.empty or len(monthly_df) < 2:
        print("Not enough data to generate monthly spend plot.")
        return False

    # Prepare data
    x = monthly_df["month"].astype(str)
    y = monthly_df["total_amount"]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 4))
    plt.plot(x, y, marker="o")
    plt.title("Monthly Spend")
    plt.xlabel("Month")
    plt.ylabel("Total Spend")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    print(f"Saved monthly spend plot to {output_path}")
    return True


def build_markdown_report(
    stats: Dict[str, Any],
    monthly_df: pd.DataFrame,
    reports_dir: Path,
    plot_created: bool,
) -> None:
    """
    Build a Markdown report summarizing spending.
    """
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / "spending_report.md"

    if not stats.get("has_data"):
        content = (
            "# Spending Report\n\n"
            "Not enough valid data in the database to generate a report yet.\n"
        )
        output_path.write_text(content, encoding="utf-8")
        print(f"Wrote minimal report to {output_path}")
        return

    currency = stats.get("currency")
    currencies = stats.get("currencies", [])
    multi_currency = stats.get("multi_currency", False)

    currency_note = ""
    if currency:
        currency_note = f"All amounts below are shown in **{currency}**."
        if multi_currency:
            currency_note += (
                f" Original data contained multiple currencies {currencies}; "
                f"for this MVP, only the most common currency ({currency}) is shown."
            )

    lines = []
    lines.append("# Spending Report")
    lines.append("")

    # Overview
    lines.append("## Overview")
    lines.append("")
    lines.append(
        f"- **Period**: {stats.get('start_date', '?')} to {stats.get('end_date', '?')}"
    )
    lines.append(
        f"- **Total spend**: {stats.get('total_spend', 0.0):.2f}"
    )
    lines.append(
        f"- **Average monthly spend**: {stats.get('average_monthly_spend', 0.0):.2f}"
    )
    if currency_note:
        lines.append(f"- {currency_note}")
    lines.append("")

    # Monthly trend
    lines.append("## Monthly Trend")
    lines.append("")
    max_month = stats.get("max_month")
    min_month = stats.get("min_month")

    if max_month and min_month:
        lines.append(
            f"- **Highest month**: {max_month['month']} "
            f"with {max_month['total_amount']:.2f}"
        )
        lines.append(
            f"- **Lowest month**: {min_month['month']} "
            f"with {min_month['total_amount']:.2f}"
        )
    else:
        lines.append("- Not enough data to compute monthly highs/lows.")

    if plot_created:
        lines.append("")
        lines.append("![Monthly Spend](monthly_spend.png)")
    lines.append("")

    # Top vendors
    lines.append("## Top Vendors")
    lines.append("")
    top_vendors = stats.get("top_vendors", [])
    if not top_vendors:
        lines.append("No vendor information available.")
    else:
        for vendor in top_vendors:
            lines.append(
                f"- **{vendor['issuer_name']}**: "
                f"{vendor['total_amount']:.2f}"
            )
    lines.append("")

    # Biggest invoices
    lines.append("## Biggest Invoices")
    lines.append("")
    biggest = stats.get("biggest_invoices", [])
    if not biggest:
        lines.append("No invoice information available.")
    else:
        for inv in biggest:
            parts = []
            if inv.get("doc_number"):
                parts.append(f"**{inv['doc_number']}**")
            if inv.get("issuer_name"):
                parts.append(f"from {inv['issuer_name']}")
            if inv.get("issue_date"):
                parts.append(f"on {inv['issue_date']}")
            parts.append(f"amount: {inv['total_amount']:.2f}")
            lines.append("- " + ", ".join(parts))
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote report to {output_path}")


def run_reporter(csv_path: Path, reports_dir: Path) -> None:
    """
    Orchestrate loading, computing, plotting, and report writing.
    """
    df = load_database(csv_path)
    stats = compute_summary_stats(df)

    # Use the filtered DataFrame for monthly spend (based on currency selection)
    if stats.get("has_data"):
        # We recompute filtered df via _filter_currency to stay consistent with stats
        currency_info = _filter_currency(df)
        filtered_df = currency_info["df"]
        monthly = compute_monthly_spend(filtered_df)
    else:
        monthly = pd.DataFrame(columns=["month", "total_amount"])

    plot_path = reports_dir / "monthly_spend.png"
    plot_created = plot_monthly_spend(monthly, plot_path)

    build_markdown_report(stats, monthly, reports_dir, plot_created)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate spending report from database CSV")
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("data/processed/database.csv"),
        help="Path to the consolidated database CSV",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="Directory where the report and plots will be saved",
    )
    args = parser.parse_args()

    run_reporter(args.csv, args.reports_dir)


