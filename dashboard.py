"""
dashboard.py

Interactive Streamlit dashboard for the Python BI Reporting
and Decision Support System.

Run:
    streamlit run dashboard.py
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from modules.decision_support import analyze
from modules.forecast import compute_revenue_forecast
from modules.kpi_engine import compute_all_kpis, load_data
from modules.segment_analysis import compute_segment_analysis


# ---------------------------------------------------------------------------
# Page configuration and visual constants
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Python BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY_COLOR = "#2D6A9F"
SECONDARY_COLOR = "#48A999"
ACCENT_COLOR = "#E8855A"
TREND_COLOR = "#8E6BBF"
HIGHLIGHT_COLOR = "#E8C25A"

PALETTE = [
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR,
    TREND_COLOR,
    HIGHLIGHT_COLOR,
]

STATUS_COLORS = {
    "Won": SECONDARY_COLOR,
    "Lost": ACCENT_COLOR,
    "Churned": TREND_COLOR,
}

SEVERITY_COLORS = {
    "critical": "#E8855A",
    "warning": "#E8C25A",
    "info": "#2D6A9F",
    "good": "#48A999",
}

SEVERITY_ICONS = {
    "critical": "🔴",
    "warning": "🟡",
    "info": "🔵",
    "good": "🟢",
}


UI_TEXT = {
    "en": {
        "page_title": "Python BI Reporting & Decision Support Dashboard",
        "page_caption": (
            "Interactive CRM analytics with live filtering, KPI reporting, "
            "forecasting, and automated decision support."
        ),
        "filters": "Filters",
        "language": "Language",
        "region": "Region",
        "year": "Year",
        "segment": "Customer Segment",
        "product": "Product",
        "all": "All",
        "scope": "Analysis Scope",
        "full_dataset": "Complete CRM dataset",
        "orders": "orders",
        "customers": "customers",
        "date_range": "Date range",
        "kpis": "Key Performance Indicators",
        "total_revenue": "Total Revenue",
        "avg_order_value": "Average Order Value",
        "win_rate": "Win Rate",
        "churn_rate": "Churn-Status Rate",
        "mom_growth": "MoM Growth",
        "overall_trend": "Overall Trend",
        "matching_orders": "Matching Orders",
        "matching_customers": "Matching Customers",
        "analytics": "Visual Analytics",
        "monthly_revenue": "Monthly Revenue Trend",
        "regional_revenue": "Revenue by Region",
        "product_mix": "Revenue by Product",
        "status_breakdown": "Order Status Breakdown",
        "am_performance": "Account Manager Performance",
        "segment_performance": "Customer Segment Performance",
        "forecast": "Three-Month Revenue Forecast",
        "revenue": "Revenue",
        "count": "Count",
        "account_manager": "Account Manager",
        "win_rate_axis": "Win Rate (%)",
        "forecast_model": "Forecast Model",
        "slope": "Monthly Slope",
        "r_squared": "R²",
        "direction": "Direction",
        "forecast_table": "Forecast Values",
        "month": "Month",
        "forecast_revenue": "Forecast Revenue",
        "decision_support": "Decision Support Insights",
        "detail": "Detail",
        "action": "Action",
        "segment_summary": "Segment Summary",
        "highest_revenue_segment": "Highest Revenue Segment",
        "highest_revenue_per_customer": "Highest Revenue per Customer",
        "highest_win_rate_segment": "Highest Win Rate Segment",
        "lowest_churn_rate_segment": "Lowest Churn Rate Segment",
        "no_forecast": (
            "A forecast could not be created for this filter combination "
            "because at least two monthly revenue records are required."
        ),
        "no_data": "No data matched the selected filters.",
        "footer": "Internship Project · KivaCRM · Developed by Salsabeel Alfayoumi",
        "actual_revenue": "Actual Revenue",
        "linear_trend": "Linear Trend",
        "forecast_label": "Forecast",
    },
    "tr": {
        "page_title": "Python İş Zekâsı Raporlama ve Karar Destek Paneli",
        "page_caption": (
            "Canlı filtreleme, KPI raporlama, gelir tahmini ve otomatik "
            "karar desteği sunan etkileşimli CRM analitiği."
        ),
        "filters": "Filtreler",
        "language": "Dil",
        "region": "Bölge",
        "year": "Yıl",
        "segment": "Müşteri Segmenti",
        "product": "Ürün",
        "all": "Tümü",
        "scope": "Analiz Kapsamı",
        "full_dataset": "Tüm CRM veri seti",
        "orders": "sipariş",
        "customers": "müşteri",
        "date_range": "Tarih aralığı",
        "kpis": "Temel Performans Göstergeleri",
        "total_revenue": "Toplam Gelir",
        "avg_order_value": "Ortalama Sipariş Değeri",
        "win_rate": "Kazanma Oranı",
        "churn_rate": "Churn Durum Oranı",
        "mom_growth": "Aylık Gelir Değişimi",
        "overall_trend": "Genel Trend",
        "matching_orders": "Eşleşen Siparişler",
        "matching_customers": "Eşleşen Müşteriler",
        "analytics": "Görsel Analizler",
        "monthly_revenue": "Aylık Gelir Trendi",
        "regional_revenue": "Bölgelere Göre Gelir",
        "product_mix": "Ürünlere Göre Gelir",
        "status_breakdown": "Sipariş Durum Dağılımı",
        "am_performance": "Müşteri Temsilcisi Performansı",
        "segment_performance": "Müşteri Segmenti Performansı",
        "forecast": "Üç Aylık Gelir Tahmini",
        "revenue": "Gelir",
        "count": "Adet",
        "account_manager": "Müşteri Temsilcisi",
        "win_rate_axis": "Kazanma Oranı (%)",
        "forecast_model": "Tahmin Modeli",
        "slope": "Aylık Eğim",
        "r_squared": "R²",
        "direction": "Yön",
        "forecast_table": "Tahmin Değerleri",
        "month": "Ay",
        "forecast_revenue": "Tahmini Gelir",
        "decision_support": "Karar Destek İçgörüleri",
        "detail": "Detay",
        "action": "Aksiyon",
        "segment_summary": "Segment Özeti",
        "highest_revenue_segment": "En Yüksek Gelir Segmenti",
        "highest_revenue_per_customer": "Müşteri Başına En Yüksek Gelir",
        "highest_win_rate_segment": "En Yüksek Kazanma Oranı",
        "lowest_churn_rate_segment": "En Düşük Churn Oranı",
        "no_forecast": (
            "Bu filtre kombinasyonu için tahmin oluşturulamadı. "
            "Doğrusal tahmin için en az iki aylık gelir kaydı gereklidir."
        ),
        "no_data": "Seçilen filtrelerle eşleşen veri bulunamadı.",
        "footer": "Staj Projesi · KivaCRM · Geliştiren: Salsabeel Alfayoumi",
        "actual_revenue": "Gerçekleşen Gelir",
        "linear_trend": "Doğrusal Trend",
        "forecast_label": "Tahmin",
    },
}


# ---------------------------------------------------------------------------
# Styling and shared helpers
# ---------------------------------------------------------------------------
def apply_custom_css() -> None:
    """Apply lightweight dashboard styling."""

    st.markdown(
        """
        <style>
            .stApp {
                background: #F4F7FB;
            }

            [data-testid="stSidebar"] {
                background: #EAF0F7;
                border-right: 1px solid #D4DEEA;
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 3rem;
                max-width: 1500px;
            }

            h1, h2, h3 {
                color: #173F63;
            }

            div[data-testid="stMetric"] {
                background: white;
                border: 1px solid #DCE5EF;
                border-radius: 14px;
                padding: 16px 18px;
                box-shadow: 0 5px 16px rgba(23, 63, 99, 0.06);
            }

            div[data-testid="stMetricLabel"] {
                color: #62758A;
            }

            .scope-card {
                background: #E7F1FB;
                border: 1px solid #CFE0F2;
                border-radius: 12px;
                padding: 14px 18px;
                color: #174A78;
                margin-bottom: 1rem;
            }

            .summary-card {
                background: white;
                border: 1px solid #DCE5EF;
                border-radius: 12px;
                padding: 14px 16px;
                min-height: 112px;
                box-shadow: 0 4px 12px rgba(23, 63, 99, 0.05);
            }

            .summary-label {
                color: #6A7D91;
                font-size: 0.82rem;
                margin-bottom: 8px;
            }

            .summary-value {
                color: #173F63;
                font-size: 1.15rem;
                font-weight: 700;
            }

            .insight-card {
                background: white;
                border: 1px solid #DCE5EF;
                border-radius: 12px;
                padding: 14px 16px;
                margin-bottom: 12px;
                box-shadow: 0 4px 12px rgba(23, 63, 99, 0.05);
            }

            .insight-title {
                color: #173F63;
                font-size: 1rem;
                font-weight: 700;
                margin-bottom: 8px;
            }

            .insight-text {
                color: #435970;
                line-height: 1.5;
                margin: 4px 0;
            }

            .footer {
                color: #7A8DA1;
                text-align: center;
                font-size: 0.85rem;
                padding-top: 2rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def text(language: str, key: str) -> str:
    """Return one interface label."""

    return UI_TEXT[language][key]


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
    """Apply consistent Streamlit-friendly Plotly styling."""

    figure.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin={
            "l": 55,
            "r": 35,
            "t": 65,
            "b": 55,
        },
        font={
            "family": "Segoe UI, Arial, sans-serif",
            "color": "#173F63",
        },
        showlegend=showlegend,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        hoverlabel={
            "bgcolor": "white",
            "font_color": "#173F63",
        },
    )

    figure.update_xaxes(
        automargin=True,
        showgrid=False,
        zeroline=False,
    )

    figure.update_yaxes(
        automargin=True,
        gridcolor="rgba(23,63,99,0.10)",
        zeroline=False,
    )

    return figure


