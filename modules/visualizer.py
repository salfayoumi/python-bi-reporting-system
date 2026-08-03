"""
modules/visualizer.py

Generates localized charts and saves them to reports/charts/.

Matplotlib is used for static PNG export, while Plotly is used
for interactive HTML visualizations.
"""

from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from modules.i18n import (
    DEFAULT_LANGUAGE,
    normalize_language,
    translate,
)


Translator = Callable[[str], str]

CHART_DIR = Path("reports/charts")
DEFAULT_ORDERS_PATH = Path("data/orders.csv")

LINE_CHART_FIGSIZE = (12, 5.4)
BAR_CHART_FIGSIZE = (9, 5.4)
MATPLOTLIB_DPI = 150
PLOTLY_TITLE_FONT_SIZE = 16

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

PLOTLY_FONT_FAMILY = "Segoe UI, Arial, sans-serif"
PLOTLY_HEIGHT = 520
PLOTLY_MARGIN = {
    "t": 100,
    "r": 70,
    "b": 70,
    "l": 80,
}

PLOTLY_CONFIG = {
    "responsive": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "lasso2d",
        "select2d",
    ],
}


def _apply_plotly_layout(
    fig: go.Figure,
    *,
    title: str,
    xaxis_title: str | None = None,
    yaxis_title: str | None = None,
    showlegend: bool = True,
    legend_y: float = 1.0,
    height: int = PLOTLY_HEIGHT,
    margin: dict | None = None,
    hovermode: str | None = None,
) -> None:
    """Apply a consistent responsive layout to Plotly charts."""

    resolved_margin = {
        **PLOTLY_MARGIN,
        **(margin or {}),
    }

    layout_kwargs = {
        "title": {
            "text": title,
            "x": 0.02,
            "xanchor": "left",
            "y": 0.97,
            "yanchor": "top",
            "font": {
                "size": PLOTLY_TITLE_FONT_SIZE,
                "color": "#173F63",
            },
        },
        "font": {
            "family": PLOTLY_FONT_FAMILY,
            "color": "#173F63",
        },
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "showlegend": showlegend,
        "height": height,
        "margin": resolved_margin,
    }

    if xaxis_title is not None:
        layout_kwargs["xaxis_title"] = xaxis_title

    if yaxis_title is not None:
        layout_kwargs["yaxis_title"] = yaxis_title

    if hovermode is not None:
        layout_kwargs["hovermode"] = hovermode

    if showlegend:
        layout_kwargs["legend"] = {
            "font": {
                "size": 11,
            },
            "bgcolor": "rgba(255,255,255,0)",
            "borderwidth": 0,
            "itemsizing": "constant",
            "traceorder": "normal",
        }

    fig.update_layout(**layout_kwargs)

    fig.update_xaxes(
        automargin=True,
        showgrid=False,
        zeroline=False,
        tickfont={
            "size": 11,
        },
        title_standoff=14,
    )

    fig.update_yaxes(
        automargin=True,
        gridcolor="rgba(23,63,99,0.10)",
        zeroline=False,
        tickfont={
            "size": 11,
        },
        title_standoff=14,
    )


def _write_plotly_html(
    fig: go.Figure,
    path: str,
) -> None:
    """Write a responsive standalone Plotly HTML file."""

    fig.write_html(
        path,
        full_html=True,
        include_plotlyjs=True,
        config=PLOTLY_CONFIG,
    )


def _get_translator(
    language: str,
) -> tuple[str, Translator]:
    """Normalize a language code and return its translator."""

    normalized_language = normalize_language(
        language
    )

    def translator(key: str) -> str:
        return translate(
            key,
            normalized_language,
        )

    return normalized_language, translator


def get_chart_path(
    filename: str,
    language: str,
) -> str:
    """Create a language-specific chart output path."""

    CHART_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_path = Path(filename)

    output_path = CHART_DIR / (
        f"{source_path.stem}_"
        f"{language}"
        f"{source_path.suffix}"
    )

    return str(output_path)


