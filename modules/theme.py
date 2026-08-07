"""
Shared visual theme constants for dashboards, reports, and charts.

Keeping the project palette here prevents presentation layers from
silently drifting apart as the UI evolves.
"""

PRIMARY_COLOR = "#2D6A9F"
SECONDARY_COLOR = "#48A999"
ACCENT_COLOR = "#E8855A"
TREND_COLOR = "#8E6BBF"
HIGHLIGHT_COLOR = "#E8C25A"
DARK_TEXT_COLOR = "#173F63"

PALETTE = (
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR,
    TREND_COLOR,
    HIGHLIGHT_COLOR,
)

STATUS_COLORS = {
    "Won": SECONDARY_COLOR,
    "Lost": ACCENT_COLOR,
    "Churned": TREND_COLOR,
}

SEVERITY_COLORS = {
    "critical": ACCENT_COLOR,
    "warning": HIGHLIGHT_COLOR,
    "good": SECONDARY_COLOR,
    "info": PRIMARY_COLOR,
}
