"""
modules/report_generator.py

Generates a polished bilingual BI dashboard containing:
- application-style sidebar navigation
- localized KPI cards
- localized decision-support insights
- English and Turkish chart versions
- customer-segment and forecast pages
- an in-browser language switch

The generated dashboard has no Python dependency after creation.
"""

from datetime import datetime
from html import escape
from pathlib import Path

from modules.i18n import translate


REPORT_DIR = Path("reports")

SEVERITY_COLOR = {
    "critical": "#E8855A",
    "warning": "#E8C25A",
    "good": "#48A999",
    "info": "#2D6A9F",
}

SEVERITY_ICON = {
    "critical": "🔴",
    "warning": "🟡",
    "good": "🟢",
    "info": "🔵",
}

UI_TEXT = {
    "en": {
        "app_name": "BI Dashboard",
        "app_subtitle": "Internship Project · KivaCRM",
        "analytics": "Analytics",
        "reports": "Reports",
        "overview": "Overview",
        "insights": "Decision Insights",
        "performance": "Performance Analytics",
        "segments": "Segment Analysis",
        "forecast": "Revenue Forecast",
        "period": "Reporting period",
        "generated": "Generated",
        "executive_summary": "Executive Summary",
        "executive_summary_sub": "Highest-priority findings from the decision-support engine",
        "kpis": "Key Performance Indicators",
        "overview_charts": "Business Overview",
        "performance_charts": "Sales & Operational Performance",
        "segment_title": "Customer Segment Analysis",
        "segment_sub": "Compare revenue contribution, conversion, and customer value by segment.",
        "forecast_title": "Three-Month Revenue Forecast",
        "forecast_sub": "A linear baseline intended as a directional estimate rather than a guaranteed prediction.",
        "all_insights": "All Decision-Support Insights",
        "all_insights_sub": "Prioritized findings and recommended actions generated from KPI thresholds.",
        "footer": "Python BI Module — Internship Project · KivaCRM",
        "monthly_revenue": "Monthly Revenue Trend",
        "regional_revenue": "Revenue by Region",
        "product_mix": "Revenue by Product",
        "status_breakdown": "Order Status Breakdown",
        "am_performance": "Account Manager Performance",
        "segment_performance": "Customer Segment Performance",
        "revenue_forecast": "Three-Month Revenue Forecast",
        "critical_count": "Critical findings",
        "positive_count": "Positive findings",
        "trend_label": "Trend",
        "top_product": "Top product",
        "top_region": "Top region",
        "dataset_snapshot": "Dataset Snapshot",
        "products": "Products",
        "regions": "Regions",
        "won_orders": "Won orders",
        "forecast_model": "Forecast Model",
        "model_name": "Model",
        "forecast_horizon": "Forecast horizon",
        "three_months": "3 months",
        "model_interpretation": "Interpretation",
        "directional_only": "Directional baseline; not a guaranteed prediction",
        "forecast_explanation": (
            "This forecast is derived from historical monthly revenue using "
            "a simple linear trend and should be interpreted as a directional "
            "estimate rather than a precise prediction."
        ),
        "segment_highlights": "Segment Highlights",
        "segment_note": (
            "Revenue, conversion, and churn should be assessed "
            "together rather than in isolation."
        ),
        "historical_performance": "Historical performance across the reporting period",
        "regional_comparison": "Comparison of won-order revenue by region",
        "product_distribution": "Revenue concentration across products",
        "status_distribution": "Distribution of Won, Lost, and Churned records",
        "manager_comparison": "Revenue and won-order volume by account manager",
        "segment_comparison": "Revenue contribution and win rate by customer segment",
        "forecast_comparison": "Historical revenue, fitted trend, and next three months",
        "overview_highlights": "Executive Alerts",
        "high_priority": "High priority",
        "investigate": "Needs investigation",
        "on_track": "On track",
        "dataset": "Dataset",
        "months": "months",
        "generated_by": "Generated",
        "revenue_status": "Revenue status",
        "sales_status": "Sales status",
        "retention_status": "Retention status",
        "declining": "Declining",
        "healthy": "Healthy",
        "needs_attention": "Needs attention",
        "exact_value": "Exact value",
        "confidence": "Confidence",
        "low": "Low",
        "slope": "Monthly slope",
        "r_squared": "R²",
        "best_revenue_segment": "Highest revenue segment",
        "best_value_segment": "Highest revenue per customer",
        "best_conversion_segment": "Highest win rate segment",
        "best_retention_segment": "Lowest churn segment",
        "developed_by": "Developed by",
        "author": "Salsabeel Alfayoumi",
        "critical": "Critical",
        "warning": "Warning",
        "good": "Good",
        "info": "Info",
    },
    "tr": {
        "app_name": "İş Zekâsı Paneli",
        "app_subtitle": "Staj Projesi · KivaCRM",
        "analytics": "Analizler",
        "reports": "Raporlar",
        "overview": "Genel Bakış",
        "insights": "Karar Destek İçgörüleri",
        "performance": "Performans Analizleri",
        "segments": "Segment Analizi",
        "forecast": "Gelir Tahmini",
        "period": "Raporlama dönemi",
        "generated": "Oluşturulma",
        "executive_summary": "Yönetici Özeti",
        "executive_summary_sub": "Karar destek motorunun en yüksek öncelikli bulguları",
        "kpis": "Temel Performans Göstergeleri",
        "overview_charts": "İşletme Genel Görünümü",
        "performance_charts": "Satış ve Operasyon Performansı",
        "segment_title": "Müşteri Segmenti Analizi",
        "segment_sub": "Segmentlere göre gelir katkısı, dönüşüm ve müşteri değerini karşılaştırın.",
        "forecast_title": "Üç Aylık Gelir Tahmini",
        "forecast_sub": "Kesin bir öngörü değil, yön gösterici temel tahmin olarak değerlendirilmelidir.",
        "all_insights": "Tüm Karar Destek İçgörüleri",
        "all_insights_sub": "KPI eşiklerinden üretilen önceliklendirilmiş bulgular ve önerilen aksiyonlar.",
        "footer": "Python İş Zekâsı Modülü — Staj Projesi · KivaCRM",
        "monthly_revenue": "Aylık Gelir Trendi",
        "regional_revenue": "Bölge Bazında Gelir",
        "product_mix": "Ürün Bazında Gelir",
        "status_breakdown": "Sipariş Durumu Dağılımı",
        "am_performance": "Müşteri Temsilcisi Performansı",
        "segment_performance": "Müşteri Segmenti Performansı",
        "revenue_forecast": "Üç Aylık Gelir Tahmini",
        "critical_count": "Kritik bulgu",
        "positive_count": "Olumlu bulgu",
        "trend_label": "Trend",
        "top_product": "En başarılı ürün",
        "top_region": "En başarılı bölge",
        "dataset_snapshot": "Veri Seti Özeti",
        "products": "Ürünler",
        "regions": "Bölgeler",
        "won_orders": "Kazanılan siparişler",
        "forecast_model": "Tahmin Modeli",
        "model_name": "Model",
        "forecast_horizon": "Tahmin dönemi",
        "three_months": "3 ay",
        "model_interpretation": "Yorum",
        "directional_only": "Yön gösterici temel tahmindir; kesin öngörü değildir",
        "forecast_explanation": (
            "Bu tahmin, geçmiş aylık gelir verilerinden basit bir doğrusal trend "
            "kullanılarak oluşturulmuştur ve kesin bir öngörü yerine yön gösterici "
            "bir tahmin olarak değerlendirilmelidir."
        ),
        "segment_highlights": "Segment Özeti",
        "segment_note": (
            "Gelir, dönüşüm ve churn göstergeleri birbirinden "
            "bağımsız değil, birlikte değerlendirilmelidir."
        ),
        "historical_performance": "Raporlama dönemindeki tarihsel performans",
        "regional_comparison": "Bölgelere göre kazanılan sipariş geliri karşılaştırması",
        "product_distribution": "Ürünlere göre gelir yoğunluğu",
        "status_distribution": "Kazanılan, kaybedilen ve churn durumundaki kayıtların dağılımı",
        "manager_comparison": "Müşteri temsilcilerine göre gelir ve kazanılan sipariş hacmi",
        "segment_comparison": "Müşteri segmentlerine göre gelir katkısı ve kazanma oranı",
        "forecast_comparison": "Gerçekleşen gelir, doğrusal trend ve sonraki üç ay",
        "overview_highlights": "Yönetici Uyarıları",
        "high_priority": "Yüksek öncelik",
        "investigate": "İncelenmesi gerekli",
        "on_track": "Hedef doğrultusunda",
        "dataset": "Veri seti",
        "months": "ay",
        "generated_by": "Oluşturulma",
        "revenue_status": "Gelir durumu",
        "sales_status": "Satış durumu",
        "retention_status": "Müşteri tutundurma durumu",
        "declining": "Düşüşte",
        "healthy": "Sağlıklı",
        "needs_attention": "İyileştirme gerekli",
        "exact_value": "Kesin değer",
        "confidence": "Güven düzeyi",
        "low": "Düşük",
        "slope": "Aylık eğim",
        "r_squared": "R²",
        "best_revenue_segment": "En yüksek gelir segmenti",
        "best_value_segment": "Müşteri başına en yüksek gelir",
        "best_conversion_segment": "En yüksek kazanma oranı",
        "best_retention_segment": "En düşük churn oranı",
        "developed_by": "Geliştiren",
        "author": "Salsabeel Alfayoumi",
        "critical": "Kritik",
        "warning": "Uyarı",
        "good": "Olumlu",
        "info": "Bilgi",
    },
}