@st.cache_data
def load_source_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load source datasets once and cache them for Streamlit reruns."""

    return load_data()


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
                f"{value:.1f}%"
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
                    <div class="summary-label">{label}</div>
                    <div class="summary-value">{value}</div>
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
                    {icon} [{insight.category}] {insight.title}
                </div>
                <div class="insight-text">
                    <strong>{text(language, "detail")}:</strong>
                    {insight.detail}
                </div>
                <div class="insight-text">
                    <strong>▶ {text(language, "action")}:</strong>
                    {insight.action}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    """Run the complete interactive Streamlit dashboard."""

    apply_custom_css()

    raw_orders, raw_customers = load_source_data()

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
        kpis = compute_all_kpis(
            orders=raw_orders,
            customers=raw_customers,
            region=selected_region,
            year=selected_year,
            segment=selected_segment,
            product=selected_product,
            print_validation_report=False,
        )
    except ValueError as error:
        st.error(
            f"{text(language, 'no_data')} {error}"
        )
        st.stop()

    filtered_orders = kpis["_data"]["orders"]
    filtered_customers = kpis["_data"]["customers"]

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
            <strong>{scope_name}</strong><br>
            {kpis['meta']['total_orders']:,}
            {text(language, 'orders')}
            &nbsp; · &nbsp;
            {kpis['meta']['total_customers']:,}
            {text(language, 'customers')}
            &nbsp; · &nbsp;
            {text(language, 'date_range')}:
            {kpis['meta']['date_range']}
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
            f"{revenue['mom_growth_pct']:+.1f}% MoM"
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
        f"{sales['churn_rate_pct']:.2f}%",
        delta=(
            f"{sales['churn_rate_pct'] - 10:+.1f}% "
            "vs target"
        ),
        delta_color="inverse",
    )

    second_row = st.columns(4)

    second_row[0].metric(
        text(language, "mom_growth"),
        f"{revenue['mom_growth_pct']:+.2f}%",
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
        use_container_width=True,
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
            use_container_width=True,
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
            use_container_width=True,
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
            use_container_width=True,
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
            use_container_width=True,
            config={
                "displaylogo": False,
            },
        )

    st.plotly_chart(
        segment_performance_figure(
            segment_analysis,
            language,
        ),
        use_container_width=True,
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

        model_columns[2].metric(
            text(language, "r_squared"),
            f"{forecast_model['r_squared']:.4f}",
        )

        model_columns[3].metric(
            text(language, "direction"),
            forecast_model["direction"],
        )

        st.plotly_chart(
            forecast_figure(
                revenue_forecast,
                language,
            ),
            use_container_width=True,
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
            use_container_width=True,
            hide_index=True,
        )

    st.markdown(
        f"""
        <div class="footer">
            {text(language, "footer")}
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()