# ── 1. Monthly Revenue Trend ──────────────────────────────────────────────────
def plot_monthly_trend(
    monthly_data: list,
    language: str = DEFAULT_LANGUAGE,
    save: bool = True,
) -> str:
    """Generate a localized monthly revenue trend chart."""

    language, t = _get_translator(
        language
    )

    df = pd.DataFrame(monthly_data)

    fig, ax = plt.subplots(
        figsize=LINE_CHART_FIGSIZE
    )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.fill_between(
        df["month"],
        df["revenue"],
        alpha=0.15,
        color=PRIMARY_COLOR,
    )

    ax.plot(
        df["month"],
        df["revenue"],
        color=PRIMARY_COLOR,
        linewidth=2.5,
        marker="o",
        markersize=4,
    )

    if not df.empty:
        ax.annotate(
            f'${df["revenue"].iloc[-1]:,.0f}',
            xy=(
                df["month"].iloc[-1],
                df["revenue"].iloc[-1],
            ),
            xytext=(0, 12),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color=PRIMARY_COLOR,
            fontweight="bold",
        )

    ax.yaxis.set_major_formatter(
        mtick.FuncFormatter(
            lambda value, _: (
                f"${value / 1000:.0f}K"
            )
        )
    )

    ax.set_title(
        t("chart.monthly_trend"),
        fontsize=14,
        fontweight="bold",
        pad=16,
    )

    ax.set_xlabel(
        t("chart.month")
    )

    ax.set_ylabel(
        t("chart.revenue_usd")
    )

    ax.tick_params(
        axis="x",
        rotation=45,
    )

    ax.grid(
        axis="y",
        alpha=0.22,
        linestyle="--",
    )

    ax.spines[
        ["top", "right"]
    ].set_visible(False)

    plt.tight_layout()

    path = get_chart_path(
        "monthly_trend.png",
        language,
    )

    if save:
        plt.savefig(
            path,
            dpi=MATPLOTLIB_DPI,
            bbox_inches="tight",
        )

        print(f"  ✓ {path}")

    plt.close(fig)

    return path


# ── 2. Product Revenue Mix ────────────────────────────────────────────────────
def plot_product_mix(
    product_revenue: dict,
    language: str = DEFAULT_LANGUAGE,
    save: bool = True,
) -> str:
    """Generate a localized product revenue pie chart."""

    language, t = _get_translator(
        language
    )

    product_column = t("chart.product")
    revenue_column = t("chart.revenue")

    df = pd.DataFrame(
        list(product_revenue.items()),
        columns=[
            product_column,
            revenue_column,
        ],
    )

    fig = px.pie(
        df,
        names=product_column,
        values=revenue_column,
        color_discrete_sequence=PALETTE,
        title=t("chart.product_mix"),
        hole=0.4,
    )

    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        pull=[
            0.02
            for _ in range(len(df))
        ],
        marker={
            "line": {
                "color": "white",
                "width": 2,
            }
        },
        hovertemplate=(
            "<b>%{label}</b><br>"
            + t("chart.revenue")
            + ": $%{value:,.2f}<br>"
            + "%{percent}"
            + "<extra></extra>"
        ),
    )

    _apply_plotly_layout(
        fig,
        title=t("chart.product_mix"),
        showlegend=False,
        height=520,
        margin={
            "t": 78,
            "r": 90,
            "b": 45,
            "l": 90,
        },
    )

    path = get_chart_path(
        "product_mix.html",
        language,
    )

    if save:
        _write_plotly_html(
            fig,
            path,
        )
        print(f"  ✓ {path}")

    return path