def _safe(value) -> str:
    """Escape values before inserting them into HTML."""

    return escape(str(value))


def _ui(language: str, key: str) -> str:
    """Return localized UI text."""

    return UI_TEXT.get(language, UI_TEXT["en"]).get(
        key,
        UI_TEXT["en"].get(key, key),
    )


def _compact_currency(value: float) -> str:
    """Format large currency values for executive KPI cards."""

    absolute = abs(value)

    if absolute >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"

    if absolute >= 1_000:
        return f"${value / 1_000:.1f}K"

    return f"${value:,.0f}"


def _kpi_card(
    label: str,
    value: str,
    subtitle: str = "",
    color: str = "#2D6A9F",
    progress: float | None = None,
    icon: str = "📌",
    delta_class: str = "",
) -> str:
    """Create one polished KPI card."""

    progress_html = ""

    if progress is not None:
        normalized = max(0.0, min(float(progress), 100.0))
        progress_html = f"""
        <div class="kpi-bar">
          <div
            class="kpi-bar-fill"
            style="width:{normalized:.1f}%;background:{_safe(color)}"
          ></div>
        </div>
        """

    subtitle_class = (
        f"kpi-sub {delta_class}"
        if delta_class
        else "kpi-sub"
    )

    return f"""
    <div class="kpi-card">
      <div class="kpi-card-top">
        <div
          class="kpi-icon"
          style="color:{_safe(color)}"
        >
          {_safe(icon)}
        </div>
        <div class="kpi-label">{_safe(label)}</div>
      </div>

      <div class="kpi-value" style="color:{_safe(color)}">
        {_safe(value)}
      </div>

      <div class="{subtitle_class}">
        {_safe(subtitle)}
      </div>

      {progress_html}
    </div>
    """


def _insight_card(insight, language: str) -> str:
    """Create one localized insight card."""

    color = SEVERITY_COLOR.get(
        insight.severity,
        SEVERITY_COLOR["info"],
    )

    icon = SEVERITY_ICON.get(
        insight.severity,
        SEVERITY_ICON["info"],
    )

    detail_label = translate(
        "insight.detail",
        language,
    )

    action_label = translate(
        "insight.action",
        language,
    )

    return f"""
    <article
      class="insight-card"
      style="border-left-color:{color}"
    >
      <div class="insight-header">
        <div class="insight-title">
          <span>{icon}</span>
          <span>[{_safe(insight.category)}] {_safe(insight.title)}</span>
        </div>

        <span
          class="severity-badge"
          style="background:{color}18;color:{color};border-color:{color}45"
        >
          {_safe(SEVERITY_ICON.get(insight.severity, "🔵"))}
          {_safe(_ui(language, insight.severity))}
        </span>
      </div>

      <div class="insight-detail">
        <b>{_safe(detail_label)}:</b>
        {_safe(insight.detail)}
      </div>

      <div class="insight-action">
        <b>▶ {_safe(action_label)}:</b>
        {_safe(insight.action)}
      </div>
    </article>
    """


def _relative_chart_path(path: str) -> str:
    """Convert a chart path into a path relative to dashboard.html."""

    chart_path = Path(path)

    try:
        relative_path = chart_path.relative_to(
            REPORT_DIR
        )
    except ValueError:
        relative_path = Path(
            chart_path.name
        )

    return relative_path.as_posix()


def _embed_chart(
    chart_paths: dict,
    key: str,
    title: str,
    size: str = "standard",
    subtitle: str = "",
) -> str:
    """Create an image or iframe chart card."""

    path = chart_paths.get(
        key,
        "",
    )

    if not path:
        return ""

    relative_path = _relative_chart_path(
        path
    )

    safe_title = _safe(title)
    safe_path = _safe(relative_path)

    class_name = f"chart-card chart-{size}"

    if path.lower().endswith(".html"):
        content = f"""
        <iframe
          src="{safe_path}"
          width="100%"
          height="520"
          frameborder="0"
          loading="lazy"
          title="{safe_title}"
        ></iframe>
        """

    elif path.lower().endswith(".png"):
        content = f"""
        <div class="image-wrap">
          <img
            src="{safe_path}"
            alt="{safe_title}"
            loading="lazy"
          />
        </div>
        """

    else:
        return ""

    return f"""
    <section class="{class_name}">
      <div class="chart-card-header">
        <h3>{safe_title}</h3>
        <p>{_safe(subtitle)}</p>
      </div>
      {content}
    </section>
    """


