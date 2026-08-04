"""
main.py

Main entry point for the Python BI Reporting and Decision Support Module.

Run:
    python main.py
    python main.py --region Bursa
    python main.py --year 2024
    python main.py --segment SMB
    python main.py --product "CRM Enterprise"

Outputs:
    reports/dashboard.html
    reports/kpi_report.xlsx
    reports/charts/*.png
    reports/charts/*.html
"""

import argparse

from modules.decision_support import analyze, format_report
from modules.excel_exporter import generate_excel_report
from modules.forecast import compute_revenue_forecast
from modules.kpi_engine import compute_all_kpis
from modules.report_generator import generate_html_report
from modules.segment_analysis import compute_segment_analysis
from modules.visualizer import generate_bilingual_charts


SEPARATOR_WIDTH = 55
FORECAST_MONTHS = 3


def parse_arguments() -> argparse.Namespace:
    """Parse optional command-line filters."""

    parser = argparse.ArgumentParser(
        description=(
            "Generate filtered BI reports from the CRM datasets."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--region",
        type=str,
        help=(
            "Analyze one region using a case-insensitive exact match, "
            "for example: --region Bursa"
        ),
    )

    parser.add_argument(
        "--year",
        type=int,
        help=(
            "Analyze orders from one calendar year, "
            "for example: --year 2024"
        ),
    )

    parser.add_argument(
        "--segment",
        type=str,
        help=(
            "Analyze one customer segment, "
            "for example: --segment SMB"
        ),
    )

    parser.add_argument(
        "--product",
        type=str,
        help=(
            "Analyze one product, for example: "
            '--product "CRM Enterprise"'
        ),
    )

    return parser.parse_args()


def print_header() -> None:
    """Print the application header."""

    print("=" * SEPARATOR_WIDTH)
    print("  Python BI Reporting & Decision Support Module")
    print("=" * SEPARATOR_WIDTH)


def print_filter_summary(
    filters: dict,
    total_orders: int,
    total_customers: int,
) -> None:
    """Print active CLI filters and resulting dataset size."""

    print("\n🔎 Analysis Scope")
    print("-" * SEPARATOR_WIDTH)

    if filters:
        for name, value in filters.items():
            print(
                f"   {name.replace('_', ' ').title():18}: "
                f"{value}"
            )
    else:
        print("   Filters           : None — full dataset")

    print(
        f"   Matching Orders   : "
        f"{total_orders:,}"
    )
    print(
        f"   Matching Customers: "
        f"{total_customers:,}"
    )


def print_kpi_summary(kpis: dict) -> None:
    """Print the main KPI values to the console."""

    revenue = kpis["revenue"]
    sales = kpis["sales"]
    trends = kpis["trends"]

    print("\n📐 KPI Summary")
    print("-" * SEPARATOR_WIDTH)

    print(
        f"   Total Revenue   : "
        f"${revenue['total_revenue']:,.2f}"
    )
    print(
        f"   Avg Order Value : "
        f"${revenue['avg_order_value']:,.2f}"
    )
    print(
        f"   MoM Growth      : "
        f"{revenue['mom_growth_pct']:+.1f}%"
    )
    print(
        f"   Win Rate        : "
        f"{sales['win_rate_pct']}%"
    )
    print(
        f"   Trend           : "
        f"{trends['trend_direction']}"
    )


def print_segment_summary(
    segment_analysis: dict,
) -> None:
    """Print the customer-segment analysis summary."""

    summary = segment_analysis["summary"]

    print("\nSegment Analysis Summary")
    print("-" * SEPARATOR_WIDTH)

    print(
        "   Highest Revenue Segment             : "
        f"{summary['highest_revenue_segment']}"
    )
    print(
        "   Highest Revenue per Customer Segment: "
        f"{summary['highest_revenue_per_customer_segment']}"
    )
    print(
        "   Highest Win Rate Segment            : "
        f"{summary['highest_win_rate_segment']}"
    )
    print(
        "   Lowest Churn Rate Segment           : "
        f"{summary['lowest_churn_rate_segment']}"
    )


def print_forecast_summary(
    revenue_forecast: dict,
) -> None:
    """Print the revenue forecast and model summary."""

    model = revenue_forecast["model"]

    print("\nRevenue Forecast Summary")
    print("-" * SEPARATOR_WIDTH)

    print(
        f"   Model            : "
        f"{model['name']} ({model['method']})"
    )
    print(
        f"   Direction        : "
        f"{model['direction']}"
    )
    print(
        f"   Monthly Slope    : "
        f"{model['slope']:,.2f}"
    )
    print(
        f"   R-squared        : "
        f"{model['r_squared']:.4f}"
    )

    print("\n   Forecasted Revenue:")

    for forecast_item in revenue_forecast["forecast"]:
        print(
            f"     {forecast_item['month']} : "
            f"${forecast_item['forecast_revenue']:,.2f}"
        )

    if model["r_squared"] < 0.1:
        print(
            "\n   Note: The linear model has weak "
            "explanatory power. Forecast values should "
            "be treated as directional estimates."
        )


def print_decision_support_reports(
    insights_by_language: dict,
) -> None:
    """Print English and Turkish decision-support reports."""

    print("\nEnglish report:")
    print(
        format_report(
            insights_by_language["en"],
            language="en",
        )
    )

    print("\nTurkish report:")
    print(
        format_report(
            insights_by_language["tr"],
            language="tr",
        )
    )


def main() -> None:
    """Run the complete BI reporting pipeline."""

    args = parse_arguments()

    print_header()

    # Step 1 — Data loading, validation, filtering, and KPI calculation
    print("\n📂 Loading and validating datasets...")

    try:
        kpis = compute_all_kpis(
            region=args.region,
            year=args.year,
            segment=args.segment,
            product=args.product,
        )
    except ValueError as error:
        print(f"\n❌ Unable to continue: {error}")
        raise SystemExit(1) from error

    print("\n✅ Data loading and validation completed.")

    print_filter_summary(
        kpis["filters"],
        kpis["meta"]["total_orders"],
        kpis["meta"]["total_customers"],
    )

    print_kpi_summary(kpis)

    filtered_orders = kpis["_data"]["orders"]
    filtered_customers = kpis["_data"]["customers"]

    # Step 2 — Customer-segment analysis
    print("\n👥 Computing customer segment analysis...")

    segment_analysis = compute_segment_analysis(
        orders=filtered_orders,
        customers=filtered_customers,
    )

    print_segment_summary(segment_analysis)

    # Step 3 — Revenue forecasting
    print(
        f"\n🔮 Computing {FORECAST_MONTHS}-month "
        "revenue forecast..."
    )

    try:
        revenue_forecast = compute_revenue_forecast(
            kpis,
            forecast_months=FORECAST_MONTHS,
        )
    except ValueError as error:
        print(
            "\n❌ Revenue forecasting could not be completed "
            f"for the selected filters: {error}"
        )
        raise SystemExit(1) from error

    print_forecast_summary(revenue_forecast)

    # Step 4 — Chart generation
    print("\n📈 Generating bilingual charts...")

    chart_paths_by_language = generate_bilingual_charts(
        kpis,
        segment_analysis,
        revenue_forecast,
    )

    # Step 5 — Decision-support analysis
    print("\n🧠 Running decision support engine...")

    insights_by_language = {
        "en": analyze(
            kpis,
            language="en",
        ),
        "tr": analyze(
            kpis,
            language="tr",
        ),
    }

    print_decision_support_reports(
        insights_by_language
    )

    # Step 6 — HTML dashboard generation
    print("\n📄 Generating bilingual HTML report...")

    report_path = generate_html_report(
        kpis,
        insights_by_language,
        chart_paths_by_language,
        segment_analysis,
        revenue_forecast,
    )

    # Step 7 — Excel report generation
    print("\n📊 Generating Excel report...")

    excel_path = generate_excel_report(
        kpis,
        insights_by_language,
        segment_analysis,
        revenue_forecast,
    )

    print("\n✅ Done!")
    print(f"   HTML report : {report_path}")
    print(f"   Excel report: {excel_path}")
    print("=" * SEPARATOR_WIDTH)


if __name__ == "__main__":
    main()