# ── 3. Regional Revenue Bar Chart ─────────────────────────────────────────────
def plot_regional_revenue(
    regional_revenue: dict,
    language: str = DEFAULT_LANGUAGE,
    save: bool = True,
) -> str:
    """Generate a localized regional revenue chart."""

    language, t = _get_translator(
        language
    )

    df = pd.DataFrame(
        list(regional_revenue.items()),
        columns=[
            "region",
            "revenue",
        ],
    )

    df = df.sort_values(
        "revenue",
        ascending=True,
    )

    fig, ax = plt.subplots(
        figsize=BAR_CHART_FIGSIZE
    )

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    bars = ax.barh(
        df["region"],
        df["revenue"],
        color=SECONDARY_COLOR,
        edgecolor="white",
    )

    for bar in bars:
        width = bar.get_width()

        ax.text(
            width + 5000,
            (
                bar.get_y()
                + bar.get_height() / 2
            ),
            f"${width:,.0f}",
            va="center",
            fontsize=9,
        )

    ax.xaxis.set_major_formatter(
        mtick.FuncFormatter(
            lambda value, _: (
                f"${value / 1000:.0f}K"
            )
        )
    )

    ax.set_title(
        t("chart.regional_revenue"),
        fontsize=14,
        fontweight="bold",
        pad=16,
    )

    ax.set_xlabel(
        t("chart.revenue_usd")
    )

    ax.spines[
        ["top", "right"]
    ].set_visible(False)

    ax.grid(
        axis="x",
        alpha=0.22,
        linestyle="--",
    )

    plt.tight_layout()

    path = get_chart_path(
        "regional_revenue.png",
        language,
    )

    if save:
        plt.savefig(
            path,
            dpi=MATPLOTLIB_DPI,
            bbox_inches="tight",
        )

        print(f"  ✓ {path}")

    plt.close(fig)

    return path


# ── 4. Order Status Breakdown ─────────────────────────────────────────────────
def plot_status_breakdown(
    orders_path: str | Path = DEFAULT_ORDERS_PATH,
    language: str = DEFAULT_LANGUAGE,
    save: bool = True,
) -> str:
    """Generate a localized order-status chart."""

    language, t = _get_translator(
        language
    )

    orders = pd.read_csv(
        orders_path
    )

    counts = (
        orders["status"]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "status",
        "count",
    ]

    color_map = STATUS_COLORS

    fig = px.bar(
        counts,
        x="status",
        y="count",
        color="status",
        color_discrete_map=color_map,
        title=t(
            "chart.status_breakdown"
        ),
        text="count",
        labels={
            "status": t("chart.status"),
            "count": t("chart.count"),
        },
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker={
            "line": {
                "color": "white",
                "width": 1.5,
            }
        },
        hovertemplate=(
            "<b>%{x}</b><br>"
            + t("chart.count")
            + ": %{y}"
            + "<extra></extra>"
        ),
    )

    _apply_plotly_layout(
        fig,
        title=t("chart.status_breakdown"),
        xaxis_title=t("chart.status"),
        yaxis_title=t("chart.count"),
        showlegend=False,
        height=500,
        margin={
            "t": 78,
            "r": 40,
            "b": 75,
            "l": 70,
        },
    )

    fig.update_yaxes(
        rangemode="tozero",
    )

    path = get_chart_path(
        "status_breakdown.html",
        language,
    )

    if save:
        _write_plotly_html(
            fig,
            path,
        )
        print(f"  ✓ {path}")

    return path


# ── 5. Account Manager Performance ────────────────────────────────────────────
def plot_am_performance(
    orders_path: str | Path = DEFAULT_ORDERS_PATH,
    language: str = DEFAULT_LANGUAGE,
    save: bool = True,
) -> str:
    """Generate a localized account-manager chart."""

    language, t = _get_translator(
        language
    )

    orders = pd.read_csv(
        orders_path
    )

    won = orders[
        orders["status"] == "Won"
    ]

    am_stats = (
        won.groupby(
            "account_manager"
        )
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

    fig = make_subplots(
        specs=[
            [
                {
                    "secondary_y": True,
                }
            ]
        ]
    )

    fig.add_trace(
        go.Bar(
            name=t("chart.revenue"),
            x=am_stats[
                "account_manager"
            ],
            y=am_stats["revenue"],
            marker_color=PRIMARY_COLOR,
            hovertemplate=(
                "%{x}<br>"
                + t("chart.revenue")
                + ": $%{y:,.2f}"
                + "<extra></extra>"
            ),
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            name=t("chart.orders"),
            x=am_stats[
                "account_manager"
            ],
            y=am_stats["orders"],
            mode="lines+markers",
            marker_color=ACCENT_COLOR,
            hovertemplate=(
                "%{x}<br>"
                + t("chart.orders")
                + ": %{y}"
                + "<extra></extra>"
            ),
        ),
        secondary_y=True,
    )

    _apply_plotly_layout(
        fig,
        title=t("chart.am_performance"),
        xaxis_title=t("chart.account_manager"),
        showlegend=True,
        height=560,
        margin={
            "t": 88,
            "r": 90,
            "b": 135,
            "l": 85,
        },
        hovermode="x unified",
    )

    fig.update_layout(
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.22,
            "xanchor": "center",
            "x": 0.5,
            "font": {
                "size": 11,
            },
            "bgcolor": "rgba(255,255,255,0)",
            "borderwidth": 0,
            "itemsizing": "constant",
            "traceorder": "normal",
        }
    )

    fig.update_traces(
        selector={
            "type": "bar",
        },
        marker_line_color="white",
        marker_line_width=1.2,
        opacity=0.95,
    )

    fig.update_traces(
        selector={
            "type": "scatter",
        },
        line={
            "width": 3,
        },
        marker={
            "size": 8,
        },
    )

    fig.update_xaxes(
        tickangle=-25,
    )

    fig.update_yaxes(
        title_text=t("chart.revenue_usd"),
        secondary_y=False,
        tickprefix="$",
        tickformat=",.0f",
        rangemode="tozero",
    )

    fig.update_yaxes(
        title_text=t("chart.orders"),
        secondary_y=True,
        rangemode="tozero",
        showgrid=False,
    )

    path = get_chart_path(
        "am_performance.html",
        language,
    )

    if save:
        _write_plotly_html(
            fig,
            path,
        )
        print(f"  ✓ {path}")

    return path


