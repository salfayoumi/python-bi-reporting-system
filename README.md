# Python Data Analytics & Decision Support System

A modular Python application that turns synthetic CRM data into validated datasets, business metrics, forecasts, automated insights, and bilingual reports.

The project demonstrates practical **Python engineering, data analysis, automation, visualization, testing, and application security**. It was completed during a software engineering internship in July–August 2026.

## Project at a glance

| Area | Implementation |
|---|---|
| Data pipeline | CSV ingestion, validation, quality reporting |
| Analysis | KPIs, customer segments, products, regions, sales |
| Forecasting | Three-month revenue trend with reliability indicators |
| Decision support | Rule-based findings and recommended actions |
| Interfaces | Streamlit dashboard, HTML dashboard, Excel workbook |
| Languages | English and Turkish |
| Data | Fully synthetic CRM records |

## What the system does

- Generates or loads synthetic CRM data
- Validates data quality and referential integrity
- Calculates operational and revenue KPIs
- Compares customer, product, regional, and sales performance
- Forecasts the next three months of revenue
- Converts analytical findings into explainable recommendations
- Produces bilingual interactive and exportable reports

## Dashboard preview

### Overview

![Dashboard overview](screenshots/dashboard-overview.png)

### Business analytics

![Business analytics](screenshots/dashboard-analytics.png)

### Revenue forecast

![Revenue forecast](screenshots/dashboard-forecast.png)

### Decision support

![Decision-support findings](screenshots/dashboard-decisions.png)

## Engineering highlights

### Modular Python architecture

The application separates domain logic, validation, analysis, forecasting, localization, visualization, and export behavior into focused modules. This keeps the core calculations reusable across the command-line pipeline, Streamlit interface, HTML dashboard, and Excel output.

### Data validation

The pipeline checks for:

- Missing and duplicate records
- Invalid dates, quantities, statuses, and revenue values
- Broken relationships between datasets
- Dataset health issues before analysis begins

### Analytics and forecasting

The analysis layer calculates metrics such as total revenue, average order value, month-over-month growth, win rate, order-level churn status, and product, regional, sales, and customer-segment performance.

A three-month revenue forecast uses a linear trend model and reports the slope, coefficient of determination, assumptions, and a reliability classification. The model is intentionally simple and explainable.

### Decision-support rules

A rule engine evaluates the analytical results and generates structured findings with:

- Severity
- Explanation
- Recommended action

This keeps the generated advice traceable to a specific metric or threshold rather than presenting a black-box recommendation.

### Bilingual reporting

English and Turkish interface text is loaded from:

```text
locales/en.json
locales/tr.json
```

The loader rejects duplicate JSON keys and verifies translation-key parity at startup. Dashboards, charts, workbook labels, forecast metadata, and insights are localized consistently.

## Technology

- Python
- Pandas
- NumPy
- Plotly
- Matplotlib
- OpenPyXL
- Streamlit
- Pytest
- HTML and CSS

## Project structure

```text
python-bi-reporting-system/
├── data/
│   ├── customers.csv
│   ├── orders.csv
│   └── generate_data.py
├── deploy/
├── locales/
│   ├── en.json
│   └── tr.json
├── modules/
│   ├── decision_support.py
│   ├── domain.py
│   ├── excel_exporter.py
│   ├── forecast.py
│   ├── i18n.py
│   ├── kpi_engine.py
│   ├── report_generator.py
│   ├── segment_analysis.py
│   ├── theme.py
│   └── visualizer.py
├── reports/
├── screenshots/
├── tests/
├── dashboard.py
├── data_analysis.py
├── main.py
├── requirements.txt
└── SECURITY.md
```

## Run locally

1. Clone the repository:

```bash
git clone https://github.com/salfayoumi/python-bi-reporting-system.git
cd python-bi-reporting-system
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Optionally regenerate the synthetic data:

```bash
python data/generate_data.py
```

4. Run the complete reporting pipeline:

```bash
python main.py
```

5. Or start the interactive dashboard:

```bash
streamlit run dashboard.py
```

6. Run the automated tests:

```bash
python -m pytest
```

## Generated outputs

The command-line pipeline creates:

```text
reports/
├── dashboard_<analysis-scope>.html
├── kpi_report_<analysis-scope>.xlsx
└── charts/
```

## Security and data scope

This is a portfolio application built around synthetic data; it contains no real customer or confidential CRM records.

- Streamlit CORS and XSRF protections remain enabled
- Dynamic values inserted into custom HTML are escaped
- `.streamlit/secrets.toml` is excluded from Git
- Invalid input becomes a user-facing error rather than a raw traceback
- A real-data deployment would require organizational authentication and access control

See [SECURITY.md](SECURITY.md) and [deploy/README.md](deploy/README.md) for additional details.

## Limitations and next steps

The forecasting method is a transparent baseline, not a production forecasting service. Useful next extensions include:

- Database and REST API integration
- Time-series model comparison and backtesting
- Authenticated deployment for real organizational data
- CI checks for tests, formatting, linting, and translation parity
- Real-time data ingestion
- Additional explainability and data-drift monitoring

> **Metric note:** `churned_order_rate_pct` is the percentage of order records labelled `Churned`; it is not a customer-level subscription churn metric.

## Author

**Salsabeel Alfayoumi**  
Computer Engineer focused on Python, applied AI, data analysis, and intelligent systems.

[Portfolio](https://salfayoumi.github.io/) · [GitHub profile](https://github.com/salfayoumi)