def _build_kpi_cards(
    kpis: dict,
    language: str,
) -> str:
    """Create all KPI cards for one language."""

    revenue = kpis["revenue"]
    sales = kpis["sales"]
    meta = kpis["meta"]

    mom_growth = revenue["mom_growth_pct"]
    win_rate = sales["win_rate_pct"]
    churn_rate = sales["churn_rate_pct"]

    if mom_growth > 0:
        mom_color = SEVERITY_COLOR["good"]
    elif mom_growth < 0:
        mom_color = SEVERITY_COLOR["critical"]
    else:
        mom_color = SEVERITY_COLOR["info"]

    if win_rate >= 55:
        win_color = SEVERITY_COLOR["good"]
    elif win_rate >= 40:
        win_color = SEVERITY_COLOR["warning"]
    else:
        win_color = SEVERITY_COLOR["critical"]

    if churn_rate <= 10:
        churn_color = SEVERITY_COLOR["good"]
    elif churn_rate <= 15:
        churn_color = SEVERITY_COLOR["warning"]
    else:
        churn_color = SEVERITY_COLOR["critical"]

    cards = [
        _kpi_card(
            translate(
                "kpi.total_revenue",
                language,
            ),
            _compact_currency(revenue["total_revenue"]),
            (
                f"{translate('kpi.mom', language, value=mom_growth)}"
                f" · {_ui(language, 'exact_value')}: "
                f"${revenue['total_revenue']:,.0f}"
            ),
            mom_color,
            min(abs(mom_growth) * 3, 100),
            "💰",
            "delta-up" if mom_growth >= 0 else "delta-down",
        ),
        _kpi_card(
            translate(
                "kpi.avg_order_value",
                language,
            ),
            _compact_currency(revenue["avg_order_value"]),
            (
                f"{translate('kpi.per_won_order', language)}"
                f" · {_ui(language, 'exact_value')}: "
                f"${revenue['avg_order_value']:,.0f}"
            ),
            SEVERITY_COLOR["info"],
            None,
            "🧾",
        ),
        _kpi_card(
            translate(
                "kpi.win_rate",
                language,
            ),
            f"{win_rate}%",
            translate(
                "kpi.win_target",
                language,
            ),
            win_color,
            win_rate,
            "🎯",
            "delta-up",
        ),
        _kpi_card(
            translate(
                "kpi.churn_status_rate",
                language,
            ),
            f"{churn_rate}%",
            translate(
                "kpi.churn_target",
                language,
            ),
            churn_color,
            churn_rate,
            "🔁",
            "delta-down",
        ),
        _kpi_card(
            translate(
                "kpi.total_customers",
                language,
            ),
            f"{meta['total_customers']:,}",
            "",
            SEVERITY_COLOR["info"],
            None,
            "👥",
        ),
        _kpi_card(
            translate(
                "kpi.total_orders",
                language,
            ),
            f"{meta['total_orders']:,}",
            meta["date_range"],
            SEVERITY_COLOR["info"],
            None,
            "📦",
        ),
    ]

    return "".join(cards)


def _build_insight_cards(
    insights: list,
    language: str,
) -> str:
    """Create all insight cards for one language."""

    if not insights:
        return (
            '<div class="empty-message">'
            f"{_safe(translate('insight.empty', language))}"
            "</div>"
        )

    return "".join(
        _insight_card(
            insight,
            language,
        )
        for insight in insights
    )


def _build_executive_summary(
    kpis: dict,
    insights: list,
    language: str,
) -> str:
    """Create a compact summary block for the overview page."""

    critical_count = sum(
        1
        for insight in insights
        if insight.severity == "critical"
    )

    positive_count = sum(
        1
        for insight in insights
        if insight.severity == "good"
    )

    trend_direction = kpis["trends"]["trend_direction"]

    if language == "tr":
        trend_direction = (
            trend_direction
            .replace("Growing", "Büyüyen")
            .replace("Declining", "Düşen")
            .replace("Stable", "Sabit")
        )
    top_product = kpis["products"]["top_product"]
    top_region = kpis["regions"]["top_region"]

    stats = [
        (
            "🔴",
            _ui(language, "critical_count"),
            critical_count,
            "#E8855A",
        ),
        (
            "🟢",
            _ui(language, "positive_count"),
            positive_count,
            "#48A999",
        ),
        (
            "➡",
            _ui(language, "trend_label"),
            trend_direction,
            "#2D6A9F",
        ),
        (
            "🧩",
            _ui(language, "top_product"),
            top_product,
            "#2D6A9F",
        ),
        (
            "📍",
            _ui(language, "top_region"),
            top_region,
            "#98A4B8",
        ),
    ]

    return "".join(
        f"""
        <div class="summary-item">
          <div
            class="summary-icon"
            style="color:{color}"
          >
            {_safe(icon)}
          </div>
          <div>
            <div class="summary-label">{_safe(label)}</div>
            <div class="summary-value">{_safe(value)}</div>
          </div>
        </div>
        """
        for icon, label, value, color in stats
    )


def _chart_subtitle(language: str, key: str) -> str:
    """Return a localized chart subtitle."""

    subtitle_keys = {
        "monthly_trend": "historical_performance",
        "regional_revenue": "regional_comparison",
        "product_mix": "product_distribution",
        "status_breakdown": "status_distribution",
        "am_performance": "manager_comparison",
        "segment_performance": "segment_comparison",
        "revenue_forecast": "forecast_comparison",
    }

    return _ui(
        language,
        subtitle_keys.get(key, "historical_performance"),
    )


