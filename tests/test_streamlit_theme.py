from pathlib import Path


def test_streamlit_config_defines_switchable_light_and_dark_themes():
    project_root = Path(__file__).resolve().parent.parent
    config = (
        project_root
        / ".streamlit"
        / "config.toml"
    ).read_text(
        encoding="utf-8"
    )

    assert "[theme.light]" in config
    assert "[theme.dark]" in config
    assert 'base = "light"' not in config
    assert 'address = "127.0.0.1"' in config
    assert "enableCORS = true" in config
    assert "enableXsrfProtection = true" in config


def test_dashboard_does_not_force_light_only_card_colors():
    project_root = Path(__file__).resolve().parent.parent
    source = (
        project_root
        / "dashboard.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "background: white" not in source
    assert 'paper_bgcolor="white"' not in source
    assert 'plot_bgcolor="white"' not in source
    assert "DARK_TEXT_COLOR" not in source
    assert "color: inherit" in source
