"""
modules/excel_exporter.py

Exports KPI results, customer-segment performance, and
decision-support insights to a formatted Excel workbook
using openpyxl.
"""

import os
from datetime import datetime
from typing import Iterable

from openpyxl import Workbook
from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    PatternFill,
    Side,
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from modules.decision_support import Insight


DEFAULT_OUTPUT_PATH = "reports/kpi_report.xlsx"


# ---------------------------------------------------------------------------
# Workbook styling
# ---------------------------------------------------------------------------

TITLE_FILL = PatternFill(
    fill_type="solid",
    fgColor="1F4E78",
)

SECTION_FILL = PatternFill(
    fill_type="solid",
    fgColor="D9EAF7",
)

HEADER_FILL = PatternFill(
    fill_type="solid",
    fgColor="5B9BD5",
)

SUBHEADER_FILL = PatternFill(
    fill_type="solid",
    fgColor="DDEBF7",
)

CRITICAL_FILL = PatternFill(
    fill_type="solid",
    fgColor="F4CCCC",
)

WARNING_FILL = PatternFill(
    fill_type="solid",
    fgColor="FFF2CC",
)

INFO_FILL = PatternFill(
    fill_type="solid",
    fgColor="D9EAF7",
)

GOOD_FILL = PatternFill(
    fill_type="solid",
    fgColor="D9EAD3",
)

THIN_BORDER = Border(
    left=Side(style="thin", color="B7B7B7"),
    right=Side(style="thin", color="B7B7B7"),
    top=Side(style="thin", color="B7B7B7"),
    bottom=Side(style="thin", color="B7B7B7"),
)


SEVERITY_FILLS = {
    "critical": CRITICAL_FILL,
    "warning": WARNING_FILL,
    "info": INFO_FILL,
    "good": GOOD_FILL,
}


def _style_title(
    worksheet: Worksheet,
    title: str,
    end_column: int,
) -> None:
    """Add and format a merged worksheet title."""

    worksheet.merge_cells(
        start_row=1,
        start_column=1,
        end_row=1,
        end_column=end_column,
    )

    title_cell = worksheet.cell(
        row=1,
        column=1,
        value=title,
    )

    title_cell.fill = TITLE_FILL
    title_cell.font = Font(
        color="FFFFFF",
        bold=True,
        size=16,
    )
    title_cell.alignment = Alignment(
        horizontal="center",
        vertical="center",
    )

    worksheet.row_dimensions[1].height = 28


def _style_header_row(
    worksheet: Worksheet,
    row_number: int,
    start_column: int,
    end_column: int,
) -> None:
    """Apply consistent formatting to a table header row."""

    for column in range(
        start_column,
        end_column + 1,
    ):
        cell = worksheet.cell(
            row=row_number,
            column=column,
        )

        cell.fill = HEADER_FILL
        cell.font = Font(
            color="FFFFFF",
            bold=True,
        )
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )
        cell.border = THIN_BORDER


def _style_data_range(
    worksheet: Worksheet,
    start_row: int,
    end_row: int,
    start_column: int,
    end_column: int,
) -> None:
    """Add borders and alignment to a worksheet data range."""

    if end_row < start_row:
        return

    for row in worksheet.iter_rows(
        min_row=start_row,
        max_row=end_row,
        min_col=start_column,
        max_col=end_column,
    ):
        for cell in row:
            cell.border = THIN_BORDER
            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True,
            )


def _auto_fit_columns(
    worksheet: Worksheet,
    minimum_width: int = 12,
    maximum_width: int = 45,
) -> None:
    """Adjust worksheet column widths based on cell contents."""

    for column_cells in worksheet.columns:
        column_letter = get_column_letter(
            column_cells[0].column
        )

        maximum_length = 0

        for cell in column_cells:
            if cell.value is None:
                continue

            value_length = len(str(cell.value))
            maximum_length = max(
                maximum_length,
                value_length,
            )

        adjusted_width = min(
            max(maximum_length + 2, minimum_width),
            maximum_width,
        )

        worksheet.column_dimensions[
            column_letter
        ].width = adjusted_width