def _forecast_model_panel(
    language: str,
    revenue_forecast: dict | None,
    kpis: dict,
) -> str:
    """Create a dynamic forecast-method summary."""

    model = (
        revenue_forecast.get("model", {})
        if revenue_forecast
        else {}
    )

    slope = model.get(
        "slope",
        kpis["trends"]["trend_slope"],
    )
    r_squared = model.get("r_squared")
    forecast_months = model.get("forecast_months", 3)
    model_name = model.get(
        "name",
        "Linear Regression",
    )
    model_method = model.get(
        "method",
        "NumPy polyfit",
    )
    model_display_name = (
        f"{model_name} ({model_method})"
        if model_method
        else model_name
    )
    direction = model.get(
        "direction",
        kpis["trends"]["trend_direction"],
    )

    if language == "tr":
        direction = (
            str(direction)
            .replace("Growing", "Büyüyen")
            .replace("Declining", "Düşen")
            .replace("Stable", "Sabit")
        )

    r_squared_item = ""

    if r_squared is not None:
        r_squared_item = f"""
        <div class="model-item">
          <span>{_safe(_ui(language, "r_squared"))}</span>
          <strong>{float(r_squared):.4f}</strong>
        </div>
        """

    confidence = (
        _ui(language, "low")
        if r_squared is not None and float(r_squared) < 0.10
        else direction
    )

    return f"""
    <div class="model-panel">
      <div class="model-panel-title">
        {_safe(_ui(language, "forecast_model"))}
      </div>

      <div class="model-grid">
        <div class="model-item">
          <span>{_safe(_ui(language, "model_name"))}</span>
          <strong>{_safe(model_display_name)}</strong>
        </div>

        <div class="model-item">
          <span>{_safe(_ui(language, "forecast_horizon"))}</span>
          <strong>{_safe(forecast_months)} {_safe("ay" if language == "tr" else "months")}</strong>
        </div>

        <div class="model-item">
          <span>{_safe(_ui(language, "slope"))}</span>
          <strong>{float(slope):,.2f}</strong>
        </div>

        {r_squared_item}

        <div class="model-item">
          <span>{_safe(_ui(language, "confidence"))}</span>
          <strong>{_safe(confidence)}</strong>
        </div>

        <div class="model-item model-item-wide">
          <span>{_safe(_ui(language, "model_interpretation"))}</span>
          <strong>{_safe(_ui(language, "directional_only"))}</strong>
        </div>
      </div>
    </div>
    """


def _segment_note_panel(
    language: str,
    segment_analysis: dict | None,
) -> str:
    """Create dynamic segment highlights."""

    if not segment_analysis:
        return f"""
        <div class="note-panel">
          <div class="note-panel-icon">💡</div>
          <div>
            <div class="note-panel-title">
              {_safe(_ui(language, "segment_highlights"))}
            </div>
            <p>{_safe(_ui(language, "segment_note"))}</p>
          </div>
        </div>
        """

    summary = segment_analysis.get("summary", {})

    items = [
        (
            _ui(language, "best_revenue_segment"),
            summary.get("highest_revenue_segment", "N/A"),
        ),
        (
            _ui(language, "best_value_segment"),
            summary.get(
                "highest_revenue_per_customer_segment",
                "N/A",
            ),
        ),
        (
            _ui(language, "best_conversion_segment"),
            summary.get("highest_win_rate_segment", "N/A"),
        ),
        (
            _ui(language, "best_retention_segment"),
            summary.get("lowest_churn_rate_segment", "N/A"),
        ),
    ]

    cards = "".join(
        f"""
        <div class="segment-highlight-item">
          <span>{_safe(label)}</span>
          <strong>{_safe(value)}</strong>
        </div>
        """
        for label, value in items
    )

    return f"""
    <div class="segment-highlight-grid">
      {cards}
    </div>

    <div class="note-panel">
      <div class="note-panel-icon">💡</div>
      <div>
        <div class="note-panel-title">
          {_safe(_ui(language, "segment_highlights"))}
        </div>
        <p>{_safe(_ui(language, "segment_note"))}</p>
      </div>
    </div>
    """


def _build_overview_highlights(
    kpis: dict,
    language: str,
) -> str:
    """Create three executive alerts for immediate attention."""

    mom_growth = kpis["revenue"]["mom_growth_pct"]
    win_rate = kpis["sales"]["win_rate_pct"]
    churn_rate = kpis["sales"]["churn_rate_pct"]

    highlights = [
        {
            "icon": "📉" if mom_growth < 0 else "📈",
            "label": _ui(language, "revenue_status"),
            "value": (
                _ui(language, "declining")
                if mom_growth < 0
                else _ui(language, "healthy")
            ),
            "detail": f"{mom_growth:+.1f}%",
            "priority": (
                _ui(language, "high_priority")
                if mom_growth < 0
                else _ui(language, "on_track")
            ),
            "class": "highlight-critical" if mom_growth < 0 else "highlight-good",
        },
        {
            "icon": "🔁",
            "label": _ui(language, "retention_status"),
            "value": (
                _ui(language, "healthy")
                if churn_rate <= 10
                else _ui(language, "needs_attention")
            ),
            "detail": f"{churn_rate:.2f}%",
            "priority": (
                _ui(language, "on_track")
                if churn_rate <= 10
                else _ui(language, "investigate")
            ),
            "class": "highlight-good" if churn_rate <= 10 else "highlight-critical",
        },
        {
            "icon": "🎯",
            "label": _ui(language, "sales_status"),
            "value": (
                _ui(language, "healthy")
                if win_rate >= 55
                else _ui(language, "needs_attention")
            ),
            "detail": f"{win_rate:.2f}%",
            "priority": (
                _ui(language, "on_track")
                if win_rate >= 55
                else _ui(language, "investigate")
            ),
            "class": "highlight-good" if win_rate >= 55 else "highlight-warning",
        },
    ]

    return "".join(
        f"""
        <div class="business-highlight {item['class']}">
          <div class="business-highlight-icon">{item['icon']}</div>

          <div class="business-highlight-main">
            <div class="business-highlight-label">
              {_safe(item['label'])}
            </div>

            <div class="business-highlight-value">
              {_safe(item['value'])}
            </div>

            <div class="business-highlight-priority">
              {_safe(item['priority'])}
            </div>
          </div>

          <div class="business-highlight-detail">
            {_safe(item['detail'])}
          </div>
        </div>
        """
        for item in highlights
    )