# ── 6. Customer Segment Performance ──────────────────────────────────────────
def plot_segment_performance(
    segment_analysis: dict,
    language: str = DEFAULT_LANGUAGE,
    save: bool = True,
) -> str:
    """
    Generate an interactive dual-axis chart comparing segment
    revenue and win rate.
    """

    language, t = _get_translator(
        language
    )

    performance = segment_analysis.get(
        "performance",
        {},
    )

    records = []

    for segment, values in performance.items():
        records.append(
            {
                "segment": segment,
                "revenue": values[
                    "total_revenue"
                ],
                "win_rate": values[
                    "win_rate_pct"
                ],
                "revenue_per_customer": values[
                    "revenue_per_customer"
                ],
                "churn_rate": values[
                    "churn_rate_pct"
                ],
            }
        )

    df = pd.DataFrame(records)

    fig = make_subplots(
        specs=[
            [
                {
                    "secondary_y": True,
                }
            ]
        ]
    )

    fig.add_trace(
        go.Bar(
            name=t("chart.revenue"),
            x=df["segment"],
            y=df["revenue"],
            marker_color=PRIMARY_COLOR,
            text=[
                f"${value:,.0f}"
                for value in df["revenue"]
            ],
            textposition="outside",
            customdata=df[
                [
                    "revenue_per_customer",
                    "churn_rate",
                ]
            ],
            hovertemplate=(
                "<b>%{x}</b><br>"
                + t("chart.revenue")
                + ": $%{y:,.2f}<br>"
                + "Revenue / Customer"
                + ": $%{customdata[0]:,.2f}<br>"
                + "Churn Rate"
                + ": %{customdata[1]:.2f}%"
                + "<extra></extra>"
            ),
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            name=t("chart.win_rate"),
            x=df["segment"],
            y=df["win_rate"],
            mode="lines+markers+text",
            marker=dict(
                color=ACCENT_COLOR,
                size=10,
            ),
            line=dict(
                color=ACCENT_COLOR,
                width=3,
            ),
            text=[
                f"{value:.2f}%"
                for value in df["win_rate"]
            ],
            textposition="top center",
            hovertemplate=(
                "<b>%{x}</b><br>"
                + t("chart.win_rate")
                + ": %{y:.2f}%"
                + "<extra></extra>"
            ),
        ),
        secondary_y=True,
    )

    _apply_plotly_layout(
        fig,
        title=t("chart.segment_performance"),
        xaxis_title=t("chart.segment"),
        showlegend=True,
        height=540,
        margin={
            "t": 88,
            "r": 300,
            "b": 80,
            "l": 85,
        },
        hovermode="x unified",
    )

    fig.update_layout(
        legend={
            "orientation": "v",
            "yanchor": "top",
            "y": 0.98,
            "xanchor": "left",
            "x": 1.02,
            "font": {
                "size": 11,
            },
            "bgcolor": "rgba(255,255,255,0)",
            "borderwidth": 0,
            "itemsizing": "constant",
            "traceorder": "normal",
        }
    )

    fig.update_traces(
        selector={
            "type": "bar",
        },
        cliponaxis=False,
        marker_line_color="white",
        marker_line_width=1.2,
        opacity=0.95,
    )

    fig.update_yaxes(
        title_text=t("chart.revenue_usd"),
        secondary_y=False,
        tickprefix="$",
        tickformat=",.0f",
        rangemode="tozero",
    )

    fig.update_yaxes(
        title_text=t("chart.win_rate"),
        secondary_y=True,
        ticksuffix="%",
        range=[0, 100],
        showgrid=False,
    )

    path = get_chart_path(
        "segment_performance.html",
        language,
    )

    if save:
        _write_plotly_html(
            fig,
            path,
        )
        print(f"  ✓ {path}")

    return path