def _format_currency_cells(
    worksheet: Worksheet,
    cells: Iterable,
) -> None:
    """Apply currency formatting to selected cells."""

    for cell in cells:
        cell.number_format = '$#,##0.00'


def _format_percentage_cells(
    worksheet: Worksheet,
    cells: Iterable,
) -> None:
    """
    Apply percentage-point formatting.

    KPI values are already stored as values such as 25.5,
    rather than decimal fractions such as 0.255.
    """

    for cell in cells:
        cell.number_format = '0.00"%"'


def _prepare_table_sheet(
    worksheet: Worksheet,
    title: str,
    headers: list[str],
) -> None:
    """Prepare a worksheet containing one main table."""

    _style_title(
        worksheet,
        title,
        len(headers),
    )

    for column, header in enumerate(
        headers,
        start=1,
    ):
        worksheet.cell(
            row=3,
            column=column,
            value=header,
        )

    _style_header_row(
        worksheet,
        row_number=3,
        start_column=1,
        end_column=len(headers),
    )

    worksheet.freeze_panes = "A4"
    worksheet.auto_filter.ref = (
        f"A3:{get_column_letter(len(headers))}3"
    )


# ---------------------------------------------------------------------------
# KPI Summary
# ---------------------------------------------------------------------------

def _create_summary_sheet(
    workbook: Workbook,
    kpis: dict,
) -> None:
    """Create the high-level KPI summary worksheet."""

    worksheet = workbook.active
    worksheet.title = "KPI Summary"

    _style_title(
        worksheet,
        "BI KPI Summary",
        3,
    )

    headers = [
        "Category",
        "Metric",
        "Value",
    ]

    for column, header in enumerate(
        headers,
        start=1,
    ):
        worksheet.cell(
            row=3,
            column=column,
            value=header,
        )

    _style_header_row(
        worksheet,
        row_number=3,
        start_column=1,
        end_column=3,
    )

    revenue = kpis["revenue"]
    sales = kpis["sales"]
    products = kpis["products"]
    regions = kpis["regions"]
    trends = kpis["trends"]
    meta = kpis["meta"]

    rows = [
        (
            "Revenue",
            "Total Revenue",
            revenue["total_revenue"],
            "currency",
        ),
        (
            "Revenue",
            "Average Order Value",
            revenue["avg_order_value"],
            "currency",
        ),
        (
            "Revenue",
            "Total Won Orders",
            revenue["total_won_orders"],
            "integer",
        ),
        (
            "Revenue",
            "Current Month",
            revenue["current_month"],
            "text",
        ),
        (
            "Revenue",
            "Current Month Revenue",
            revenue["current_month_revenue"],
            "currency",
        ),
        (
            "Revenue",
            "Previous Month",
            revenue["previous_month"],
            "text",
        ),
        (
            "Revenue",
            "Previous Month Revenue",
            revenue["previous_month_revenue"],
            "currency",
        ),
        (
            "Revenue",
            "MoM Growth",
            revenue["mom_growth_pct"],
            "percentage",
        ),
        (
            "Sales",
            "Won Orders",
            sales["won_orders"],
            "integer",
        ),
        (
            "Sales",
            "Lost Orders",
            sales["lost_orders"],
            "integer",
        ),
        (
            "Sales",
            "Churned Orders",
            sales["churned_orders"],
            "integer",
        ),
        (
            "Sales",
            "Win Rate",
            sales["win_rate_pct"],
            "percentage",
        ),
        (
            "Sales",
            "Churn Rate",
            sales["churn_rate_pct"],
            "percentage",
        ),
        (
            "Sales",
            "Top Account Manager",
            sales["top_account_manager"],
            "text",
        ),
        (
            "Sales",
            "Top Account Manager Revenue",
            sales["top_am_revenue"],
            "currency",
        ),
        (
            "Product",
            "Top Product",
            products["top_product"],
            "text",
        ),
        (
            "Region",
            "Top Region",
            regions["top_region"],
            "text",
        ),
        (
            "Trend",
            "Trend Direction",
            trends["trend_direction"],
            "text",
        ),
        (
            "Trend",
            "Trend Slope",
            trends["trend_slope"],
            "number",
        ),
        (
            "Metadata",
            "Total Customers",
            meta["total_customers"],
            "integer",
        ),
        (
            "Metadata",
            "Total Orders",
            meta["total_orders"],
            "integer",
        ),
        (
            "Metadata",
            "Date Range",
            meta["date_range"],
            "text",
        ),
        (
            "Metadata",
            "Generated At",
            meta["generated_at"],
            "text",
        ),
    ]

    currency_cells = []
    percentage_cells = []

    for row_number, (
        category,
        metric,
        value,
        value_type,
    ) in enumerate(
        rows,
        start=4,
    ):
        worksheet.cell(
            row=row_number,
            column=1,
            value=category,
        )

        worksheet.cell(
            row=row_number,
            column=2,
            value=metric,
        )

        value_cell = worksheet.cell(
            row=row_number,
            column=3,
            value=value,
        )

        if value_type == "currency":
            currency_cells.append(value_cell)

        elif value_type == "percentage":
            percentage_cells.append(value_cell)

        elif value_type == "integer":
            value_cell.number_format = "#,##0"

        elif value_type == "number":
            value_cell.number_format = "#,##0.00"

    final_row = 3 + len(rows)

    _style_data_range(
        worksheet,
        start_row=4,
        end_row=final_row,
        start_column=1,
        end_column=3,
    )

    _format_currency_cells(
        worksheet,
        currency_cells,
    )

    _format_percentage_cells(
        worksheet,
        percentage_cells,
    )

    previous_category = None

    for row_number in range(
        4,
        final_row + 1,
    ):
        category_cell = worksheet.cell(
            row=row_number,
            column=1,
        )

        if category_cell.value != previous_category:
            category_cell.fill = SECTION_FILL
            category_cell.font = Font(bold=True)
            previous_category = category_cell.value

    worksheet.freeze_panes = "A4"
    worksheet.auto_filter.ref = f"A3:C{final_row}"

    _auto_fit_columns(worksheet)


