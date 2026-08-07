# Python BI Reporting & Decision Support System

A modular **Business Intelligence (BI)** and **Decision Support System** developed in Python as part of my **Software Engineering Internship at KivaCRM**.

The system analyzes synthetic CRM sales data, validates data quality and referential integrity, calculates key business performance indicators (KPIs), performs customer segment analysis, generates revenue forecasts, produces automated business recommendations, and provides bilingual HTML and Streamlit reporting in **English** and **Turkish**.

The core pipeline runs locally and requires no paid APIs. An optional Streamlit interface can also be deployed as a public demo.

---

# Features

## Data Processing

- Synthetic CRM dataset generator
- Automated data validation
- Dataset health report
- CSV-based data pipeline
- Duplicate and missing-value detection
- Invalid data validation (dates, quantities, statuses, revenue)

## KPI Engine

Automatically calculates business metrics including:

- Total Revenue
- Average Order Value
- Month-over-Month (MoM) Revenue Growth
- Win Rate
- Churned-Order Rate
- Product Performance
- Regional Performance
- Sales Performance
- Revenue Trend Analysis

## Customer Segment Analysis

Compares customer segments using:

- Total Revenue
- Share of Selected Revenue
- Revenue per Active Customer
- Average Order Value
- Win Rate
- Churned-Order Rate
- Active Customers
- Best Performing Product

## Revenue Forecasting

Forecasts the next three months using Linear Regression (NumPy Polyfit).

The forecast includes:

- Historical monthly revenue
- Trend line
- Forecast values
- Monthly slope
- R² (coefficient of determination)
- Forecast reliability classification
- Forecast assumptions

## Decision Support Engine

A rule-based decision support engine automatically evaluates KPI results and generates business recommendations.

The engine identifies situations such as:

- Revenue decline
- High churned-order status
- Sales performance
- Regional performance
- Product concentration
- Business trend

Each insight contains:

- Severity level
- Business explanation
- Recommended action

## Reporting

The system automatically generates:

- Interactive bilingual HTML Dashboard
- Interactive bilingual Streamlit Dashboard
- Fully bilingual Excel KPI workbook
- Bilingual Decision Support insights
- Console Summary

## Bilingual Support

The HTML dashboard, Streamlit dashboard, charts, and decision-support insights are available in:

- 🇬🇧 English
- 🇹🇷 Turkish

The Excel workbook is bilingual as well: fixed analytical sheet names, titles, headers, metric labels, forecast metadata, and forecast assumptions are rendered as English / Turkish labels, while the insights sheet keeps separate English and Turkish insight records.

---

## Translation Architecture

All user-facing translations are loaded from:

```text
locales/en.json
locales/tr.json
```

The loader rejects duplicate JSON keys and verifies English/Turkish key parity at startup.

## Security and Deployment

The included data is synthetic. Local Streamlit development is loopback-only and keeps CORS/XSRF protections enabled. Real CRM data must be deployed behind a proper authentication/authorization layer rather than a simple password inside the Streamlit script.

See [`SECURITY.md`](SECURITY.md) and [`deploy/README.md`](deploy/README.md) for the local and hosted deployment profiles.

# Dashboard Preview

## Overview

![Dashboard Overview](screenshots/dashboard-overview.png)

---

## Business Analytics

![Business Analytics](screenshots/dashboard-analytics.png)

---

## Revenue Forecast

![Revenue Forecast](screenshots/dashboard-forecast.png)

---

## Decision Support

![Decision Support](screenshots/dashboard-decisions.png)

---

# Excel Reports

## KPI Summary

<img src="screenshots/excel-kpi-summary.png" width="900">

---

## Revenue Forecast

<img src="screenshots/excel-forecast.png" width="900">

---

# Technologies

- Python
- Pandas
- NumPy
- Matplotlib
- Plotly
- OpenPyXL
- HTML
- CSS

---

# Project Structure

```text
Python-BI-Reporting-System/
│
├── data/
│   ├── customers.csv
│   ├── orders.csv
│   └── generate_data.py
│
├── modules/
│   ├── __init__.py
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
│
├── tests/
├── reports/
├── screenshots/
├── .streamlit/
│   └── config.toml
│
├── dashboard.py
├── data_analysis.py
├── main.py
├── requirements.txt
└── README.md
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/salfayoumi/python-bi-reporting-system.git
```

Install the required packages:

```bash
pip install -r requirements.txt
```

(Optional) Regenerate the synthetic CRM dataset:

```bash
python data/generate_data.py
```

Run the complete pipeline:

```bash
python main.py
```

Run the interactive Streamlit dashboard:

```bash
streamlit run dashboard.py
```

Run automated tests:

```bash
python -m pytest
```

---

# Workflow

The application executes the following pipeline:

```text
Load CRM Data
        │
        ▼
Validate Dataset
        │
        ▼
Compute KPIs
        │
        ▼
Customer Segment Analysis
        │
        ▼
Revenue Forecasting
        │
        ▼
Generate Charts
        │
        ▼
Evaluate Decision-Support Rules Once
        │
        ├──► Localize English Insights
        └──► Localize Turkish Insights
        │
        ▼
Generate HTML Dashboard
        │
        ▼
Generate Excel Report
```

---

# Generated Outputs

Running the project automatically creates:

```text
reports/
│
├── dashboard_<analysis-scope>.html
├── kpi_report_<analysis-scope>.xlsx
└── charts/
```

The HTML dashboard contains:

- Executive KPI Overview
- Monthly Revenue Analysis
- Regional Performance
- Product Performance
- Customer Segment Analysis
- Revenue Forecast
- Decision Support Insights

---

# Security and Data Scope

The repository is a **demo/portfolio BI system built around synthetic CRM data**.

- No real customer or confidential CRM data is included.
- The public Streamlit demo does not implement application authentication because the exposed dataset is synthetic.
- Streamlit CORS/XSRF protections are not disabled.
- Dynamic values inserted into custom HTML are escaped.
- `.streamlit/secrets.toml` is excluded from Git.
- Missing or invalid data files are converted into user-facing errors rather than exposing raw tracebacks.

If this project is connected to real CRM data, it should be placed behind a proper authentication/access-control layer (for example an authenticated reverse proxy or organization platform) rather than relying on a simple password inside the Streamlit script.

# Future Improvements

Possible future extensions include:

- Database integration
- REST API
- Authenticated production deployment for real CRM data
- PDF report generation
- More advanced forecasting models
- CI checks for tests, translation parity, formatting, and linting
- Real-time CRM integration

---

# Internship

This project was developed during my **Software Engineering Internship at KivaCRM**.

The original internship roadmap is available in:

```
Internship_Build_Plan.md
```

The final implementation extends the original roadmap with several additional features, including:

- Customer Segment Analysis
- Revenue Forecasting
- Excel Report Export
- Bilingual Reporting (English & Turkish)
- Data Validation Module
- Enhanced Dashboard Design
- Interactive Plotly Visualizations

---

# Author

**Salsabeel Alfayoumi**

Computer Engineer

Software Engineering • Python • Data Analysis • Business Intelligence • Decision Support Systems

## Tests

```bash
pip install -r requirements.txt
python -m pytest
```


> **Metric note:** `churned_order_rate_pct` is the percentage of order records labelled `Churned`. It is not a customer-level subscription churn metric.