# ── 7. Revenue Forecast ──────────────────────────────────────────────────────
def plot_revenue_forecast(
    revenue_forecast: dict,
    language: str = DEFAULT_LANGUAGE,
    save: bool = True,
) -> str:
    """
    Generate a localized interactive chart showing historical
    revenue, fitted trend values, and future revenue forecasts.
    """

    language, t = _get_translator(
        language
    )

    historical = revenue_forecast.get(
        "historical",
        [],
    )

    forecast = revenue_forecast.get(
        "forecast",
        [],
    )

    model = revenue_forecast.get(
        "model",
        {},
    )

    historical_df = pd.DataFrame(
        historical
    )

    forecast_df = pd.DataFrame(
        forecast
    )

    if historical_df.empty:
        raise ValueError(
            "Historical revenue data is required "
            "to generate the forecast chart."
        )

    if forecast_df.empty:
        raise ValueError(
            "Forecast revenue data is required "
            "to generate the forecast chart."
        )

    historical_df["month"] = (
        historical_df["month"].astype(str)
    )

    forecast_df["month"] = (
        forecast_df["month"].astype(str)
    )

    fig = go.Figure()

    # Historical monthly revenue
    fig.add_trace(
        go.Scatter(
            name=t("chart.actual_revenue"),
            x=historical_df["month"],
            y=historical_df["revenue"],
            mode="lines+markers",
            line=dict(
                color=PRIMARY_COLOR,
                width=2,
            ),
            marker=dict(
                color=PRIMARY_COLOR,
                size=7,
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                + t("chart.actual_revenue")
                + ": $%{y:,.2f}"
                + "<extra></extra>"
            ),
        )
    )

    # Historical fitted linear trend
    fig.add_trace(
        go.Scatter(
            name=t("chart.linear_trend"),
            x=historical_df["month"],
            y=historical_df["trend_value"],
            mode="lines",
            line=dict(
                color=TREND_COLOR,
                width=2,
                dash="dash",
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                + t("chart.linear_trend")
                + ": $%{y:,.2f}"
                + "<extra></extra>"
            ),
        )
    )

    # Connect the forecast to the final fitted trend value.
    forecast_x = [
        historical_df["month"].iloc[-1],
        *forecast_df["month"].tolist(),
    ]

    forecast_y = [
        historical_df[
            "trend_value"
        ].iloc[-1],
        *forecast_df[
            "forecast_revenue"
        ].tolist(),
    ]

    fig.add_trace(
        go.Scatter(
            name=t("chart.forecast"),
            x=forecast_x,
            y=forecast_y,
            mode="lines+markers",
            line=dict(
                color=ACCENT_COLOR,
                width=4,
                dash="dot",
            ),
            marker=dict(
                color=ACCENT_COLOR,
                size=9,
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                + t("chart.forecast")
                + ": $%{y:,.2f}"
                + "<extra></extra>"
            ),
        )
    )

    forecast_start_month = (
        forecast_df["month"].iloc[0]
    )

    fig.add_vline(
        x=forecast_start_month,
        line_width=3,
        line_dash="dash",
        line_color=HIGHLIGHT_COLOR,
    )

    fig.add_annotation(
        x=forecast_start_month,
        y=1,
        yref="paper",
        text=t(
            "chart.forecast_start"
        ),
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font=dict(
            size=11,
        ),
    )

    r_squared = float(
        model.get(
            "r_squared",
            0,
        )
    )

    model_name = model.get(
        "name",
        "Linear Regression",
    )

    model_method = model.get(
        "method",
        "NumPy polyfit",
    )

    forecast_months = model.get(
        "forecast_months",
        3,
    )

    direction = model.get(
        "direction",
        "",
    )

    if language == "tr":
        direction_labels = {
            "Growing": "Büyüyen",
            "Declining": "Düşen",
            "Stable": "Sabit",
        }

        localized_direction = (
            direction_labels.get(
                direction,
                direction,
            )
        )

        forecast_horizon_text = (
            f"{forecast_months} Aylık Tahmin"
        )

        trend_text = (
            f"Trend: {localized_direction}"
        )

    else:
        localized_direction = direction

        forecast_horizon_text = (
            f"{forecast_months}-Month Forecast"
        )

        trend_text = (
            f"Trend: {localized_direction}"
        )

    subtitle = (
        f"{model_name} ({model_method})"
        f" · R² = {r_squared:.4f}"
        f" · {trend_text}"
        f" · {forecast_horizon_text}"
    )

    _apply_plotly_layout(
        fig,
        title=(
            f"{t('chart.revenue_forecast')}"
            f"<br><sup>{subtitle}</sup>"
        ),
        xaxis_title=t("chart.month"),
        yaxis_title=t("chart.revenue_usd"),
        showlegend=True,
        height=560,
        margin={
            "t": 118,
            "r": 340,
            "b": 90,
            "l": 85,
        },
        hovermode="x unified",
    )

    fig.update_layout(
        legend={
            "orientation": "v",
            "yanchor": "top",
            "y": 0.98,
            "xanchor": "left",
            "x": 1.02,
            "font": {
                "size": 11,
            },
            "bgcolor": "rgba(255,255,255,0)",
            "borderwidth": 0,
            "itemsizing": "constant",
            "traceorder": "normal",
        }
    )

    fig.update_yaxes(
        tickprefix="$",
        tickformat=",.0f",
        rangemode="tozero",
    )

    fig.update_xaxes(
        tickangle=-40,
        nticks=12,
    )

    path = get_chart_path(
        "revenue_forecast.html",
        language,
    )

    if save:
        _write_plotly_html(
            fig,
            path,
        )
        print(f"  ✓ {path}")

    return path