# ---------------------------------------------------------------------------
# Trend worksheets
# ---------------------------------------------------------------------------

def _create_monthly_revenue_sheet(
    workbook: Workbook,
    kpis: dict,
) -> None:
    """Create the monthly revenue worksheet."""

    worksheet = workbook.create_sheet(
        "Monthly Revenue"
    )

    headers = [
        "Month",
        "Revenue",
    ]

    _prepare_table_sheet(
        worksheet,
        "Monthly Revenue Trend",
        headers,
    )

    records = kpis["trends"]["monthly_revenue"]

    for row_number, record in enumerate(
        records,
        start=4,
    ):
        worksheet.cell(
            row=row_number,
            column=1,
            value=str(record["month"]),
        )

        revenue_cell = worksheet.cell(
            row=row_number,
            column=2,
            value=record["revenue"],
        )

        revenue_cell.number_format = '$#,##0.00'

    if records:
        final_row = len(records) + 3

        _style_data_range(
            worksheet,
            start_row=4,
            end_row=final_row,
            start_column=1,
            end_column=2,
        )

        worksheet.auto_filter.ref = (
            f"A3:B{final_row}"
        )

    _auto_fit_columns(worksheet)


def _create_quarterly_revenue_sheet(
    workbook: Workbook,
    kpis: dict,
) -> None:
    """Create the quarterly revenue worksheet."""

    worksheet = workbook.create_sheet(
        "Quarterly Revenue"
    )

    headers = [
        "Quarter",
        "Revenue",
    ]

    _prepare_table_sheet(
        worksheet,
        "Quarterly Revenue Trend",
        headers,
    )

    records = kpis["trends"]["quarterly_revenue"]

    for row_number, record in enumerate(
        records,
        start=4,
    ):
        worksheet.cell(
            row=row_number,
            column=1,
            value=str(record["quarter"]),
        )

        revenue_cell = worksheet.cell(
            row=row_number,
            column=2,
            value=record["revenue"],
        )

        revenue_cell.number_format = '$#,##0.00'

    if records:
        final_row = len(records) + 3

        _style_data_range(
            worksheet,
            start_row=4,
            end_row=final_row,
            start_column=1,
            end_column=2,
        )

        worksheet.auto_filter.ref = (
            f"A3:B{final_row}"
        )

    _auto_fit_columns(worksheet)


