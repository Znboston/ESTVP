"""ESTVP — Earth Surface Temperature Visualization Project.

Generates an interactive temperature analysis dashboard as a self-contained
HTML file and opens it in the default browser.
"""

import os
import webbrowser

from src.data import compute_trend, load_country_data, load_state_data
from src.visualization import build_dashboard

OUTPUT_FILE = "temperature_analysis_dashboard.html"

CUSTOM_CSS = """\
<style>
    body, html {
        margin: 0; padding: 0;
        background-color: #2d2d2d;
        overflow: hidden;
    }
    .modebar-btn, .button {
        background-color: #404040;
        color: #ffffff;
        border: none;
    }
    .button:hover { background-color: #606060; }
</style>
"""


def main():
    print("Loading data...")
    us_data = load_state_data()
    country_data = load_country_data()

    print("Computing trends...")
    us_trend = compute_trend(us_data)
    global_trend = compute_trend(country_data)

    print("Building dashboard...")
    fig = build_dashboard(us_data, country_data, us_trend, global_trend)

    print(f"Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(CUSTOM_CSS + fig.to_html(config={
            "showSendToCloud": False,
            "displayModeBar": False,
            "scrollZoom": False,
        }))

    webbrowser.open("file://" + os.path.realpath(OUTPUT_FILE), new=2)
    print("Done. Dashboard opened in browser.")


if __name__ == "__main__":
    main()
