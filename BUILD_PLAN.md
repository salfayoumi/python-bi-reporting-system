# Python BI Reporting & Decision Support Module
### Internship Project — Salsabeel Alfayoumi

---

## What This Project Does

A fully local, zero-cost Business Intelligence system that:
- Generates a realistic synthetic CRM sales dataset (no real data needed)
- Computes KPIs: revenue, win rate, churn, product mix, trend
- Runs a rule-based decision support engine that flags issues + suggests actions
- Generates 5 charts (Matplotlib static + Plotly interactive)
- Produces a self-contained HTML dashboard report

**Zero cloud. Zero paid APIs. Runs entirely on your laptop.**

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic data (run once)
python data/generate_data.py

# 3. Run the full pipeline
python main.py

# 4. Open the report in your browser
open reports/dashboard.html      # macOS
start reports/dashboard.html     # Windows
xdg-open reports/dashboard.html  # Linux
```

---

## Project Structure

```
salsabeel_bi/
│
├── data/
│   ├── generate_data.py    ← synthetic dataset generator
│   ├── customers.csv       ← 200 customers (auto-generated)
│   └── orders.csv          ← 1500 orders   (auto-generated)
│
├── modules/
│   ├── kpi_engine.py       ← KPI calculations (revenue, sales, product, region, trend)
│   ├── visualizer.py       ← chart generation (Matplotlib + Plotly)
│   ├── decision_support.py ← rule-based insight & action engine
│   └── report_generator.py ← HTML report builder
│
├── reports/
│   ├── dashboard.html      ← final HTML report (open in browser)
│   └── charts/             ← individual chart files (.png / .html)
│
├── main.py                 ← single entry point, runs all 4 steps
├── requirements.txt
└── README.md
```

---

## 20-Day Build Plan

This maps each internship day to a concrete coding task.

### Week 1 — Data Foundation

| Day | Task | File(s) |
|-----|------|---------|
| 1 | Study the project. Sketch the data model on paper. Define 5 KPIs you want to measure. | — |
| 2 | Understand `orders.csv` and `customers.csv` structure. Write pandas `describe()` analysis. | `data/` |
| 3 | Build `load_data()` in `kpi_engine.py`. Read CSVs, parse dates, check dtypes. | `kpi_engine.py` |
| 4 | Add data validation: check for nulls, negative amounts, unknown statuses. Print a health report. | `kpi_engine.py` |
| 5 | Define your 5 KPIs formally (formula + benchmark + source column). Write them as comments. | — |

**Week 1 deliverable:** Working `load_data()`, data validation report, KPI definitions document.

---

### Week 2 — KPI Engine + Analysis

| Day | Task | File(s) |
|-----|------|---------|
| 6 | Implement `revenue_kpis()`: total revenue, avg order value, MoM growth. | `kpi_engine.py` |
| 7 | Implement `sales_kpis()`: win rate, churn rate, top account manager. | `kpi_engine.py` |
| 8 | Implement `trend_analysis()`: monthly/quarterly groupby, linear trend slope via `numpy.polyfit`. | `kpi_engine.py` |
| 9 | Add `product_kpis()` and `regional_kpis()`. Build `compute_all_kpis()` master function. | `kpi_engine.py` |
| 10 | Write `modules/report_generator.py` — start with plain text, then upgrade to HTML template. | `report_generator.py` |

**Week 2 deliverable:** All KPI functions working. CLI output showing all metrics. Basic report file.

---

### Week 3 — Visualizations + Decision Support

| Day | Task | File(s) |
|-----|------|---------|
| 11 | Design the decision support logic on paper. Define 5 rules with thresholds and actions. | — |
| 12 | Implement `modules/decision_support.py` — `Insight` dataclass, `analyze()`, `format_report()`. | `decision_support.py` |
| 13 | Build `plot_monthly_trend()` in `visualizer.py` using Matplotlib. | `visualizer.py` |
| 14 | Build `plot_product_mix()` and `plot_status_breakdown()` using Plotly. | `visualizer.py` |
| 15 | Build `plot_regional_revenue()` and `plot_am_performance()`. Run all charts end-to-end. | `visualizer.py` |

**Week 3 deliverable:** Decision support report running. All 5 charts generating correctly.

---

### Week 4 — Integration + Polish

| Day | Task | File(s) |
|-----|------|---------|
| 16 | Embed charts into HTML report. Validate all KPI numbers are correct by checking manually. | `report_generator.py` |
| 17 | Improve HTML styling. Add color coding (green/yellow/red) to KPI cards based on thresholds. | `report_generator.py` |
| 18 | Write technical documentation: what each function does, inputs, outputs, assumptions. | `docs/` |
| 19 | Write the final report: project goals, what was built, what you learned, what could be improved. | `docs/` |
| 20 | Final review. Clean up code. Add comments. Test from a fresh install. Package and submit. | — |

**Week 4 deliverable:** Polished HTML dashboard. Full technical docs. Final report. Clean repo.

---

## Extension Ideas (if you finish early)

1. **Excel export** — use `openpyxl` to export the KPI table as a formatted `.xlsx` file
2. **Segment comparison** — add a filter to compare Enterprise vs SMB vs Startup
3. **Forecast** — extend the trend line 3 months forward using `numpy.polyfit`
4. **CLI flags** — `python main.py --region Istanbul --year 2024` filtering
5. **Streamlit dashboard** — convert the HTML report into a live interactive app (`pip install streamlit`)

---

## Key Python Concepts You Will Practice

| Concept | Where |
|---------|-------|
| `pandas` groupby, agg, merge | `kpi_engine.py` |
| `numpy` polyfit (linear regression) | `kpi_engine.py` |
| `matplotlib` subplots, formatters | `visualizer.py` |
| `plotly` express + graph_objects | `visualizer.py` |
| Python dataclasses | `decision_support.py` |
| f-strings, string formatting | `report_generator.py` |
| File I/O, `os.makedirs` | all modules |
| Type hints (`list[Insight]`, `dict`) | all modules |
| `if __name__ == "__main__"` pattern | all modules |

---

## Questions to Answer in Your Final Report

1. What is a KPI and how did you decide which ones to measure?
2. What does "MoM growth" mean and how is it calculated?
3. What is a linear trend slope and what does it tell a business?
4. What is the difference between a "Lost" and "Churned" order in your dataset?
5. If you had real KivaCRM data, what would you change about this project?