def _build_language_content(
    kpis: dict,
    insights: list,
    chart_paths: dict,
    language: str,
    generated: str,
    segment_analysis: dict | None = None,
    revenue_forecast: dict | None = None,
) -> str:
    """Build the complete application interface for one language."""

    meta = kpis["meta"]

    reporting_months = len(
        kpis["trends"].get(
            "monthly_revenue",
            [],
        )
    )

    kpi_cards = _build_kpi_cards(
        kpis,
        language,
    )

    insight_cards = _build_insight_cards(
        insights,
        language,
    )

    executive_summary = _build_executive_summary(
        kpis,
        insights,
        language,
    )

    business_highlights = _build_overview_highlights(
        kpis,
        language,
    )

    overview_charts = "".join(
        [
            _embed_chart(
                chart_paths,
                "monthly_trend",
                _ui(language, "monthly_revenue"),
                size="wide",
                subtitle=_chart_subtitle(language, "monthly_trend"),
            ),
            _embed_chart(
                chart_paths,
                "regional_revenue",
                _ui(language, "regional_revenue"),
                subtitle=_chart_subtitle(language, "regional_revenue"),
            ),
            _embed_chart(
                chart_paths,
                "product_mix",
                _ui(language, "product_mix"),
                subtitle=_chart_subtitle(language, "product_mix"),
            ),
        ]
    )

    performance_charts = "".join(
        [
            _embed_chart(
                chart_paths,
                "status_breakdown",
                _ui(language, "status_breakdown"),
                subtitle=_chart_subtitle(language, "status_breakdown"),
            ),
            _embed_chart(
                chart_paths,
                "am_performance",
                _ui(language, "am_performance"),
                size="wide",
                subtitle=_chart_subtitle(language, "am_performance"),
            ),
        ]
    )

    segment_chart = _embed_chart(
        chart_paths,
        "segment_performance",
        _ui(language, "segment_performance"),
        size="wide",
        subtitle=_chart_subtitle(language, "segment_performance"),
    )

    forecast_chart = _embed_chart(
        chart_paths,
        "revenue_forecast",
        _ui(language, "revenue_forecast"),
        size="wide",
        subtitle=_chart_subtitle(language, "revenue_forecast"),
    )

    title = translate(
        "dashboard.title",
        language,
    )

    return f"""
    <div
      class="language-content"
      data-language-content="{language}"
    >
      <aside class="sidebar">
        <div class="sidebar-brand">
          <div class="brand-title">
            📊 {_safe(_ui(language, "app_name"))}
          </div>
          <div class="brand-subtitle">
            {_safe(_ui(language, "app_subtitle"))}
          </div>
        </div>

        <nav class="sidebar-nav">
          <div class="nav-section">
            {_safe(_ui(language, "analytics"))}
          </div>

          <button
            class="nav-item active"
            data-page-button="overview"
            onclick="showPage('{language}', 'overview')"
          >
            <span class="nav-icon">🏠</span>
            <span>{_safe(_ui(language, "overview"))}</span>
          </button>

          <button
            class="nav-item"
            data-page-button="performance"
            onclick="showPage('{language}', 'performance')"
          >
            <span class="nav-icon">📈</span>
            <span>{_safe(_ui(language, "performance"))}</span>
          </button>

          <button
            class="nav-item"
            data-page-button="segments"
            onclick="showPage('{language}', 'segments')"
          >
            <span class="nav-icon">👥</span>
            <span>{_safe(_ui(language, "segments"))}</span>
          </button>

          <button
            class="nav-item"
            data-page-button="forecast"
            onclick="showPage('{language}', 'forecast')"
          >
            <span class="nav-icon">🔮</span>
            <span>{_safe(_ui(language, "forecast"))}</span>
          </button>

          <div class="nav-section">
            {_safe(_ui(language, "reports"))}
          </div>

          <button
            class="nav-item"
            data-page-button="insights"
            onclick="showPage('{language}', 'insights')"
          >
            <span class="nav-icon">🧠</span>
            <span>{_safe(_ui(language, "insights"))}</span>
          </button>
        </nav>

        <div class="sidebar-footer">
          Python BI Module v1.0
        </div>
      </aside>

      <div class="app-main">
        <header class="topbar">
          <div>
            <div
              class="topbar-title"
              data-topbar-title
            >
              {_safe(_ui(language, "overview"))}
            </div>
            <div class="topbar-subtitle">
              {_safe(title)}
            </div>
          </div>

          <div class="topbar-right">
            <div class="topbar-metrics">
              <div class="topbar-metric">
                <span>{_safe(_ui(language, "dataset"))}</span>
                <strong>
                  {_safe(reporting_months)}
                  {_safe(_ui(language, "months"))}
                </strong>
              </div>

              <div class="topbar-metric">
                <span>{_safe(translate("kpi.total_customers", language))}</span>
                <strong>{_safe(meta["total_customers"])}</strong>
              </div>

              <div class="topbar-metric">
                <span>{_safe(translate("kpi.total_orders", language))}</span>
                <strong>{_safe(f"{meta['total_orders']:,}")}</strong>
              </div>

              <div class="topbar-metric topbar-generated">
                <span>{_safe(_ui(language, "generated_by"))}</span>
                <strong>{_safe(generated)}</strong>
              </div>
            </div>

            <div class="period-badge">
              <span>{_safe(_ui(language, "period"))}</span>
              <strong>{_safe(meta["date_range"])}</strong>
            </div>

            <div
              class="language-switcher"
              aria-label="Language selection"
            >
              <button
                type="button"
                class="language-button"
                data-language-button="en"
                onclick="setLanguage('en')"
              >
                EN
              </button>

              <button
                type="button"
                class="language-button"
                data-language-button="tr"
                onclick="setLanguage('tr')"
              >
                TR
              </button>
            </div>
          </div>
        </header>

        <main class="page-container">
          <section
            class="page active"
            data-page="overview"
          >
            <div class="page-heading">
              <div>
                <h1>{_safe(_ui(language, "overview"))}</h1>
                <p>
                  {_safe(_ui(language, "generated"))}:
                  {_safe(generated)}
                </p>
              </div>
            </div>

                        <section class="dashboard-section">
              <div class="section-header">
                <div>
                  <h2>{_safe(_ui(language, "kpis"))}</h2>
                </div>
              </div>

              <div class="kpi-grid">
                {kpi_cards}
              </div>
            </section>

            <section class="dashboard-section">
              <div class="section-header">
                <div>
                  <h2>{_safe(_ui(language, "overview_highlights"))}</h2>
                </div>
              </div>

              <div class="business-highlight-grid">
                {business_highlights}
              </div>
            </section>

                        <section class="dashboard-section">
              <div class="section-header">
                <div>
                  <h2>{_safe(_ui(language, "overview_charts"))}</h2>
                </div>
              </div>

              <div class="chart-grid">
                {overview_charts}
              </div>
            </section>

                        <section class="dashboard-section">
              <div class="section-header">
                <div>
                  <h2>{_safe(_ui(language, "executive_summary"))}</h2>
                  <p>{_safe(_ui(language, "executive_summary_sub"))}</p>
                </div>
              </div>

              <div class="summary-strip">
                {executive_summary}
              </div>
            </section>
          </section>

          <section
            class="page"
            data-page="performance"
            hidden
          >
            <div class="page-heading">
              <div>
                <h1>{_safe(_ui(language, "performance"))}</h1>
                <p>{_safe(_ui(language, "performance_charts"))}</p>
              </div>
            </div>

            <div class="chart-grid">
              {performance_charts}
            </div>
          </section>

          <section
            class="page"
            data-page="segments"
            hidden
          >
            <div class="page-heading">
              <div>
                <h1>{_safe(_ui(language, "segment_title"))}</h1>
                <p>{_safe(_ui(language, "segment_sub"))}</p>
              </div>
            </div>

            {_segment_note_panel(language, segment_analysis)}

            <div class="chart-grid">
              {segment_chart}
            </div>
          </section>

          <section
            class="page"
            data-page="forecast"
            hidden
          >
            <div class="page-heading">
              <div>
                <h1>{_safe(_ui(language, "forecast_title"))}</h1>
                <p>{_safe(_ui(language, "forecast_sub"))}</p>
              </div>
            </div>

            <div class="chart-grid">
              {forecast_chart}
            </div>

            <div class="forecast-explanation">
              <div class="forecast-explanation-icon">ℹ️</div>
              <p>{_safe(_ui(language, "forecast_explanation"))}</p>
            </div>

            {_forecast_model_panel(
                language,
                revenue_forecast,
                kpis,
            )}
          </section>

          <section
            class="page"
            data-page="insights"
            hidden
          >
            <div class="page-heading">
              <div>
                <h1>{_safe(_ui(language, "all_insights"))}</h1>
                <p>{_safe(_ui(language, "all_insights_sub"))}</p>
              </div>
            </div>

            <div class="insights-list">
              {insight_cards}
            </div>
          </section>
        </main>

        <footer>
          <div class="footer-main">
            Python BI Reporting &amp; Decision Support Dashboard
          </div>

          <div class="footer-author">
            {_safe(_ui(language, "developed_by"))}
            <strong>{_safe(_ui(language, "author"))}</strong>
          </div>

          <div class="footer-project">
            KTÜ Computer Engineering Internship · KivaCRM
          </div>

          <div class="footer-tech-label">
            Powered by
          </div>

          <div class="footer-tech">
            Python • Pandas • NumPy • Plotly • Matplotlib • OpenPyXL
          </div>

          <div class="footer-date">{_safe(generated)}</div>
        </footer>
      </div>
    </div>
    """


