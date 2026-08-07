from pathlib import Path

import pytest


def test_streamlit_dashboard_smoke_run():
    streamlit = pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    project_root = Path(__file__).resolve().parent.parent
    app = AppTest.from_file(
        str(project_root / "dashboard.py")
    )

    app.run(timeout=30)

    assert not app.exception
