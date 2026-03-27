"""Dashboard figure construction: traces, frames, and layout."""

from datetime import timedelta

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import FRAME_DURATION_MS, THEME, TRANSITION_DURATION_MS
from .data import predict_temperatures


def build_dashboard(us_data, country_data, us_trend, global_trend) -> go.Figure:
    """Construct the full interactive Plotly dashboard figure."""
    fig = make_subplots(
        rows=2, cols=2,
        column_widths=[0.7, 0.3],
        row_heights=[0.7, 0.3],
        specs=[
            [{"type": "choropleth", "rowspan": 2}, {"type": "table"}],
            [None, {"type": "scatter"}],
        ],
        subplot_titles=["Temperature Map", "Temperature Data", "Temperature Trend"],
    )

    # Temperature ranges for fixed color scales
    state_min = us_data["AverageTemperature"].min()
    state_max = us_data["AverageTemperature"].max()
    country_min = country_data["AverageTemperature"].min()
    country_max = country_data["AverageTemperature"].max()

    initial_year = us_data["Year"].dt.year.min()

    # --- Initial traces ---
    _add_choropleth(fig, us_data, initial_year, "USA-states", "State_Code",
                    state_min, state_max, visible=True, name="US States")
    _add_choropleth(fig, country_data, initial_year, "country names", "Country",
                    country_min, country_max, visible=False, name="Countries")
    _add_table(fig, us_trend, dark=True)
    _add_trend_scatter(fig, us_trend)
    _add_prediction_trace(fig)

    # --- Animation frames ---
    frames = _build_frames(us_data, country_data, us_trend,
                           state_min, state_max, country_min, country_max)
    fig.frames = frames

    # --- Layout ---
    _apply_layout(fig, us_trend, global_trend, us_data)

    return fig


def _add_choropleth(fig, data, year, location_mode, location_col,
                    zmin, zmax, visible, name):
    year_data = data[data["Year"].dt.year == year]
    fig.add_trace(
        go.Choropleth(
            locations=year_data[location_col],
            z=year_data["AverageTemperature"],
            locationmode=location_mode,
            colorscale="RdBu_r",
            zmin=zmin, zmax=zmax,
            colorbar_title="Temperature °C",
            hovertemplate=f"{name}: %{{location}}<br>Temperature: %{{z:.1f}}°C<extra></extra>",
            visible=visible,
            name=name,
        ),
        row=1, col=1,
    )


def _add_table(fig, trend, dark=True):
    bg = THEME["surface"] if dark else "paleturquoise"
    cell_bg = THEME["bg"] if dark else "lavender"
    font_color = THEME["text"] if dark else "black"

    fig.add_trace(
        go.Table(
            header=dict(
                values=["Year", "Avg Temp (°C)", "Change from Start (°C)"],
                fill_color=bg, align="left",
                font=dict(color=font_color, size=12),
            ),
            cells=dict(
                values=[
                    trend["Year"].dt.year,
                    np.round(trend["AverageTemperature"], 2),
                    np.round(trend["TempChange"], 2),
                ],
                fill_color=cell_bg, align="left",
                font=dict(color=font_color),
            ),
            visible=True,
        ),
        row=1, col=2,
    )


def _add_trend_scatter(fig, trend):
    fig.add_trace(
        go.Scatter(
            x=trend["Year"], y=trend["AverageTemperature"],
            mode="lines+markers", name="Temperature",
            line=dict(color="red"), visible=True,
        ),
        row=2, col=2,
    )


def _add_prediction_trace(fig):
    fig.add_trace(
        go.Scatter(
            x=[], y=[],
            mode="lines+markers", name="Prediction",
            line=dict(color="purple", dash="dot"),
            marker=dict(color="purple", size=6),
            visible=False,
        ),
        row=2, col=2,
    )


def _build_frames(us_data, country_data, us_trend,
                   state_min, state_max, country_min, country_max):
    frames = []
    for year in sorted(us_data["Year"].dt.year.unique()):
        state_year = us_data[us_data["Year"].dt.year == year]
        country_year = country_data[country_data["Year"].dt.year == year]

        trend_to_year = us_trend[us_trend["Year"].dt.year <= year]
        pred_dates, pred_temps = predict_temperatures(
            trend_to_year["Year"], trend_to_year["AverageTemperature"], year
        )

        frames.append(go.Frame(
            data=[
                go.Choropleth(
                    locations=state_year["State_Code"],
                    z=state_year["AverageTemperature"],
                    locationmode="USA-states", colorscale="RdBu_r",
                    zmin=state_min, zmax=state_max,
                    hovertemplate="State: %{location}<br>Temperature: %{z:.1f}°C<extra></extra>",
                ),
                go.Choropleth(
                    locations=country_year["Country"],
                    z=country_year["AverageTemperature"],
                    locationmode="country names", colorscale="RdBu_r",
                    zmin=country_min, zmax=country_max,
                    hovertemplate="Country: %{location}<br>Temperature: %{z:.1f}°C<extra></extra>",
                ),
                go.Table(
                    header=dict(
                        values=["Year", "Avg Temp (°C)", "Change from Start (°C)"],
                        fill_color=THEME["surface"], align="left",
                        font=dict(color=THEME["text"], size=12),
                    ),
                    cells=dict(
                        values=[
                            trend_to_year["Year"].dt.year,
                            np.round(trend_to_year["AverageTemperature"], 2),
                            np.round(trend_to_year["TempChange"], 2),
                        ],
                        fill_color=THEME["bg"], align="left",
                        font=dict(color=THEME["text"]),
                    ),
                ),
                go.Scatter(
                    x=trend_to_year["Year"],
                    y=trend_to_year["AverageTemperature"],
                    mode="lines+markers", line=dict(color="red"),
                    name="Temperature",
                ),
                go.Scatter(
                    x=pred_dates, y=pred_temps,
                    mode="lines+markers",
                    line=dict(color="purple", dash="dot"),
                    marker=dict(color="purple", size=6),
                    name="Prediction",
                ),
            ],
            name=str(year),
        ))
    return frames