# ---------------------------------------------------------------------------
# Product worksheet
# ---------------------------------------------------------------------------

def _create_product_sheet(
    workbook: Workbook,
    kpis: dict,
) -> None:
    """Create the product performance worksheet."""

    worksheet = workbook.create_sheet(
        "Product Performance"
    )

    headers = [
        "Product",
        "Revenue",
        "Revenue Mix",
        "Units Sold",
    ]

    _prepare_table_sheet(
        worksheet,
        "Product Performance",
        headers,
    )

    products = kpis["products"]

    product_revenue = products["product_revenue"]
    product_mix = products["product_mix_pct"]
    product_units = products["product_units_sold"]

    all_products = list(
        dict.fromkeys(
            list(product_revenue.keys())
            + list(product_mix.keys())
            + list(product_units.keys())
        )
    )

    for row_number, product in enumerate(
        all_products,
        start=4,
    ):
        worksheet.cell(
            row=row_number,
            column=1,
            value=product,
        )

        revenue_cell = worksheet.cell(
            row=row_number,
            column=2,
            value=product_revenue.get(
                product,
                0.0,
            ),
        )
        revenue_cell.number_format = '$#,##0.00'

        mix_cell = worksheet.cell(
            row=row_number,
            column=3,
            value=product_mix.get(
                product,
                0.0,
            ),
        )
        mix_cell.number_format = '0.00"%"'

        units_cell = worksheet.cell(
            row=row_number,
            column=4,
            value=product_units.get(
                product,
                0,
            ),
        )
        units_cell.number_format = "#,##0"

    if all_products:
        final_row = len(all_products) + 3

        _style_data_range(
            worksheet,
            start_row=4,
            end_row=final_row,
            start_column=1,
            end_column=4,
        )

        worksheet.auto_filter.ref = (
            f"A3:D{final_row}"
        )

    _auto_fit_columns(worksheet)


# ---------------------------------------------------------------------------
# Regional worksheet
# ---------------------------------------------------------------------------

def _create_regional_sheet(
    workbook: Workbook,
    kpis: dict,
) -> None:
    """Create the regional performance worksheet."""

    worksheet = workbook.create_sheet(
        "Regional Performance"
    )

    headers = [
        "Region",
        "Revenue",
        "Won Orders",
        "Average Order Value",
    ]

    _prepare_table_sheet(
        worksheet,
        "Regional Performance",
        headers,
    )

    regions = kpis["regions"]

    regional_revenue = regions["regional_revenue"]
    regional_won_orders = regions[
        "regional_won_orders"
    ]
    regional_avg_order_value = regions[
        "regional_avg_order_value"
    ]

    all_regions = list(
        dict.fromkeys(
            list(regional_revenue.keys())
            + list(regional_won_orders.keys())
            + list(regional_avg_order_value.keys())
        )
    )

    for row_number, region in enumerate(
        all_regions,
        start=4,
    ):
        worksheet.cell(
            row=row_number,
            column=1,
            value=region,
        )

        revenue_cell = worksheet.cell(
            row=row_number,
            column=2,
            value=regional_revenue.get(
                region,
                0.0,
            ),
        )
        revenue_cell.number_format = '$#,##0.00'

        won_orders_cell = worksheet.cell(
            row=row_number,
            column=3,
            value=regional_won_orders.get(
                region,
                0,
            ),
        )
        won_orders_cell.number_format = "#,##0"

        average_cell = worksheet.cell(
            row=row_number,
            column=4,
            value=regional_avg_order_value.get(
                region,
                0.0,
            ),
        )
        average_cell.number_format = '$#,##0.00'

    if all_regions:
        final_row = len(all_regions) + 3

        _style_data_range(
            worksheet,
            start_row=4,
            end_row=final_row,
            start_column=1,
            end_column=4,
        )

        worksheet.auto_filter.ref = (
            f"A3:D{final_row}"
        )

    _auto_fit_columns(worksheet)


