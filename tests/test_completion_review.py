import ast
import inspect
import json
from pathlib import Path

from openpyxl import Workbook

from data.generate_data import status_probabilities
from modules.domain import KPIBundle
from modules.excel_exporter import _make_workbook_bilingual
from modules.i18n import LOCALES_DIR, TRANSLATIONS
from modules.kpi_engine import AnalysisResult


def test_dashboard_cached_loader_exists_and_is_called():
    project_root = Path(__file__).resolve().parent.parent
    source = (
        project_root
        / "dashboard.py"
    ).read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)

    function_names = {
        node.name
        for node in tree.body
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        )
    }

    assert "load_source_data" in function_names
    assert "raw_orders, raw_customers = load_source_data()" in source
    assert "@st.cache_data" in source


def test_synthetic_status_probabilities_are_context_sensitive():
    from datetime import datetime

    enterprise = status_probabilities(
        "Enterprise",
        "CRM Enterprise",
        datetime(2024, 6, 1),
        "AM_1",
    )
    startup = status_probabilities(
        "Startup",
        "CRM Basic",
        datetime(2023, 6, 1),
        "AM_5",
    )

    assert enterprise != startup
    assert enterprise["Won"] > startup["Won"]
    assert enterprise["Churned"] < startup["Churned"]

    for probabilities in (enterprise, startup):
        assert abs(sum(probabilities.values()) - 1.0) < 1e-9
        assert all(value > 0 for value in probabilities.values())


def test_kpi_public_boundary_uses_typed_bundle():
    annotation = AnalysisResult.__annotations__["kpis"]

    assert annotation is KPIBundle


def test_translations_are_loaded_from_json_files():
    assert LOCALES_DIR.is_dir()

    for language in ("en", "tr"):
        path = LOCALES_DIR / f"{language}.json"
        assert path.is_file()

        data = json.loads(
            path.read_text(encoding="utf-8")
        )
        assert data == TRANSLATIONS[language]


def test_excel_workbook_fixed_labels_become_bilingual():
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "KPI Summary"
    worksheet["A1"] = "Total Revenue"
    worksheet["A2"] = "Win Rate"

    _make_workbook_bilingual(workbook)

    assert workbook.active.title == "Summary - Özet"
    assert workbook.active["A1"].value == "Total Revenue / Toplam Gelir"
    assert workbook.active["A2"].value == "Win Rate / Kazanma Oranı"
