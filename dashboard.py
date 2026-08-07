"""
dashboard.py

Interactive Streamlit dashboard for the Python BI Reporting
and Decision Support System.

Run:
    streamlit run dashboard.py
"""

from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from modules.decision_support import analyze, DEFAULT_THRESHOLDS
from modules.forecast import compute_revenue_forecast
from modules.i18n import translate
from modules.kpi_engine import compute_analysis, load_data
from modules.segment_analysis import compute_segment_analysis
from modules.theme import (
    ACCENT_COLOR,
    HIGHLIGHT_COLOR,
    PALETTE,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    SEVERITY_COLORS,
    STATUS_COLORS,
    TREND_COLOR,
)


# ---------------------------------------------------------------------------
# Page configuration and visual constants
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Python BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


SEVERITY_ICONS = {
    "critical": "🔴",
    "warning": "🟡",
    "info": "🔵",
    "good": "🟢",
}




# ---------------------------------------------------------------------------
# Styling and shared helpers
# ---------------------------------------------------------------------------
def apply_custom_css() -> None:
    """
    Apply lightweight theme-neutral dashboard styling.

    Colors intentionally use inherited text and translucent surfaces so
    Streamlit's native light/dark theme switch remains readable.
    """

    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 2rem;
                padding-bottom: 3rem;
                max-width: 1500px;
            }

            .scope-card {
                background: rgba(45, 106, 159, 0.12);
                border: 1px solid rgba(45, 106, 159, 0.28);
                border-radius: 12px;
                padding: 14px 18px;
                color: inherit;
                margin-bottom: 1rem;
            }

            .summary-card,
            .insight-card {
                background: rgba(128, 128, 128, 0.06);
                border: 1px solid rgba(128, 128, 128, 0.24);
                border-radius: 12px;
                padding: 14px 16px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
            }

            .summary-card {
                min-height: 112px;
            }

            .insight-card {
                margin-bottom: 12px;
            }

            .summary-label {
                color: inherit;
                opacity: 0.72;
                font-size: 0.82rem;
                margin-bottom: 8px;
            }

            .summary-value,
            .insight-title {
                color: inherit;
                font-weight: 700;
            }

            .summary-value {
                font-size: 1.15rem;
            }

            .insight-title {
                font-size: 1rem;
                margin-bottom: 8px;
            }

            .insight-text {
                color: inherit;
                opacity: 0.86;
                line-height: 1.5;
                margin: 4px 0;
            }

            .footer {
                color: inherit;
                opacity: 0.68;
                text-align: center;
                font-size: 0.85rem;
                padding-top: 2rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def text(language: str, key: str) -> str:
    """Return dashboard UI text from the central translation source."""

    return translate(
        f"dashboard.{key}",
        language,
    )


def format_currency(value: float, compact: bool = False) -> str:
    """Format a numeric value as USD."""

    if compact:
        absolute_value = abs(value)

        if absolute_value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"

        if absolute_value >= 1_000:
            return f"${value / 1_000:.1f}K"

    return f"${value:,.2f}"


def clean_plotly_figure(
    figure: go.Figure,
    *,
    height: int = 430,
    showlegend: bool = True,
) -> go.Figure:
    """
    Apply layout details while leaving colors to Streamlit's active theme.

    st.plotly_chart uses the Streamlit Plotly theme by default, so explicit
    white backgrounds or dark text colors would break dark-mode support.
    """

    figure.update_layout(
        height=height,
        margin={
            "l": 55,
            "r": 35,
            "t": 65,
            "b": 55,
        },
        font={
            "family": "Segoe UI, Arial, sans-serif",
        },
        showlegend=showlegend,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
    )

    figure.update_xaxes(
        automargin=True,
        showgrid=False,
        zeroline=False,
    )

    figure.update_yaxes(
        automargin=True,
        showgrid=True,
        zeroline=False,
    )

    return figure


def sorted_text_values(
    dataframe: pd.DataFrame,
    column: str,
) -> list[str]:
    """Return sorted unique non-null text values."""

    return sorted(
        dataframe[column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )



@st.cache_data
def load_source_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load source datasets once and cache them for Streamlit reruns."""

    return load_data()


def build_filter_options(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
) -> dict[str, list[Any]]:
    """Build sidebar filter options from the source datasets."""

    years = sorted(
        orders["order_date"]
        .dropna()
        .dt.year
        .astype(int)
        .unique()
        .tolist()
    )

    return {
        "regions": sorted_text_values(orders, "region"),
        "years": years,
        "segments": sorted_text_values(customers, "segment"),
        "products": sorted_text_values(orders, "product"),
    }


def selected_or_none(value: Any, all_label: str) -> Any | None:
    """Convert the localized 'All' selection into None."""

    return None if value == all_label else value


# ---------------------------------------------------------------------------
# Figure builders
# ---------------------------------------------------------------------------
def monthly_revenue_figure(
    kpis: dict,
    language: str,
) -> go.Figure:
    """Build the monthly revenue line chart."""

    dataframe = pd.DataFrame(
        kpis["trends"]["monthly_revenue"]
    )

    figure = px.line(
        dataframe,
        x="month",
        y="revenue",
        markers=True,
        title=text(language, "monthly_revenue"),
        labels={
            "month": text(language, "month"),
            "revenue": text(language, "revenue"),
        },
    )

    figure.update_traces(
        line={
            "color": PRIMARY_COLOR,
            "width": 3,
        },
        marker={
            "color": PRIMARY_COLOR,
            "size": 7,
        },
        fill="tozeroy",
        fillcolor="rgba(45,106,159,0.12)",
        hovertemplate=(
            "<b>%{x}</b><br>"
            + text(language, "revenue")
            + ": $%{y:,.2f}<extra></extra>"
        ),
    )

    figure.update_yaxes(
        tickprefix="$",
        tickformat=",.0f",
    )

    return clean_plotly_figure(
        figure,
        height=460,
        showlegend=False,
    )


def regional_revenue_figure(
    kpis: dict,
    language: str,
) -> go.Figure:
    """Build the regional revenue bar chart."""

    dataframe = pd.DataFrame(
        list(
            kpis["regions"]["regional_revenue"].items()
        ),
        columns=[
            "region",
            "revenue",
        ],
    ).sort_values(
        "revenue",
        ascending=True,
    )

    figure = px.bar(
        dataframe,
        x="revenue",
        y="region",
        orientation="h",
        title=text(language, "regional_revenue"),
        labels={
            "region": text(language, "region"),
            "revenue": text(language, "revenue"),
        },
        text_auto=".3s",
    )

    figure.update_traces(
        marker_color=SECONDARY_COLOR,
        hovertemplate=(
            "<b>%{y}</b><br>"
            + text(language, "revenue")
            + ": $%{x:,.2f}<extra></extra>"
        ),
    )

    figure.update_xaxes(
        tickprefix="$",
        tickformat=",.0f",
    )

    return clean_plotly_figure(
        figure,
        showlegend=False,
    )


def product_mix_figure(
    kpis: dict,
    language: str,
) -> go.Figure:
    """Build the product revenue donut chart."""

    dataframe = pd.DataFrame(
        list(
            kpis["products"]["product_revenue"].items()
        ),
        columns=[
            "product",
            "revenue",
        ],
    )

    figure = px.pie(
        dataframe,
        names="product",
        values="revenue",
        hole=0.48,
        title=text(language, "product_mix"),
        color_discrete_sequence=PALETTE,
    )

    figure.update_traces(
        textinfo="percent+label",
        textposition="inside",
        hovertemplate=(
            "<b>%{label}</b><br>"
            + text(language, "revenue")
            + ": $%{value:,.2f}<br>"
            + "%{percent}<extra></extra>"
        ),
        marker={
            "line": {
                "color": "white",
                "width": 2,
            }
        },
    )

    return clean_plotly_figure(
        figure,
        showlegend=False,
    )


def status_breakdown_figure(
    orders: pd.DataFrame,
    language: str,
) -> go.Figure:
    """Build the order status chart."""

    dataframe = (
        orders["status"]
        .value_counts()
        .rename_axis("status")
        .reset_index(name="count")
    )

    figure = px.bar(
        dataframe,
        x="status",
        y="count",
        color="status",
        color_discrete_map=STATUS_COLORS,
        title=text(language, "status_breakdown"),
        labels={
            "status": "Status",
            "count": text(language, "count"),
        },
        text="count",
    )

    figure.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{x}</b><br>"
            + text(language, "count")
            + ": %{y}<extra></extra>"
        ),
    )

    return clean_plotly_figure(
        figure,
        showlegend=False,
    )


def account_manager_figure(
    orders: pd.DataFrame,
    language: str,
) -> go.Figure:
    """Build the account-manager revenue and order chart."""

    won_orders = orders[
        orders["status"] == "Won"
    ]

    dataframe = (
        won_orders.groupby("account_manager")
        .agg(
            revenue=(
                "total_amount",
                "sum",
            ),
            orders=(
                "order_id",
                "count",
            ),
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False,
        )
    )

    figure = make_subplots(
        specs=[
            [
                {
                    "secondary_y": True,
                }
            ]
        ]
    )

    figure.add_trace(
        go.Bar(
            name=text(language, "revenue"),
            x=dataframe["account_manager"],
            y=dataframe["revenue"],
            marker_color=PRIMARY_COLOR,
            hovertemplate=(
                "<b>%{x}</b><br>"
                + text(language, "revenue")
                + ": $%{y:,.2f}<extra></extra>"
            ),
        ),
        secondary_y=False,
    )

    figure.add_trace(
        go.Scatter(
            name=text(language, "orders"),
            x=dataframe["account_manager"],
            y=dataframe["orders"],
            mode="lines+markers",
            line={
                "color": ACCENT_COLOR,
                "width": 3,
            },
            marker={
                "size": 8,
            },
            hovertemplate=(
                "<b>%{x}</b><br>"
                + text(language, "orders")
                + ": %{y}<extra></extra>"
            ),
        ),
        secondary_y=True,
    )

    figure.update_layout(
        title=text(language, "am_performance"),
        hovermode="x unified",
    )

    figure.update_yaxes(
        title_text=text(language, "revenue"),
        tickprefix="$",
        tickformat=",.0f",
        secondary_y=False,
    )

    figure.update_yaxes(
        title_text=text(language, "orders"),
        secondary_y=True,
        showgrid=False,
    )

    return clean_plotly_figure(
        figure,
        height=470,
        showlegend=True,
    )


def segment_performance_figure(
    segment_analysis: dict,
    language: str,
) -> go.Figure:
    """Build the segment revenue and win-rate chart."""

    records = []

    for segment_name, values in (
        segment_analysis["performance"].items()
    ):
        records.append(
            {
                "segment": segment_name,
                "revenue": values["total_revenue"],
                "win_rate": values["win_rate_pct"],
            }
        )

    dataframe = pd.DataFrame(records)

    figure = make_subplots(
        specs=[
            [
                {
                    "secondary_y": True,
                }
            ]
        ]
    )

    figure.add_trace(
        go.Bar(
            name=text(language, "revenue"),
            x=dataframe["segment"],
            y=dataframe["revenue"],
            marker_color=PRIMARY_COLOR,
            hovertemplate=(
                "<b>%{x}</b><br>"
                + text(language, "revenue")
                + ": $%{y:,.2f}<extra></extra>"
            ),
        ),
        secondary_y=False,
    )

    figure.add_trace(
        go.Scatter(
            name=text(language, "win_rate"),
            x=dataframe["segment"],
            y=dataframe["win_rate"],
            mode="lines+markers+text",
            text=[
                f"{value:.2f}%"
                for value in dataframe["win_rate"]
            ],
            textposition="top center",
            line={
                "color": ACCENT_COLOR,
                "width": 3,
            },
            marker={
                "size": 9,
            },
            hovertemplate=(
                "<b>%{x}</b><br>"
                + text(language, "win_rate")
                + ": %{y:.2f}%<extra></extra>"
            ),
        ),
        secondary_y=True,
    )

    figure.update_layout(
        title=text(language, "segment_performance"),
        hovermode="x unified",
    )

    figure.update_yaxes(
        title_text=text(language, "revenue"),
        tickprefix="$",
        tickformat=",.0f",
        secondary_y=False,
    )

    figure.update_yaxes(
        title_text=text(language, "win_rate_axis"),
        ticksuffix="%",
        range=[0, 100],
        showgrid=False,
        secondary_y=True,
    )

    return clean_plotly_figure(
        figure,
        showlegend=True,
    )


def forecast_figure(
    forecast: dict,
    language: str,
) -> go.Figure:
    """Build the historical, trend, and forecast chart."""

    historical = pd.DataFrame(
        forecast["historical"]
    )

    future = pd.DataFrame(
        forecast["forecast"]
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            name=text(language, "actual_revenue"),
            x=historical["month"],
            y=historical["revenue"],
            mode="lines+markers",
            line={
                "color": PRIMARY_COLOR,
                "width": 3,
            },
            marker={
                "size": 7,
            },
            hovertemplate=(
                "<b>%{x}</b><br>"
                + text(language, "actual_revenue")
                + ": $%{y:,.2f}<extra></extra>"
            ),
        )
    )

    figure.add_trace(
        go.Scatter(
            name=text(language, "linear_trend"),
            x=historical["month"],
            y=historical["trend_value"],
            mode="lines",
            line={
                "color": TREND_COLOR,
                "width": 2,
                "dash": "dash",
            },
            hovertemplate=(
                "<b>%{x}</b><br>"
                + text(language, "linear_trend")
                + ": $%{y:,.2f}<extra></extra>"
            ),
        )
    )

    forecast_x = [
        historical["month"].iloc[-1],
        *future["month"].tolist(),
    ]

    forecast_y = [
        historical["trend_value"].iloc[-1],
        *future["forecast_revenue"].tolist(),
    ]

    figure.add_trace(
        go.Scatter(
            name=text(language, "forecast_label"),
            x=forecast_x,
            y=forecast_y,
            mode="lines+markers",
            line={
                "color": ACCENT_COLOR,
                "width": 4,
                "dash": "dot",
            },
            marker={
                "size": 9,
            },
            hovertemplate=(
                "<b>%{x}</b><br>"
                + text(language, "forecast_label")
                + ": $%{y:,.2f}<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title=text(language, "forecast"),
        hovermode="x unified",
    )

    figure.update_yaxes(
        tickprefix="$",
        tickformat=",.0f",
    )

    return clean_plotly_figure(
        figure,
        height=480,
        showlegend=True,
    )


# ---------------------------------------------------------------------------
# Dashboard rendering
# ---------------------------------------------------------------------------
def render_segment_summary(
    segment_analysis: dict,
    language: str,
) -> None:
    """Render segment leaders as four summary cards."""

    summary = segment_analysis["summary"]

    cards = [
        (
            text(language, "highest_revenue_segment"),
            summary["highest_revenue_segment"],
        ),
        (
            text(language, "highest_revenue_per_customer"),
            summary[
                "highest_revenue_per_customer_segment"
            ],
        ),
        (
            text(language, "highest_win_rate_segment"),
            summary["highest_win_rate_segment"],
        ),
        (
            text(language, "lowest_churn_rate_segment"),
            summary["lowest_churn_rate_segment"],
        ),
    ]

    columns = st.columns(4)

    for column, (label, value) in zip(
        columns,
        cards,
    ):
        with column:
            st.markdown(
                f"""
                <div class="summary-card">
                    <div class="summary-label">{escape(str(label))}</div>
                    <div class="summary-value">{escape(str(value))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_insights(
    insights: list,
    language: str,
) -> None:
    """Render localized decision-support insight cards."""

    for insight in insights:
        color = SEVERITY_COLORS.get(
            insight.severity,
            SEVERITY_COLORS["info"],
        )

        icon = SEVERITY_ICONS.get(
            insight.severity,
            SEVERITY_ICONS["info"],
        )

        st.markdown(
            f"""
            <div class="insight-card"
                 style="border-left: 5px solid {color};">
                <div class="insight-title">
                    {escape(str(icon))} [{escape(str(insight.category))}] {escape(str(insight.title))}
                </div>
                <div class="insight-text">
                    <strong>{escape(str(text(language, "detail")))}:</strong>
                    {escape(str(insight.detail))}
                </div>
                <div class="insight-text">
                    <strong>▶ {escape(str(text(language, "action")))}:</strong>
                    {escape(str(insight.action))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    """Run the complete interactive Streamlit dashboard."""

    apply_custom_css()

    try:
        raw_orders, raw_customers = load_source_data()
    except ValueError:
        st.error(
            "CRM data could not be loaded. "
            "Please check the project data files."
        )
        st.stop()

    options = build_filter_options(
        raw_orders,
        raw_customers,
    )

    language_display = st.sidebar.selectbox(
        "Language / Dil",
        options=[
            "English",
            "Türkçe",
        ],
    )

    language = (
        "tr"
        if language_display == "Türkçe"
        else "en"
    )

    all_label = text(language, "all")

    st.sidebar.header(
        f"🔎 {text(language, 'filters')}"
    )

    selected_region_display = st.sidebar.selectbox(
        text(language, "region"),
        options=[
            all_label,
            *options["regions"],
        ],
    )

    selected_year_display = st.sidebar.selectbox(
        text(language, "year"),
        options=[
            all_label,
            *options["years"],
        ],
    )

    selected_segment_display = st.sidebar.selectbox(
        text(language, "segment"),
        options=[
            all_label,
            *options["segments"],
        ],
    )

    selected_product_display = st.sidebar.selectbox(
        text(language, "product"),
        options=[
            all_label,
            *options["products"],
        ],
    )

    selected_region = selected_or_none(
        selected_region_display,
        all_label,
    )

    selected_year = selected_or_none(
        selected_year_display,
        all_label,
    )

    selected_segment = selected_or_none(
        selected_segment_display,
        all_label,
    )

    selected_product = selected_or_none(
        selected_product_display,
        all_label,
    )

    st.title(
        f"📊 {text(language, 'page_title')}"
    )

    st.caption(
        text(language, "page_caption")
    )

    try:
        analysis = compute_analysis(
            orders=raw_orders,
            customers=raw_customers,
            region=selected_region,
            year=selected_year,
            segment=selected_segment,
            product=selected_product,
            print_validation=False,
        )
        kpis = analysis.kpis
    except ValueError as error:
        st.error(
            f"{text(language, 'no_data')} {error}"
        )
        st.stop()

    filtered_orders = analysis.orders
    filtered_customers = analysis.customers

    segment_analysis = compute_segment_analysis(
        orders=filtered_orders,
        customers=filtered_customers,
    )

    insights = analyze(
        kpis,
        language=language,
    )

    try:
        revenue_forecast = compute_revenue_forecast(
            kpis,
            forecast_months=3,
        )
    except ValueError:
        revenue_forecast = None

    st.subheader(
        text(language, "scope")
    )

    active_filters = kpis["filters"]

    if active_filters:
        filter_parts = [
            f"{text(language, key)}: {value}"
            for key, value in active_filters.items()
        ]

        scope_name = " · ".join(filter_parts)
    else:
        scope_name = text(
            language,
            "full_dataset",
        )

    st.markdown(
        f"""
        <div class="scope-card">
            <strong>{escape(str(scope_name))}</strong><br>
            {kpis['meta']['total_orders']:,}
            {escape(str(text(language, 'orders')))}
            &nbsp; · &nbsp;
            {kpis['meta']['active_customers']:,}
            {escape(str(text(language, 'customers')))}
            &nbsp; · &nbsp;
            {escape(str(text(language, 'date_range')))}:
            {escape(str(kpis['meta']['date_range']))}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(
        text(language, "kpis")
    )

    revenue = kpis["revenue"]
    sales = kpis["sales"]
    trends = kpis["trends"]

    first_row = st.columns(4)

    first_row[0].metric(
        text(language, "total_revenue"),
        format_currency(
            revenue["total_revenue"],
            compact=True,
        ),
        delta=(
            f"{revenue['mom_growth_pct']:+.2f}% MoM"
            if revenue["mom_growth_pct"] is not None
            else revenue.get("mom_growth_status", "Unavailable")
        ),
    )

    first_row[1].metric(
        text(language, "avg_order_value"),
        format_currency(
            revenue["avg_order_value"],
            compact=True,
        ),
    )

    first_row[2].metric(
        text(language, "win_rate"),
        f"{sales['win_rate_pct']:.2f}%",
    )

    first_row[3].metric(
        text(language, "churn_rate"),
        f"{sales['churned_order_rate_pct']:.2f}%",
        delta=(
            f"{sales['churned_order_rate_pct'] - DEFAULT_THRESHOLDS.churned_order_warning_pct:+.2f}% "
            "vs target"
        ),
        delta_color="inverse",
    )

    second_row = st.columns(4)

    second_row[0].metric(
        text(language, "mom_growth"),
        (
            f"{revenue['mom_growth_pct']:+.2f}%"
            if revenue["mom_growth_pct"] is not None
            else revenue.get("mom_growth_status", "Unavailable")
        ),
    )

    second_row[1].metric(
        text(language, "overall_trend"),
        trends["trend_direction"],
    )

    second_row[2].metric(
        text(language, "matching_orders"),
        f"{kpis['meta']['total_orders']:,}",
    )

    second_row[3].metric(
        text(language, "matching_customers"),
        f"{kpis['meta']['total_customers']:,}",
    )

    st.subheader(
        text(language, "segment_summary")
    )

    render_segment_summary(
        segment_analysis,
        language,
    )

    st.subheader(
        text(language, "analytics")
    )

    st.plotly_chart(
        monthly_revenue_figure(
            kpis,
            language,
        ),
        width="stretch",
        config={
            "displaylogo": False,
        },
    )

    analytics_left, analytics_right = st.columns(2)

    with analytics_left:
        st.plotly_chart(
            regional_revenue_figure(
                kpis,
                language,
            ),
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

    with analytics_right:
        st.plotly_chart(
            product_mix_figure(
                kpis,
                language,
            ),
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

    status_column, manager_column = st.columns(2)

    with status_column:
        st.plotly_chart(
            status_breakdown_figure(
                filtered_orders,
                language,
            ),
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

    with manager_column:
        st.plotly_chart(
            account_manager_figure(
                filtered_orders,
                language,
            ),
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

    st.plotly_chart(
        segment_performance_figure(
            segment_analysis,
            language,
        ),
        width="stretch",
        config={
            "displaylogo": False,
        },
    )

    st.subheader(
        text(language, "decision_support")
    )

    render_insights(
        insights,
        language,
    )

    st.subheader(
        text(language, "forecast")
    )

    if revenue_forecast is None:
        st.warning(
            text(language, "no_forecast")
        )
    else:
        forecast_model = revenue_forecast["model"]

        model_columns = st.columns(4)

        model_columns[0].metric(
            text(language, "forecast_model"),
            forecast_model["name"],
        )

        model_columns[1].metric(
            text(language, "slope"),
            f"{forecast_model['slope']:,.2f}",
        )

        r_squared_display = (
            f"{forecast_model['r_squared']:.4f}"
            if forecast_model.get(
                "r_squared_interpretable",
                True,
            )
            else "N/A"
        )

        model_columns[2].metric(
            text(language, "r_squared"),
            r_squared_display,
        )

        reliability = forecast_model.get(
            "reliability",
            "unavailable",
        )
        model_columns[3].metric(
            translate(
                "forecast.reliability.label",
                language,
            ),
            translate(
                f"forecast.reliability.{reliability}",
                language,
            ),
        )

        st.plotly_chart(
            forecast_figure(
                revenue_forecast,
                language,
            ),
            width="stretch",
            config={
                "displaylogo": False,
            },
        )

        forecast_table = pd.DataFrame(
            revenue_forecast["forecast"]
        ).rename(
            columns={
                "month": text(language, "month"),
                "forecast_revenue": text(
                    language,
                    "forecast_revenue",
                ),
            }
        )

        forecast_table[
            text(language, "forecast_revenue")
        ] = forecast_table[
            text(language, "forecast_revenue")
        ].map(format_currency)

        st.markdown(
            f"### {text(language, 'forecast_table')}"
        )

        st.dataframe(
            forecast_table,
            width="stretch",
            hide_index=True,
        )

    st.markdown(
        f"""
        <div class="footer">
            {escape(str(text(language, "footer")))}
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