# ---------------------------------------------------------------------------
# Sales worksheet
# ---------------------------------------------------------------------------

def _create_sales_sheet(
    workbook: Workbook,
    kpis: dict,
) -> None:
    """Create the sales performance worksheet."""

    worksheet = workbook.create_sheet(
        "Sales Performance"
    )

    _style_title(
        worksheet,
        "Sales Performance",
        2,
    )

    worksheet.cell(
        row=3,
        column=1,
        value="Metric",
    )
    worksheet.cell(
        row=3,
        column=2,
        value="Value",
    )

    _style_header_row(
        worksheet,
        row_number=3,
        start_column=1,
        end_column=2,
    )

    sales = kpis["sales"]

    rows = [
        (
            "Won Orders",
            sales["won_orders"],
            "integer",
        ),
        (
            "Lost Orders",
            sales["lost_orders"],
            "integer",
        ),
        (
            "Churned Orders",
            sales["churned_orders"],
            "integer",
        ),
        (
            "Win Rate",
            sales["win_rate_pct"],
            "percentage",
        ),
        (
            "Churn Rate",
            sales["churn_rate_pct"],
            "percentage",
        ),
        (
            "Top Account Manager",
            sales["top_account_manager"],
            "text",
        ),
        (
            "Top Account Manager Revenue",
            sales["top_am_revenue"],
            "currency",
        ),
    ]

    for row_number, (
        metric,
        value,
        value_type,
    ) in enumerate(
        rows,
        start=4,
    ):
        worksheet.cell(
            row=row_number,
            column=1,
            value=metric,
        )

        value_cell = worksheet.cell(
            row=row_number,
            column=2,
            value=value,
        )

        if value_type == "currency":
            value_cell.number_format = '$#,##0.00'

        elif value_type == "percentage":
            value_cell.number_format = '0.00"%"'

        elif value_type == "integer":
            value_cell.number_format = "#,##0"

    final_row = len(rows) + 3

    _style_data_range(
        worksheet,
        start_row=4,
        end_row=final_row,
        start_column=1,
        end_column=2,
    )

    worksheet.freeze_panes = "A4"
    worksheet.auto_filter.ref = f"A3:B{final_row}"

    _auto_fit_columns(worksheet)


# ---------------------------------------------------------------------------
# Segment worksheet
# ---------------------------------------------------------------------------

