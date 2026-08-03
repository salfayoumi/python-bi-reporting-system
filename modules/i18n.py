"""
modules/i18n.py

Central translation system for English and Turkish support.
"""

SUPPORTED_LANGUAGES = ("en", "tr")
DEFAULT_LANGUAGE = "en"


TRANSLATIONS = {
    "en": {
        # Dashboard
        "dashboard.title": "BI Reporting & Decision Support Dashboard",
        "dashboard.report_generated": "Report generated",
        "dashboard.data_calculated": "Data calculated",
        "dashboard.period": "Period",

        # Sections
        "section.kpis": "Key Performance Indicators",
        "section.insights": "Decision Support Insights",
        "section.charts": "Visual Analytics",

        # KPI labels
        "kpi.total_revenue": "Total Revenue",
        "kpi.avg_order_value": "Avg Order Value",
        "kpi.win_rate": "Win Rate",
        "kpi.churn_status_rate": "Churn-Status Rate",
        "kpi.total_customers": "Total Customers",
        "kpi.total_orders": "Total Orders",

        # KPI subtitles
        "kpi.mom": "MoM: {value:+.1f}%",
        "kpi.per_won_order": "per won order",
        "kpi.win_target": "configured target: 55%",
        "kpi.churn_target": "order records · target: ≤10%",

        # Insight card
        "insight.detail": "Detail",
        "insight.action": "Action",
        "insight.empty": "No decision-support insights were generated.",

        # Charts
        "chart.monthly_trend": "Monthly Revenue Trend",
        "chart.product_mix": "Revenue by Product",
        "chart.regional_revenue": "Revenue by Region",
        "chart.status_breakdown": "Order Status Breakdown",
        "chart.am_performance": "Account Manager Performance",
        "chart.empty": "No chart files are available.",

        # Chart axes
        "chart.month": "Month",
        "chart.revenue_usd": "Revenue (USD)",
        "chart.region": "Region",
        "chart.product": "Product",
        "chart.status": "Status",
        "chart.count": "Count",
        "chart.orders": "Orders",
        "chart.account_manager": "Account Manager",

        # Main console
        "main.title": "Python BI Reporting & Decision Support Module",
        "main.computing_kpis": "Computing KPIs...",
        "main.generating_charts": "Generating charts...",
        "main.running_decision_support": "Running decision support engine...",
        "main.generating_report": "Generating HTML report...",
        "main.done": "Done!",
        "main.open": "Open",

        # Footer
        "footer.text": "Python BI Module — Internship Project · KivaCRM",

        # Decision-support report
        "report.decision_support": "DECISION SUPPORT REPORT",
        "report.detail": "Detail",
        "report.action": "Action",

        # Categories
        "category.revenue": "Revenue",
        "category.sales": "Sales",
        "category.retention": "Retention",
        "category.product": "Product",
        "category.region": "Region",
        "category.trend": "Trend",

        # Revenue insights
        "revenue.sharp_decline.title": "Revenue declining sharply",
        "revenue.sharp_decline.detail":
            "Month-over-month revenue changed by {value}%.",
        "revenue.sharp_decline.action":
            "Investigate lost deals, pricing changes, seasonality, "
            "and competitive pressure.",

        "revenue.decline.title": "Revenue declined month-over-month",
        "revenue.decline.detail":
            "Month-over-month revenue changed by {value}%.",
        "revenue.decline.action":
            "Review the current month by product and region, and monitor "
            "whether the decline continues.",

        "revenue.stable.title": "Revenue remained stable",
        "revenue.stable.detail":
            "No month-over-month revenue change was detected.",
        "revenue.stable.action":
            "Monitor the next reporting period and identify opportunities "
            "for controlled growth.",

        "revenue.growth.title": "Revenue growing",
        "revenue.growth.detail":
            "Month-over-month revenue increased by {value}%.",
        "revenue.growth.action":
            "Identify which products, regions, or account managers "
            "contributed most to the growth.",

        # Sales insights
        "sales.low.title": "Low win rate",
        "sales.low.detail":
            "Win rate is {value}%. The configured healthy threshold is 55%.",
        "sales.low.action":
            "Analyze lost opportunities by product, region, "
            "and account manager.",

        "sales.below_target.title": "Win rate below target",
        "sales.below_target.detail":
            "Win rate is {value}%. The configured target is 55%.",
        "sales.below_target.action":
            "Review lead qualification, sales coaching, and common reasons "
            "for lost opportunities.",

        "sales.healthy.title": "Win rate healthy",
        "sales.healthy.detail": "Win rate is {value}%.",
        "sales.healthy.action":
            "Document successful deal patterns and apply them across "
            "the sales team.",

        # Retention insights
        "retention.high.title": "High churn-status rate",
        "retention.high.detail":
            "{value}% of order records have the 'Churned' status.",
        "retention.high.action":
            "Identify the affected customers, products, regions, and "
            "segments, then investigate the main reasons.",

        "retention.elevated.title": "Churn-status rate elevated",
        "retention.elevated.detail":
            "{value}% of order records have the 'Churned' status.",
        "retention.elevated.action":
            "Review churn patterns and prepare targeted retention actions.",

        "retention.target.title": "Churn-status rate within target",
        "retention.target.detail":
            "{value}% of order records have the 'Churned' status.",
        "retention.target.action":
            "Continue monitoring retention patterns and customer feedback.",

        # Product insights
        "product.concentrated.title":
            "Revenue concentrated in one product",
        "product.concentrated.detail":
            "'{product}' contributes {share}% of total revenue.",
        "product.concentrated.action":
            "Increase cross-selling and upselling of other products "
            "to reduce concentration risk.",

        "product.diversified.title":
            "Product revenue reasonably diversified",
        "product.diversified.detail":
            "The largest product share is {share}% from '{product}'.",
        "product.diversified.action":
            "Maintain product diversification while monitoring changes "
            "in revenue concentration.",

        "product.unavailable.title": "No product revenue available",
        "product.unavailable.detail":
            "No product-mix information could be calculated from won orders.",
        "product.unavailable.action":
            "Confirm that won-order data is available before performing "
            "product analysis.",

        # Regional insights
        "region.leaders.title":
            "Regional performance leaders identified",
        "region.top_revenue":
            "{region} generated the highest revenue at {value:,.2f}.",
        "region.top_average":
            "{region} had the highest average order value at {value:,.2f}.",
        "region.leaders.action":
            "Compare the sales practices of the leading regions and evaluate "
            "whether they can be replicated elsewhere.",

        # Trend insights
        "trend.growing.title": "Overall revenue trend is growing",
        "trend.growing.detail":
            "Linear trend slope is {value:,.2f} per month.",
        "trend.growing.action":
            "Use the current trend as a reference when setting future "
            "sales targets.",

        "trend.declining.title": "Overall revenue trend is declining",
        "trend.declining.detail":
            "Linear trend slope is {value:,.2f} per month.",
        "trend.declining.action":
            "Analyze the quarters, products, and regions that contributed "
            "most to the decline.",

        "trend.stable.title": "Overall revenue trend is stable",
        "trend.stable.detail":
            "Linear trend slope is {value:,.2f} per month and remains "
            "within the stability tolerance.",
        "trend.stable.action":
            "Monitor upcoming periods and focus on converting stable "
            "performance into sustainable growth.",

        # Visualizer
        "visualizer.generating": "Generating charts...",

        "chart.monthly_trend": "Monthly Revenue Trend",
        "chart.product_mix": "Revenue by Product",
        "chart.regional_revenue": "Revenue by Region",
        "chart.status_breakdown": "Order Status Breakdown",
        "chart.am_performance": "Account Manager Performance",

        "chart.month": "Month",
        "chart.revenue_usd": "Revenue (USD)",
        "chart.product": "Product",
        "chart.region": "Region",
        "chart.status": "Status",
        "chart.count": "Count",
        "chart.revenue": "Revenue",
        "chart.orders": "Orders",
        "chart.account_manager": "Account Manager",

        "chart.segment_performance": "Customer Segment Performance",
        "chart.segment": "Customer Segment",
        "chart.win_rate": "Win Rate",

        "chart.revenue_forecast": "Three-Month Revenue Forecast",
        "chart.actual_revenue": "Actual Revenue",
        "chart.linear_trend": "Linear Trend",
        "chart.forecast": "Forecast",
        "chart.forecast_start": "Forecast Start",
        "chart.directional_estimate": "Directional estimate",
    },

    "tr": {
        # Dashboard
        "dashboard.title": "İş Zekâsı Raporlama ve Karar Destek Paneli",
        "dashboard.report_generated": "Rapor oluşturulma zamanı",
        "dashboard.data_calculated": "Veri hesaplama zamanı",
        "dashboard.period": "Dönem",

        # Sections
        "section.kpis": "Temel Performans Göstergeleri",
        "section.insights": "Karar Destek İçgörüleri",
        "section.charts": "Görsel Analizler",

        # KPI labels
        "kpi.total_revenue": "Toplam Gelir",
        "kpi.avg_order_value": "Ortalama Sipariş Değeri",
        "kpi.win_rate": "Kazanma Oranı",
        "kpi.churn_status_rate": "Churn Durum Oranı",
        "kpi.total_customers": "Toplam Müşteri",
        "kpi.total_orders": "Toplam Sipariş",

        # KPI subtitles
        "kpi.mom": "Aylık değişim: {value:+.1f}%",
        "kpi.per_won_order": "kazanılan sipariş başına",
        "kpi.win_target": "tanımlı hedef: %55",
        "kpi.churn_target": "sipariş kayıtları · hedef: ≤%10",

        # Insight card
        "insight.detail": "Detay",
        "insight.action": "Aksiyon",
        "insight.empty": "Herhangi bir karar destek içgörüsü oluşturulmadı.",

        # Charts
        "chart.monthly_trend": "Aylık Gelir Trendi",
        "chart.product_mix": "Ürün Bazında Gelir",
        "chart.regional_revenue": "Bölge Bazında Gelir",
        "chart.status_breakdown": "Sipariş Durumu Dağılımı",
        "chart.am_performance": "Müşteri Temsilcisi Performansı",
        "chart.empty": "Kullanılabilir grafik dosyası bulunmamaktadır.",

        # Chart axes
        "chart.month": "Ay",
        "chart.revenue_usd": "Gelir (USD)",
        "chart.region": "Bölge",
        "chart.product": "Ürün",
        "chart.status": "Durum",
        "chart.count": "Adet",
        "chart.orders": "Siparişler",
        "chart.account_manager": "Müşteri Temsilcisi",

        # Main console
        "main.title": "Python İş Zekâsı Raporlama ve Karar Destek Modülü",
        "main.computing_kpis": "KPI değerleri hesaplanıyor...",
        "main.generating_charts": "Grafikler oluşturuluyor...",
        "main.running_decision_support": "Karar destek motoru çalıştırılıyor...",
        "main.generating_report": "HTML raporu oluşturuluyor...",
        "main.done": "Tamamlandı!",
        "main.open": "Aç",

        # Footer
        "footer.text": "Python İş Zekâsı Modülü — Staj Projesi · KivaCRM",

        # Karar destek raporu
        "report.decision_support": "KARAR DESTEK RAPORU",
        "report.detail": "Detay",
        "report.action": "Aksiyon",

        # Kategoriler
        "category.revenue": "Gelir",
        "category.sales": "Satış",
        "category.retention": "Müşteri Tutundurma",
        "category.product": "Ürün",
        "category.region": "Bölge",
        "category.trend": "Trend",

        # Gelir içgörüleri
        "revenue.sharp_decline.title": "Gelir keskin şekilde düşüyor",
        "revenue.sharp_decline.detail":
            "Aylık gelir değişimi {value:+}% olarak gerçekleşti.",
        "revenue.sharp_decline.action":
            "Kaybedilen satışları, fiyat değişikliklerini, mevsimselliği "
            "ve rekabet baskısını inceleyin.",

        "revenue.decline.title": "Gelir önceki aya göre düştü",
        "revenue.decline.detail":
            "Aylık gelir değişimi {value:+}% olarak gerçekleşti.",
        "revenue.decline.action":
            "Mevcut ayı ürün ve bölge bazında inceleyin ve düşüşün devam "
            "edip etmediğini takip edin.",

        "revenue.stable.title": "Gelir sabit kaldı",
        "revenue.stable.detail":
            "Önceki aya göre herhangi bir gelir değişimi tespit edilmedi.",
        "revenue.stable.action":
            "Bir sonraki raporlama dönemini takip edin ve kontrollü büyüme "
            "fırsatlarını belirleyin.",

        "revenue.growth.title": "Gelir artıyor",
        "revenue.growth.detail":
            "Gelir önceki aya göre %{value} arttı.",
        "revenue.growth.action":
            "Büyümeye en fazla katkı sağlayan ürünleri, bölgeleri veya "
            "müşteri temsilcilerini belirleyin.",

        # Satış içgörüleri
        "sales.low.title": "Kazanma oranı düşük",
        "sales.low.detail":
            "Kazanma oranı %{value}. Tanımlanan sağlıklı eşik %55'tir.",
        "sales.low.action":
            "Kaybedilen fırsatları ürün, bölge ve müşteri temsilcisi "
            "bazında analiz edin.",

        "sales.below_target.title": "Kazanma oranı hedefin altında",
        "sales.below_target.detail":
            "Kazanma oranı %{value}. Tanımlanan hedef %55'tir.",
        "sales.below_target.action":
            "Potansiyel müşteri değerlendirmesini, satış eğitimlerini ve "
            "kaybedilen fırsatların ortak nedenlerini inceleyin.",

        "sales.healthy.title": "Kazanma oranı sağlıklı",
        "sales.healthy.detail": "Kazanma oranı %{value}.",
        "sales.healthy.action":
            "Başarılı satış örüntülerini belgeleyin ve satış ekibi "
            "genelinde uygulayın.",

        # Müşteri tutundurma içgörüleri
        "retention.high.title": "Churn durum oranı yüksek",
        "retention.high.detail":
            "Sipariş kayıtlarının %{value} kadarı 'Churned' durumundadır.",
        "retention.high.action":
            "Etkilenen müşterileri, ürünleri, bölgeleri ve segmentleri "
            "belirleyerek temel nedenleri inceleyin.",

        "retention.elevated.title": "Churn durum oranı yükselmiş",
        "retention.elevated.detail":
            "Sipariş kayıtlarının %{value} kadarı 'Churned' durumundadır.",
        "retention.elevated.action":
            "Churn örüntülerini inceleyin ve hedefli müşteri tutundurma "
            "aksiyonları hazırlayın.",

        "retention.target.title": "Churn durum oranı hedef aralığında",
        "retention.target.detail":
            "Sipariş kayıtlarının %{value} kadarı 'Churned' durumundadır.",
        "retention.target.action":
            "Müşteri tutundurma örüntülerini ve müşteri geri bildirimlerini "
            "takip etmeye devam edin.",

        # Ürün içgörüleri
        "product.concentrated.title":
            "Gelir tek bir üründe yoğunlaşmış",
        "product.concentrated.detail":
            "'{product}' toplam gelirin %{share} kadarını oluşturmaktadır.",
        "product.concentrated.action":
            "Yoğunlaşma riskini azaltmak için diğer ürünlerde çapraz satış "
            "ve üst satış çalışmalarını artırın.",

        "product.diversified.title":
            "Ürün gelir dağılımı yeterince çeşitlendirilmiş",
        "product.diversified.detail":
            "En büyük ürün payı, '{product}' ürünüyle %{share} seviyesindedir.",
        "product.diversified.action":
            "Gelir yoğunluğundaki değişimleri takip ederken ürün "
            "çeşitliliğini koruyun.",

        "product.unavailable.title": "Ürün geliri bulunmamaktadır",
        "product.unavailable.detail":
            "Kazanılan siparişlerden ürün karması bilgisi hesaplanamadı.",
        "product.unavailable.action":
            "Ürün analizi yapmadan önce kazanılmış sipariş verilerinin "
            "mevcut olduğunu doğrulayın.",

        # Bölgesel içgörüler
        "region.leaders.title":
            "Bölgesel performans liderleri belirlendi",
        "region.top_revenue":
            "{region}, {value:,.2f} ile en yüksek geliri elde etti.",
        "region.top_average":
            "{region}, {value:,.2f} ile en yüksek ortalama sipariş "
            "değerine ulaştı.",
        "region.leaders.action":
            "Önde gelen bölgelerin satış uygulamalarını karşılaştırın ve "
            "bu uygulamaların diğer bölgelerde kullanılabilirliğini "
            "değerlendirin.",

        # Trend içgörüleri
        "trend.growing.title": "Genel gelir trendi yükseliyor",
        "trend.growing.detail":
            "Doğrusal trend eğimi aylık {value:,.2f} seviyesindedir.",
        "trend.growing.action":
            "Gelecekteki satış hedeflerini belirlerken mevcut trendi "
            "referans olarak kullanın.",

        "trend.declining.title": "Genel gelir trendi düşüyor",
        "trend.declining.detail":
            "Doğrusal trend eğimi aylık {value:,.2f} seviyesindedir.",
        "trend.declining.action":
            "Düşüşe en fazla katkı sağlayan çeyrekleri, ürünleri ve "
            "bölgeleri analiz edin.",

        "trend.stable.title": "Genel gelir trendi sabit",
        "trend.stable.detail":
            "Doğrusal trend eğimi aylık {value:,.2f} seviyesindedir ve "
            "kararlılık toleransı içinde kalmaktadır.",
        "trend.stable.action":
            "Gelecek dönemleri takip edin ve sabit performansı "
            "sürdürülebilir büyümeye dönüştürmeye odaklanın.",

        # Görselleştirme
        "visualizer.generating": "Grafikler oluşturuluyor...",

        "chart.monthly_trend": "Aylık Gelir Trendi",
        "chart.product_mix": "Ürün Bazında Gelir",
        "chart.regional_revenue": "Bölge Bazında Gelir",
        "chart.status_breakdown": "Sipariş Durumu Dağılımı",
        "chart.am_performance": "Müşteri Temsilcisi Performansı",

        "chart.month": "Ay",
        "chart.revenue_usd": "Gelir (USD)",
        "chart.product": "Ürün",
        "chart.region": "Bölge",
        "chart.status": "Durum",
        "chart.count": "Adet",
        "chart.revenue": "Gelir",
        "chart.orders": "Siparişler",
        "chart.account_manager": "Müşteri Temsilcisi",

        "chart.segment_performance": "Müşteri Segmenti Performansı",
        "chart.segment": "Müşteri Segmenti",
        "chart.win_rate": "Kazanma Oranı",

        "chart.revenue_forecast": "Üç Aylık Gelir Tahmini",
        "chart.actual_revenue": "Gerçekleşen Gelir",
        "chart.linear_trend": "Doğrusal Trend",
        "chart.forecast": "Tahmin",
        "chart.forecast_start": "Tahmin Başlangıcı",
        "chart.directional_estimate": "Yön gösterici tahmin",
    },
}


def normalize_language(language: str) -> str:
    """
    Return a supported language code.

    Unsupported values fall back to the default language.
    """

    if not isinstance(language, str):
        return DEFAULT_LANGUAGE

    language = language.lower().strip()

    if language not in SUPPORTED_LANGUAGES:
        return DEFAULT_LANGUAGE

    return language


def translate(
    key: str,
    language: str = DEFAULT_LANGUAGE,
    **kwargs,
) -> str:
    """
    Return the translation associated with a key.

    Falls back to English and then to the key itself.
    """

    selected_language = normalize_language(language)

    text = TRANSLATIONS[selected_language].get(
        key,
        TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key),
    )

    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text