# ── Master Runner ─────────────────────────────────────────────────────────────
def generate_all_charts(
    kpis: dict,
    segment_analysis: dict,
    revenue_forecast: dict,
    language: str = DEFAULT_LANGUAGE,
) -> dict:
    """Generate all charts for one language."""

    language = normalize_language(
        language
    )

    print(
        "\n📊 "
        + translate(
            "visualizer.generating",
            language,
        )
    )

    paths = {}

    paths["monthly_trend"] = (
        plot_monthly_trend(
            kpis[
                "trends"
            ][
                "monthly_revenue"
            ],
            language=language,
        )
    )

    paths["product_mix"] = (
        plot_product_mix(
            kpis[
                "products"
            ][
                "product_revenue"
            ],
            language=language,
        )
    )

    paths["regional_revenue"] = (
        plot_regional_revenue(
            kpis[
                "regions"
            ][
                "regional_revenue"
            ],
            language=language,
        )
    )

    paths["status_breakdown"] = (
        plot_status_breakdown(
            language=language,
        )
    )

    paths["am_performance"] = (
        plot_am_performance(
            language=language,
        )
    )

    paths["segment_performance"] = (
        plot_segment_performance(
            segment_analysis,
            language=language,
        )
    )

    paths["revenue_forecast"] = (
        plot_revenue_forecast(
            revenue_forecast,
            language=language,
        )
    )

    return paths


def generate_bilingual_charts(
    kpis: dict,
    segment_analysis: dict,
    revenue_forecast: dict,
) -> dict:
    """Generate English and Turkish chart collections."""

    return {
        "en": generate_all_charts(
            kpis,
            segment_analysis,
            revenue_forecast,
            language="en",
        ),
        "tr": generate_all_charts(
            kpis,
            segment_analysis,
            revenue_forecast,
            language="tr",
        ),
    }