def _create_segment_sheet(
    workbook: Workbook,
    segment_analysis: dict,
) -> None:
    """Create the customer-segment performance worksheet."""

    worksheet = workbook.create_sheet(
        "Segment Performance"
    )

    headers = [
        "Segment",
        "Customers",
        "Active Customers",
        "Total Orders",
        "Won Orders",
        "Lost Orders",
        "Churned Orders",
        "Revenue",
        "Revenue Share",
        "Revenue per Customer",
        "Average Order Value",
        "Win Rate",
        "Churn Rate",
        "Top Product",
    ]

    _prepare_table_sheet(
        worksheet,
        "Customer Segment Performance",
        headers,
    )

    performance = segment_analysis.get(
        "performance",
        {},
    )

    for row_number, (
        segment,
        values,
    ) in enumerate(
        performance.items(),
        start=4,
    ):
        worksheet.cell(
            row=row_number,
            column=1,
            value=segment,
        )

        customer_cell = worksheet.cell(
            row=row_number,
            column=2,
            value=values["customer_count"],
        )
        customer_cell.number_format = "#,##0"

        active_customer_cell = worksheet.cell(
            row=row_number,
            column=3,
            value=values["active_customers"],
        )
        active_customer_cell.number_format = "#,##0"

        total_orders_cell = worksheet.cell(
            row=row_number,
            column=4,
            value=values["total_orders"],
        )
        total_orders_cell.number_format = "#,##0"

        won_orders_cell = worksheet.cell(
            row=row_number,
            column=5,
            value=values["won_orders"],
        )
        won_orders_cell.number_format = "#,##0"

        lost_orders_cell = worksheet.cell(
            row=row_number,
            column=6,
            value=values["lost_orders"],
        )
        lost_orders_cell.number_format = "#,##0"

        churned_orders_cell = worksheet.cell(
            row=row_number,
            column=7,
            value=values["churned_orders"],
        )
        churned_orders_cell.number_format = "#,##0"

        revenue_cell = worksheet.cell(
            row=row_number,
            column=8,
            value=values["total_revenue"],
        )
        revenue_cell.number_format = '$#,##0.00'

        share_cell = worksheet.cell(
            row=row_number,
            column=9,
            value=values["revenue_share_pct"],
        )
        share_cell.number_format = '0.00"%"'

        revenue_per_customer_cell = worksheet.cell(
            row=row_number,
            column=10,
            value=values["revenue_per_customer"],
        )
        revenue_per_customer_cell.number_format = '$#,##0.00'

        average_order_value_cell = worksheet.cell(
            row=row_number,
            column=11,
            value=values["avg_order_value"],
        )
        average_order_value_cell.number_format = '$#,##0.00'

        win_rate_cell = worksheet.cell(
            row=row_number,
            column=12,
            value=values["win_rate_pct"],
        )
        win_rate_cell.number_format = '0.00"%"'

        churn_rate_cell = worksheet.cell(
            row=row_number,
            column=13,
            value=values["churn_rate_pct"],
        )
        churn_rate_cell.number_format = '0.00"%"'

        worksheet.cell(
            row=row_number,
            column=14,
            value=values["top_product"],
        )

    if performance:
        final_row = len(performance) + 3

        _style_data_range(
            worksheet,
            start_row=4,
            end_row=final_row,
            start_column=1,
            end_column=14,
        )

        worksheet.auto_filter.ref = (
            f"A3:N{final_row}"
        )

    worksheet.freeze_panes = "A4"

    _auto_fit_columns(
        worksheet,
        minimum_width=12,
        maximum_width=24,
    )


# ---------------------------------------------------------------------------
# Decision-support worksheet
# ---------------------------------------------------------------------------

def _create_insights_sheet(
    workbook: Workbook,
    insights_by_language: dict[
        str,
        list[Insight],
    ],
) -> None:
    """Create a bilingual decision-support insights worksheet."""

    worksheet = workbook.create_sheet(
        "Decision Insights"
    )

    headers = [
        "Language",
        "Priority",
        "Severity",
        "Category",
        "Title",
        "Detail",
        "Recommended Action",
    ]

    _prepare_table_sheet(
        worksheet,
        "Decision-Support Insights",
        headers,
    )

    row_number = 4

    for language, insights in insights_by_language.items():
        language_label = (
            "English"
            if language == "en"
            else "Türkçe"
        )

        for insight in insights:
            values = [
                language_label,
                insight.priority,
                insight.severity.capitalize(),
                insight.category,
                insight.title,
                insight.detail,
                insight.action,
            ]

            for column, value in enumerate(
                values,
                start=1,
            ):
                worksheet.cell(
                    row=row_number,
                    column=column,
                    value=value,
                )

            severity_fill = SEVERITY_FILLS.get(
                insight.severity,
                INFO_FILL,
            )

            worksheet.cell(
                row=row_number,
                column=3,
            ).fill = severity_fill

            row_number += 1

    final_row = row_number - 1

    if final_row >= 4:
        _style_data_range(
            worksheet,
            start_row=4,
            end_row=final_row,
            start_column=1,
            end_column=7,
        )

        worksheet.auto_filter.ref = (
            f"A3:G{final_row}"
        )

    worksheet.column_dimensions["A"].width = 12
    worksheet.column_dimensions["B"].width = 10
    worksheet.column_dimensions["C"].width = 12
    worksheet.column_dimensions["D"].width = 18
    worksheet.column_dimensions["E"].width = 30
    worksheet.column_dimensions["F"].width = 55
    worksheet.column_dimensions["G"].width = 55

    worksheet.freeze_panes = "A4"