def generate_html_report(
    kpis: dict,
    insights_by_language: dict,
    chart_paths_by_language: dict,
    segment_analysis: dict | None = None,
    revenue_forecast: dict | None = None,
) -> str:
    """Generate one polished bilingual dashboard."""

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    generated = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    english_content = _build_language_content(
        kpis=kpis,
        insights=insights_by_language.get(
            "en",
            [],
        ),
        chart_paths=chart_paths_by_language.get(
            "en",
            {},
        ),
        language="en",
        generated=generated,
        segment_analysis=segment_analysis,
        revenue_forecast=revenue_forecast,
    )

    turkish_content = _build_language_content(
        kpis=kpis,
        insights=insights_by_language.get(
            "tr",
            [],
        ),
        chart_paths=chart_paths_by_language.get(
            "tr",
            {},
        ),
        language="tr",
        generated=generated,
        segment_analysis=segment_analysis,
        revenue_forecast=revenue_forecast,
    )

    browser_title = translate(
        "dashboard.title",
        "en",
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta
  name="viewport"
  content="width=device-width, initial-scale=1.0"
/>
<title>{_safe(browser_title)}</title>

<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  :root {{
    --blue: #2D6A9F;
    --blue-dark: #173F63;
    --blue-light: #EBF3FA;
    --green: #48A999;
    --orange: #E8855A;
    --yellow: #AAB4C3;
    --purple: #60758A;
    --background: #F4F7FB;
    --surface: #FFFFFF;
    --border: #E2E8F0;
    --text: #1A2233;
    --muted: #6B7A99;
    --faint: #98A4B8;
    --radius: 12px;
    --shadow: 0 5px 18px rgba(23, 63, 99, 0.08);
    --sidebar-width: 230px;
  }}

  body {{
    font-family:
      "Segoe UI",
      system-ui,
      -apple-system,
      BlinkMacSystemFont,
      sans-serif;
    background: var(--background);
    color: var(--text);
    min-height: 100vh;
  }}

  button {{
    font: inherit;
  }}

  .language-content {{
    min-height: 100vh;
    display: flex;
  }}

  .language-content[hidden] {{
    display: none;
  }}

  .sidebar {{
    width: var(--sidebar-width);
    min-height: 100vh;
    background:
      linear-gradient(
        180deg,
        var(--blue-dark) 0%,
        #102F4B 100%
      );
    color: white;
    display: flex;
    flex-direction: column;
    position: fixed;
    inset: 0 auto 0 0;
    z-index: 100;
  }}

  .sidebar-brand {{
    padding: 25px 21px 21px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }}

  .brand-title {{
    font-size: 1.03rem;
    font-weight: 750;
  }}

  .brand-subtitle {{
    font-size: 0.72rem;
    color: rgba(255, 255, 255, 0.52);
    margin-top: 4px;
  }}

  .sidebar-nav {{
    padding: 14px 0;
    flex: 1;
  }}

  .nav-section {{
    padding: 12px 18px 6px;
    color: rgba(255, 255, 255, 0.34);
    font-size: 0.64rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.11em;
  }}

  .nav-item {{
    width: 100%;
    border: 0;
    border-left: 3px solid transparent;
    background: transparent;
    color: rgba(255, 255, 255, 0.72);
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 11px 18px;
    cursor: pointer;
    text-align: left;
    transition:
      background 0.15s ease,
      color 0.15s ease,
      border-color 0.15s ease;
  }}

  .nav-item:hover {{
    color: white;
    background: rgba(255, 255, 255, 0.07);
  }}

  .nav-item.active {{
    color: white;
    background: rgba(255, 255, 255, 0.12);
    border-left-color: var(--green);
  }}

  .nav-icon {{
    width: 22px;
    text-align: center;
  }}

  .sidebar-footer {{
    padding: 17px 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.36);
    font-size: 0.7rem;
  }}

  .app-main {{
    margin-left: var(--sidebar-width);
    min-height: 100vh;
    width: calc(100% - var(--sidebar-width));
    display: flex;
    flex-direction: column;
  }}

  .topbar {{
    min-height: 68px;
    padding: 10px 28px;
    background: rgba(255, 255, 255, 0.96);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    position: sticky;
    top: 0;
    z-index: 50;
    backdrop-filter: blur(12px);
  }}

  .topbar-title {{
    font-size: 1rem;
    font-weight: 750;
  }}

  .topbar-subtitle {{
    font-size: 0.76rem;
    color: var(--muted);
    margin-top: 2px;
  }}

  .topbar-right {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .period-badge {{
    background: var(--blue-light);
    color: var(--blue);
    border-radius: 20px;
    padding: 6px 12px;
    font-size: 0.72rem;
    display: flex;
    gap: 6px;
    align-items: center;
    white-space: nowrap;
  }}

  .language-switcher {{
    display: flex;
    gap: 4px;
    padding: 4px;
    border: 1px solid var(--border);
    background: var(--surface);
    border-radius: 9px;
  }}

  .language-button {{
    border: none;
    background: transparent;
    color: var(--blue);
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 0.76rem;
    font-weight: 700;
    cursor: pointer;
  }}

  .language-button:hover {{
    background: var(--blue-light);
  }}

  .language-button.active {{
    color: white;
    background: var(--blue);
  }}

  .page-container {{
    width: 100%;
    max-width: 1460px;
    margin: 0 auto;
    padding: 28px;
    flex: 1;
  }}

  .page {{
    display: block;
  }}

  .page[hidden] {{
    display: none;
  }}

  .page-heading {{
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 24px;
  }}

  .page-heading h1 {{
    font-size: 1.52rem;
    font-weight: 760;
  }}

  .page-heading p {{
    color: var(--muted);
    font-size: 0.84rem;
    margin-top: 5px;
    line-height: 1.5;
  }}

  .dashboard-section {{
    margin-bottom: 27px;
  }}

  .section-header {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 12px;
  }}

  .section-header h2 {{
    color: var(--blue);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 780;
  }}

  .section-header p {{
    color: var(--muted);
    font-size: 0.78rem;
    margin-top: 4px;
  }}

  .kpi-grid {{
    display: grid;
    grid-template-columns:
      repeat(auto-fit, minmax(175px, 1fr));
    gap: 16px;
  }}

  .kpi-card {{
    position: relative;
    overflow: hidden;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px;
    box-shadow: var(--shadow);
    min-height: 138px;
    transition:
      transform 0.18s ease,
      box-shadow 0.18s ease,
      border-color 0.18s ease;
  }}

  .kpi-label {{
    font-size: 0.67rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--muted);
  }}

  .kpi-value {{
    font-size: 2.15rem;
    line-height: 1.05;
    font-weight: 760;
    margin: 10px 0 5px;
  }}

  .kpi-sub {{
    color: var(--faint);
    font-size: 0.69rem;
    line-height: 1.4;
    min-height: 18px;
  }}

  .kpi-bar {{
    height: 4px;
    border-radius: 99px;
    background: #EDF1F6;
    margin-top: 12px;
    overflow: hidden;
  }}

  .kpi-bar-fill {{
    height: 100%;
    border-radius: inherit;
  }}

  .summary-strip {{
    display: grid;
    grid-template-columns:
      repeat(auto-fit, minmax(150px, 1fr));
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow);
  }}

  .summary-item {{
    min-height: 78px;
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 15px 16px;
    background: var(--surface);
  }}

  .summary-icon {{
    width: 30px;
    height: 30px;
    display: grid;
    place-items: center;
    flex-shrink: 0;
    border-radius: 9px;
    background: var(--background);
    font-size: 0.95rem;
  }}

  .summary-label {{
    color: var(--muted);
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }}

  .summary-value {{
    font-size: 0.94rem;
    font-weight: 720;
    margin-top: 3px;
  }}

  .chart-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }}

  .chart-card {{
    min-width: 0;
    background: var(--surface);
    border: 1px solid #DCE4ED;
    border-radius: var(--radius);
    box-shadow: 0 8px 22px rgba(23, 63, 99, 0.07);
    overflow: hidden;
    transition:
      transform 0.18s ease,
      box-shadow 0.18s ease;
  }}

  .chart-wide {{
    grid-column: 1 / -1;
  }}

  .chart-card h3 {{
    font-size: 0.9rem;
    font-weight: 730;
  }}

  .chart-card iframe {{
    width: 100%;
    display: block;
    border: none;
    background: white;
  }}

  .image-wrap {{
    padding: 8px 16px 17px;
  }}

  .chart-card img {{
    width: 100%;
    display: block;
    border-radius: 8px;
  }}

  .insights-list {{
    display: flex;
    flex-direction: column;
    gap: 11px;
  }}

  .insight-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-left-width: 4px;
    border-radius: var(--radius);
    padding: 16px 18px;
    box-shadow: var(--shadow);
  }}

  .insight-title {{
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.88rem;
    font-weight: 730;
    margin-bottom: 7px;
  }}

  .insight-detail {{
    color: var(--muted);
    font-size: 0.81rem;
    line-height: 1.55;
    margin-bottom: 4px;
  }}

  .insight-action {{
    color: var(--blue);
    font-size: 0.81rem;
    line-height: 1.55;
  }}

  .empty-message {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    color: var(--muted);
  }}

  footer {{
    color: var(--faint);
    font-size: 0.74rem;
    text-align: center;
    padding: 20px 28px 24px;
    border-top: 1px solid var(--border);
    background: rgba(255, 255, 255, 0.55);
  }}


  .kpi-card:hover {{
    transform: translateY(-3px);
    border-color: #CFD9E6;
    box-shadow: 0 10px 25px rgba(23, 63, 99, 0.12);
  }}

  .kpi-card-top {{
    display: flex;
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
  }}

  .kpi-icon {{
    width: 42px;
    height: 42px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    background: #F3F7FB;
    font-size: 1.18rem;
    flex-shrink: 0;
    box-shadow: inset 0 0 0 1px #E6EDF5;
  }}

  .delta-up {{
    color: var(--green);
  }}

  .delta-down {{
    color: var(--orange);
  }}


  .chart-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(23, 63, 99, 0.11);
  }}

  .chart-card-header p {{
    color: var(--muted);
    font-size: 0.73rem;
    line-height: 1.4;
    margin-top: 4px;
  }}

  .insight-header {{
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 14px;
    margin-bottom: 7px;
  }}

  .severity-badge {{
    flex-shrink: 0;
    border: 1px solid;
    border-radius: 999px;
    padding: 3px 8px;
    font-size: 0.61rem;
    letter-spacing: 0.06em;
    font-weight: 800;
  }}

  .model-panel,
  .note-panel {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 20px;
  }}

  .model-panel {{
    padding: 18px;
  }}

  .forecast-explanation {{
    margin: 16px 0 20px;
    padding: 15px 17px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    background: var(--blue-light);
    border: 1px solid #D7E6F3;
    border-radius: var(--radius);
    color: var(--blue-dark);
  }}

  .forecast-explanation-icon {{
    width: 32px;
    height: 32px;
    display: grid;
    place-items: center;
    flex-shrink: 0;
    border-radius: 9px;
    background: white;
  }}

  .forecast-explanation p {{
    font-size: 0.8rem;
    line-height: 1.6;
  }}


  .model-panel-title,
  .note-panel-title {{
    color: var(--blue);
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.07em;
  }}

  .model-grid {{
    margin-top: 13px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }}

  .model-item {{
    background: var(--background);
    border-radius: 9px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}

  .model-item-wide {{
    grid-column: 1 / -1;
  }}

  .model-item span {{
    color: var(--muted);
    font-size: 0.68rem;
  }}

  .model-item strong {{
    font-size: 0.84rem;
    line-height: 1.4;
  }}

  .note-panel {{
    padding: 16px 18px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
  }}

  .note-panel-icon {{
    width: 34px;
    height: 34px;
    display: grid;
    place-items: center;
    flex-shrink: 0;
    background: #FFF8E2;
    border-radius: 9px;
  }}

  .note-panel p {{
    color: var(--muted);
    font-size: 0.8rem;
    line-height: 1.55;
    margin-top: 5px;
  }}

  .footer-main {{
    color: var(--muted);
    font-weight: 650;
  }}

  .footer-tech-label {{
    margin-top: 7px;
    color: var(--faint);
    font-size: 0.64rem;
    font-weight: 650;
  }}

  .footer-tech {{
    margin-top: 3px;
    color: var(--faint);
    font-size: 0.66rem;
  }}

  .footer-date {{
    margin-top: 3px;
    color: var(--faint);
  }}


  .business-highlight-grid {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
  }}

  .business-highlight {{
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 12px;
    min-height: 92px;
    padding: 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-left-width: 4px;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
  }}

  .highlight-critical {{
    border-left-color: var(--orange);
  }}

  .highlight-good {{
    border-left-color: var(--green);
  }}

  .highlight-warning {{
    border-left-color: var(--yellow);
  }}

  .business-highlight-icon {{
    width: 38px;
    height: 38px;
    display: grid;
    place-items: center;
    border-radius: 10px;
    background: var(--background);
    font-size: 1.08rem;
  }}

  .business-highlight-label {{
    color: var(--muted);
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }}

  .business-highlight-value {{
    margin-top: 4px;
    font-size: 1.10rem;
    line-height: 1.2;
    font-weight: 790;
  }}

  .business-highlight-detail {{
    font-size: 1.45rem;
    line-height: 1;
    font-weight: 820;
    color: var(--blue-dark);
  }}

  .segment-highlight-grid {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 14px;
  }}

  .segment-highlight-item {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    box-shadow: var(--shadow);
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}

  .segment-highlight-item span {{
    color: var(--muted);
    font-size: 0.68rem;
  }}

  .segment-highlight-item strong {{
    color: var(--blue-dark);
    font-size: 0.92rem;
  }}

  .footer-author {{
    margin-top: 5px;
    color: var(--muted);
  }}


  .topbar-metrics {{
    display: flex;
    align-items: stretch;
    gap: 8px;
  }}

  .topbar-metric {{
    min-width: 82px;
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: #FAFCFE;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}

  .topbar-metric span {{
    color: var(--muted);
    font-size: 0.61rem;
  }}

  .topbar-metric strong {{
    font-size: 0.72rem;
    white-space: nowrap;
  }}

  .topbar-generated {{
    min-width: 130px;
  }}

  .chart-grid {{
    padding: 2px;
    border-radius: 14px;
  }}

  .chart-card-header {{
    padding: 18px 20px 7px;
    border-bottom: 1px solid #EEF2F6;
  }}

  .business-highlight-priority {{
    margin-top: 6px;
    color: var(--muted);
    font-size: 0.66rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}

  .footer-project {{
    margin-top: 4px;
    color: var(--muted);
  }}

  @media (max-width: 1180px) {{
    .topbar-generated {{
      display: none;
    }}
  }}

  @media (max-width: 980px) {{
    :root {{
      --sidebar-width: 78px;
    }}

    .brand-title {{
      font-size: 0;
    }}

    .brand-title::before {{
      content: "📊";
      font-size: 1.35rem;
    }}

    .brand-subtitle,
    .nav-item span:last-child,
    .nav-section,
    .sidebar-footer {{
      display: none;
    }}

    .nav-item {{
      justify-content: center;
      padding: 13px 0;
    }}

    .nav-icon {{
      width: auto;
    }}

    .sidebar-brand {{
      padding: 24px 0;
      text-align: center;
    }}
  }}

  @media (max-width: 760px) {{
    :root {{
      --sidebar-width: 0px;
    }}

    .sidebar {{
      display: none;
    }}

    .app-main {{
      margin-left: 0;
      width: 100%;
    }}

    .topbar {{
      padding: 10px 16px;
      align-items: flex-start;
      flex-direction: column;
    }}

    .topbar-right {{
      width: 100%;
      justify-content: space-between;
      flex-wrap: wrap;
    }}

    .topbar-metrics {{
      width: 100%;
      overflow-x: auto;
      padding-bottom: 2px;
    }}

    .topbar-metric {{
      flex: 0 0 auto;
    }}

    .period-badge {{
      max-width: calc(100% - 82px);
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .page-container {{
      padding: 20px 15px;
    }}

    .chart-grid {{
      grid-template-columns: 1fr;
    }}

    .chart-wide {{
      grid-column: auto;
    }}

    .business-highlight-grid,
    .segment-highlight-grid {{
      grid-template-columns: 1fr;
    }}

    .business-highlight {{
      grid-template-columns: auto 1fr;
    }}

    .business-highlight-detail {{
      grid-column: 2;
      margin-top: 4px;
    }}

    .chart-card iframe {{
      height: 470px;
    }}
  }}
</style>
</head>

<body>

{english_content}

{turkish_content}

<script>
  const PAGE_TITLES = {{
    en: {{
      overview: "Overview",
      performance: "Performance Analytics",
      segments: "Segment Analysis",
      forecast: "Revenue Forecast",
      insights: "Decision Insights"
    }},
    tr: {{
      overview: "Genel Bakış",
      performance: "Performans Analizleri",
      segments: "Segment Analizi",
      forecast: "Gelir Tahmini",
      insights: "Karar Destek İçgörüleri"
    }}
  }};

  function showPage(language, pageName) {{
    const languageRoot = document.querySelector(
      `[data-language-content="${{language}}"]`
    );

    if (!languageRoot) {{
      return;
    }}

    languageRoot
      .querySelectorAll("[data-page]")
      .forEach((page) => {{
        const isActive =
          page.dataset.page === pageName;

        page.hidden = !isActive;
        page.classList.toggle("active", isActive);
      }});

    languageRoot
      .querySelectorAll("[data-page-button]")
      .forEach((button) => {{
        button.classList.toggle(
          "active",
          button.dataset.pageButton === pageName
        );
      }});

    const title = languageRoot.querySelector(
      "[data-topbar-title]"
    );

    if (title) {{
      title.textContent =
        PAGE_TITLES[language][pageName]
        || PAGE_TITLES[language].overview;
    }}

    localStorage.setItem(
      "dashboardPage",
      pageName
    );

    window.scrollTo({{
      top: 0,
      behavior: "smooth"
    }});
  }}

  function setLanguage(language) {{
    const supportedLanguages = ["en", "tr"];

    if (!supportedLanguages.includes(language)) {{
      language = "en";
    }}

    document.documentElement.lang = language;

    document
      .querySelectorAll("[data-language-content]")
      .forEach((content) => {{
        content.hidden =
          content.dataset.languageContent !== language;
      }});

    document
      .querySelectorAll("[data-language-button]")
      .forEach((button) => {{
        const isActive =
          button.dataset.languageButton === language;

        button.classList.toggle(
          "active",
          isActive
        );

        button.setAttribute(
          "aria-pressed",
          isActive.toString()
        );
      }});

    localStorage.setItem(
      "dashboardLanguage",
      language
    );

    const savedPage =
      localStorage.getItem("dashboardPage")
      || "overview";

    showPage(language, savedPage);
  }}

  const savedLanguage =
    localStorage.getItem("dashboardLanguage");

  const browserLanguage =
    navigator.language
      .toLowerCase()
      .startsWith("tr")
        ? "tr"
        : "en";

  setLanguage(
    savedLanguage || browserLanguage
  );
</script>

</body>
</html>
"""

    output_path = REPORT_DIR / "dashboard.html"

    output_path.write_text(
        html,
        encoding="utf-8",
    )

    print(f"  ✓ {output_path}")

    return str(output_path)