def _apply_layout(fig, us_trend, global_trend, us_data):
    t = THEME
    fig.update_layout(
        title=dict(text="Temperature Dashboard", y=0.95, x=0.5,
                   xanchor="center", yanchor="top",
                   font=dict(size=24, color=t["text"])),
        paper_bgcolor=t["bg"], plot_bgcolor=t["bg"],
        font=dict(color=t["text"]),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(x=1.0, y=0.4, xanchor="right", yanchor="top",
                    bgcolor=f"rgba(45, 45, 45, 0.8)",
                    bordercolor=t["border"], borderwidth=1,
                    font=dict(color=t["text"])),
        updatemenus=[
            _view_selector_menu(t),
            _prediction_toggle_menu(t),
            _animation_controls_menu(t),
        ],
        sliders=[_year_slider(us_data, t)],
        xaxis2=dict(
            autorange=True,
            range=[
                min(us_trend["Year"].min(), global_trend["Year"].min()),
                max(us_trend["Year"].max(), global_trend["Year"].max())
                + timedelta(days=365 * 10),
            ],
            showgrid=True, gridcolor=t["grid"], gridwidth=1, color=t["text"],
        ),
        yaxis2=dict(autorange=True, showgrid=True,
                    gridcolor=t["grid"], gridwidth=1, color=t["text"]),
        geo=dict(
            scope="usa",
            projection=go.layout.geo.Projection(type="albers usa"),
            showlakes=True, lakecolor=t["bg"],
            bgcolor=t["bg"], landcolor=t["land"],
            showframe=False, framecolor=t["surface"],
        ),
    )


def _view_selector_menu(t):
    return {
        "buttons": [
            {"label": "US States", "method": "update",
             "args": [{"visible": [True, False, True, True, True]},
                      {"title": "US State Temperature Dashboard",
                       "geo.scope": "usa", "geo.projection.type": "albers usa"}]},
            {"label": "Countries", "method": "update",
             "args": [{"visible": [False, True, False, True, True]},
                      {"title": "Global Country-Level Temperature Dashboard",
                       "geo.scope": "world", "geo.projection.type": "natural earth"}]},
        ],
        "direction": "down", "showactive": False,
        "x": 0, "xanchor": "left", "y": 1.2, "yanchor": "top",
        "bgcolor": t["button"], "bordercolor": t["border"],
        "font": {"color": t["text"]},
    }


def _prediction_toggle_menu(t):
    return {
        "buttons": [
            {"label": "Show Predictions", "method": "update",
             "args": [{"visible": [True, False, True, True, True]}, {}]},
            {"label": "Hide Predictions", "method": "update",
             "args": [{"visible": [True, False, True, True, False]}, {}]},
        ],
        "direction": "down", "showactive": False,
        "x": 0.7, "xanchor": "left", "y": 0.4, "yanchor": "top",
        "bgcolor": t["button"], "bordercolor": t["border"],
        "font": {"size": 12, "color": t["text"]},
    }


def _animation_controls_menu(t):
    return {
        "buttons": [
            {"args": [None, {"frame": {"duration": FRAME_DURATION_MS, "redraw": True},
                             "fromcurrent": True,
                             "transition": {"duration": TRANSITION_DURATION_MS,
                                            "easing": "quadratic-in-out"}}],
             "label": "Play", "method": "animate"},
            {"args": [[None], {"frame": {"duration": 0, "redraw": False},
                               "mode": "immediate",
                               "transition": {"duration": 0}}],
             "label": "Pause", "method": "animate"},
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 85},
        "showactive": False, "type": "buttons",
        "x": 0.1, "xanchor": "right", "y": 0, "yanchor": "top",
        "bgcolor": t["button"], "bordercolor": t["border"],
        "font": {"size": 12, "color": t["text"]},
    }


def _year_slider(us_data, t):
    return {
        "active": 0, "yanchor": "top", "xanchor": "left",
        "currentvalue": {"font": {"size": 20, "color": t["text"]},
                         "prefix": "Year: ", "visible": True, "xanchor": "right"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9, "x": 0.1, "y": 0,
        "bgcolor": t["button"], "bordercolor": t["border"],
        "steps": [
            {"args": [[str(year)],
                      {"frame": {"duration": TRANSITION_DURATION_MS, "redraw": True},
                       "mode": "immediate",
                       "transition": {"duration": TRANSITION_DURATION_MS}}],
             "label": str(year), "method": "animate"}
            for year in sorted(us_data["Year"].dt.year.unique())
        ],
    }