def _create_forecast_sheet(
    workbook: Workbook,
    revenue_forecast: dict,
) -> None:
    """Create the revenue forecast worksheet."""

    worksheet = workbook.create_sheet(
        "Revenue Forecast"
    )

    headers = [
        "Month",
        "Actual Revenue",
        "Trend Value",
        "Forecast Revenue",
    ]

    _prepare_table_sheet(
        worksheet,
        "Three-Month Revenue Forecast",
        headers,
    )

    historical = revenue_forecast["historical"]
    forecast = revenue_forecast["forecast"]
    model = revenue_forecast["model"]

    row = 4

    for record in historical:
        worksheet.cell(
            row=row,
            column=1,
            value=record["month"],
        )

        actual = worksheet.cell(
            row=row,
            column=2,
            value=record["revenue"],
        )

        trend = worksheet.cell(
            row=row,
            column=3,
            value=record["trend_value"],
        )

        actual.number_format = '$#,##0.00'
        trend.number_format = '$#,##0.00'

        row += 1

    for record in forecast:
        worksheet.cell(
            row=row,
            column=1,
            value=record["month"],
        )

        forecast_cell = worksheet.cell(
            row=row,
            column=4,
            value=record["forecast_revenue"],
        )

        forecast_cell.number_format = '$#,##0.00'

        row += 1

    row += 2

    worksheet.cell(row=row, column=1).value = "Model"
    worksheet.cell(row=row, column=2).value = model["name"]

    row += 1
    worksheet.cell(row=row, column=1).value = "Method"
    worksheet.cell(row=row, column=2).value = model["method"]

    row += 1
    worksheet.cell(row=row, column=1).value = "Slope"
    worksheet.cell(row=row, column=2).value = model["slope"]

    row += 1
    worksheet.cell(row=row, column=1).value = "R²"
    worksheet.cell(row=row, column=2).value = model["r_squared"]

    row += 1
    worksheet.cell(row=row, column=1).value = "Trend Direction"
    worksheet.cell(row=row, column=2).value = model["direction"]

    row += 2

    worksheet.cell(
        row=row,
        column=1,
    ).value = "Forecast Assumptions"

    worksheet.cell(
        row=row,
        column=1,
    ).font = Font(bold=True)

    row += 1

    for assumption in revenue_forecast["assumptions"]:
        worksheet.cell(
            row=row,
            column=1,
            value=assumption,
        )
        row += 1

    _auto_fit_columns(worksheet)

# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

def generate_excel_report(
    kpis: dict,
    insights_by_language: dict[
        str,
        list[Insight],
    ],
    segment_analysis: dict,
    revenue_forecast: dict,
    output_path: str = DEFAULT_OUTPUT_PATH,
) -> str:
    """
    Generate a formatted Excel workbook containing KPI results,
    customer-segment performance, and bilingual decision-support
    insights.

    Args:
        kpis:
            KPI results returned by compute_all_kpis().

        insights_by_language:
            English and Turkish Insight collections.

        segment_analysis:
            Segment-analysis results returned by
            compute_segment_analysis().

        output_path:
            Destination path of the generated Excel workbook.

    Returns:
        The generated workbook path.
    """

    output_directory = os.path.dirname(
        output_path
    )

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True,
        )

    workbook = Workbook()

    _create_summary_sheet(
        workbook,
        kpis,
    )

    _create_monthly_revenue_sheet(
        workbook,
        kpis,
    )

    _create_quarterly_revenue_sheet(
        workbook,
        kpis,
    )

    _create_product_sheet(
        workbook,
        kpis,
    )

    _create_regional_sheet(
        workbook,
        kpis,
    )

    _create_sales_sheet(
        workbook,
        kpis,
    )

    _create_segment_sheet(
        workbook,
        segment_analysis,
    )

    _create_forecast_sheet(
        workbook,
        revenue_forecast,
    )

    _create_insights_sheet(
        workbook,
        insights_by_language,
    )

    workbook.properties.title = (
        "Python BI Reporting and Decision Support Report"
    )

    workbook.properties.subject = (
        "KPI, segment, and decision-support analysis"
    )

    workbook.properties.creator = (
        "Salsabeel Alfayoumi"
    )

    workbook.properties.created = datetime.now()

    workbook.save(output_path)

    print(f"  ✓ {output_path}")

    return output_path