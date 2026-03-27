import os
import warnings
import webbrowser
from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression

warnings.filterwarnings("ignore")


# Helper function for predictions
def get_predictions(dates, temperatures, current_year, predict_years=10):
    """Calculate predictions with persistent points"""
    X = np.array([(d.year + d.dayofyear / 365) for d in dates]).reshape(-1, 1)
    y = temperatures

    model = LinearRegression()
    model.fit(X, y)

    # Calculate yearly predictions up to current point
    prediction_years = np.arange(
        min(dates).year,
        current_year + predict_years + 1,
        1,
    ).reshape(-1, 1)

    y_pred = model.predict(prediction_years)

    # Create datetime objects for prediction dates
    prediction_dates = [
        pd.Timestamp(year=int(year), month=1, day=1)
        for year in prediction_years.flatten()
    ]

    return prediction_dates, y_pred


# Data Acquisition and Preprocessing
print("1. Data Acquisition and Preprocessing")

# Load both datasets
state_df = pd.read_csv("archive/Trimmed/Threshold/State-threshold-trimmed.csv")
state_df = state_df.dropna()

# Clean state names
state_df["State"] = state_df["State"].replace("Georgia (State)", "Georgia")

country_df = pd.read_csv("archive/Trimmed/Threshold/Country-threshold-trimmed.csv")
country_df["Year"] = pd.to_datetime(country_df["Year"], format="%Y")
country_df = country_df.dropna()

# State data processing
us_state_code_map = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

# Process US state data
us_data = state_df[state_df["Country"] == "United States"].copy()
us_data["State_Code"] = us_data["State"].map(us_state_code_map)
us_data["Year"] = pd.to_datetime(us_data["Year"], format="%Y")

# Process country data
country_data = (
    country_df.groupby(["Year", "Country"])["AverageTemperature"].mean().reset_index()
)

# Calculate temperature ranges
state_temp_min = us_data["AverageTemperature"].min()
state_temp_max = us_data["AverageTemperature"].max()
country_temp_min = country_data["AverageTemperature"].min()
country_temp_max = country_data["AverageTemperature"].max()

# Calculate average temperatures for trend data
us_temp = us_data.groupby("Year")["AverageTemperature"].mean().reset_index()
us_temp["TempChange"] = (
    us_temp["AverageTemperature"] - us_temp["AverageTemperature"].iloc[0]
)

global_temp = country_data.groupby("Year")["AverageTemperature"].mean().reset_index()
global_temp["TempChange"] = (
    global_temp["AverageTemperature"] - global_temp["AverageTemperature"].iloc[0]
)

# Create the dashboard
fig = make_subplots(
    rows=2,
    cols=2,
    column_widths=[0.7, 0.3],
    row_heights=[0.7, 0.3],
    specs=[
        [{"type": "choropleth", "rowspan": 2}, {"type": "table"}],
        [None, {"type": "scatter"}],
    ],
    subplot_titles=[
        "Temperature Map",
        "Temperature Data",
        "Temperature Trend",
    ],
)

# Add initial traces for both visualizations (state and country)
# State visualization
fig.add_trace(
    go.Choropleth(
        locations=us_data[us_data["Year"].dt.year == us_data["Year"].dt.year.min()][
            "State_Code"
        ],
        z=us_data[us_data["Year"].dt.year == us_data["Year"].dt.year.min()][
            "AverageTemperature"
        ],
        locationmode="USA-states",
        colorscale="RdBu_r",
        zmin=state_temp_min,
        zmax=state_temp_max,
        colorbar_title="Temperature °C",
        hovertemplate="State: %{location}<br>Temperature: %{z:.1f}°C<extra></extra>",
        visible=True,
        name="US States",
    ),
    row=1,
    col=1,
)

# Country visualization
fig.add_trace(
    go.Choropleth(
        locations=country_data[
            country_data["Year"].dt.year == country_data["Year"].dt.year.min()
        ]["Country"],
        z=country_data[
            country_data["Year"].dt.year == country_data["Year"].dt.year.min()
        ]["AverageTemperature"],
        locationmode="country names",
        colorscale="RdBu_r",
        zmin=country_temp_min,
        zmax=country_temp_max,
        colorbar_title="Temperature °C",
        hovertemplate="Country: %{location}<br>Temperature: %{z:.1f}°C<extra></extra>",
        visible=False,
        name="Countries",
    ),
    row=1,
    col=1,
)

# Initial table and scatter for US states
fig.add_trace(
    go.Table(
        header=dict(
            values=["Year", "Avg Temp (°C)", "Change from Start (°C)"],
            fill_color="paleturquoise",
            align="left",
        ),
        cells=dict(
            values=[
                us_temp["Year"].dt.year,
                np.round(us_temp["AverageTemperature"], 2),
                np.round(us_temp["TempChange"], 2),
            ],
            fill_color="lavender",
            align="left",
        ),
        visible=True,
    ),
    row=1,
    col=2,
)

# Add temperature trace
fig.add_trace(
    go.Scatter(
        x=us_temp["Year"],
        y=us_temp["AverageTemperature"],
        mode="lines+markers",
        name="Temperature",
        line=dict(color="red"),
        visible=True,
    ),
    row=2,
    col=2,
)

# Add prediction trace (initially empty)
fig.add_trace(
    go.Scatter(
        x=[],
        y=[],
        mode="lines+markers",
        name="Prediction",
        line=dict(color="purple", dash="dot"),
        marker=dict(color="purple", size=6),
        visible=False,
    ),
    row=2,
    col=2,
)

# Modify the Table trace creation:
fig.add_trace(
    go.Table(
        header=dict(
            values=["Year", "Avg Temp (°C)", "Change from Start (°C)"],
            fill_color="#1f1f1f",  # Darker background for header
            align="left",
            font=dict(color="#ffffff", size=12),
        ),
        cells=dict(
            values=[
                us_temp["Year"].dt.year,
                np.round(us_temp["AverageTemperature"], 2),
                np.round(us_temp["TempChange"], 2),
            ],
            fill_color="#2d2d2d",  # Darker background for cells
            align="left",
            font=dict(color="#ffffff"),
        ),
        visible=True,
    ),
    row=1,
    col=2,
)

# Update layout
fig.update_layout(
    title={
        "text": "Temperature Dashboard",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
        "font": {"size": 24, "color": "#ffffff"},
    },
    paper_bgcolor="#2d2d2d",  # Set background color for the page
    plot_bgcolor="#2d2d2d",  # Set background color for plots
    font=dict(color="#ffffff"),
    margin=dict(l=0, r=0, t=0, b=0),  # Remove plot margins
    showlegend=True,
    legend=dict(
        x=1.0,
        y=0.4,
        xanchor="right",
        yanchor="top",
        bgcolor="rgba(45, 45, 45, 0.8)",
        bordercolor="#555555",
        borderwidth=1,
        font=dict(color="#ffffff"),
    ),
    updatemenus=[
        # View selector dropdown with simplified styling
        {
            "buttons": [
                {
                    "label": "US States",
                    "method": "update",
                    "args": [
                        {"visible": [True, False, True, True, True]},
                        {
                            "title": "US State Temperature Dashboard",
                            "geo.scope": "usa",
                            "geo.projection.type": "albers usa",
                        },
                    ],
                },
                {
                    "label": "Countries",
                    "method": "update",
                    "args": [
                        {"visible": [False, True, False, True, True]},
                        {
                            "title": "Global Country-Level Temperature Dashboard",
                            "geo.scope": "world",
                            "geo.projection.type": "natural earth",
                        },
                    ],
                },
            ],
            "direction": "down",
            "showactive": False,
            "x": 0,
            "xanchor": "left",
            "y": 1.2,
            "yanchor": "top",
            "bgcolor": "#404040",
            "bordercolor": "#555555",
            "font": {"color": "#ffffff"},
        },
        # Prediction toggle
        {
            "buttons": [
                {
                    "label": "Show Predictions",
                    "method": "update",
                    "args": [{"visible": [True, False, True, True, True]}, {}],
                },
                {
                    "label": "Hide Predictions",
                    "method": "update",
                    "args": [{"visible": [True, False, True, True, False]}, {}],
                },
            ],
            "direction": "down",
            "showactive": False,
            "x": 0.7,
            "xanchor": "left",
            "y": 0.4,
            "yanchor": "top",
            "bgcolor": "#404040",
            "bordercolor": "#555555",
            "font": {"size": 12, "color": "#ffffff"},
        },
        # Animation controls
        {
            "buttons": [
                {
                    "args": [
                        None,
                        {
                            "frame": {"duration": 500, "redraw": True},
                            "fromcurrent": True,
                            "transition": {
                                "duration": 300,
                                "easing": "quadratic-in-out",
                            },
                        },
                    ],
                    "label": "Play",
                    "method": "animate",
                },
                {
                    "args": [
                        [None],
                        {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0},
                        },
                    ],
                    "label": "Pause",
                    "method": "animate",
                },
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 85},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top",
            "bgcolor": "#404040",
            "bordercolor": "#555555",
            "font": {"size": 12, "color": "#ffffff"},
        },
    ],
    sliders=[
        {
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 20, "color": "#ffffff"},
                "prefix": "Year: ",
                "visible": True,
                "xanchor": "right",
            },
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "bgcolor": "#404040",
            "bordercolor": "#555555",
            "steps": [
                {
                    "args": [
                        [str(year)],
                        {
                            "frame": {"duration": 300, "redraw": True},
                            "mode": "immediate",
                            "transition": {"duration": 300},
                        },
                    ],
                    "label": str(year),
                    "method": "animate",
                }
                for year in sorted(us_data["Year"].dt.year.unique())
            ],
        },
    ],
    xaxis2=dict(
        autorange=True,
        range=[
            min(us_temp["Year"].min(), global_temp["Year"].min()),
            max(us_temp["Year"].max(), global_temp["Year"].max())
            + timedelta(days=365 * 10),
        ],
        showgrid=True,
        gridcolor="#404040",
        gridwidth=1,
        color="#ffffff",
    ),
    yaxis2=dict(
        autorange=True,
        showgrid=True,
        gridcolor="#404040",
        gridwidth=1,
        color="#ffffff",
    ),
    geo=dict(
        scope="usa",
        projection=go.layout.geo.Projection(type="albers usa"),
        showlakes=True,
        lakecolor="#2d2d2d",
        bgcolor="#2d2d2d",
        landcolor="#444444",
        showframe=False,  # Remove frame around map
        framecolor="#1f1f1f",
    ),
)

# Create frames for animation
frames = []
years = sorted(us_data["Year"].dt.year.unique())
for year in years:
    state_year_data = us_data[us_data["Year"].dt.year == year]
    country_year_data = country_data[country_data["Year"].dt.year == year]

    # Calculate predictions based on data up to current year
    current_dates = us_temp[us_temp["Year"].dt.year <= year]["Year"]
    current_temps = us_temp[us_temp["Year"].dt.year <= year]["AverageTemperature"]
    pred_dates, pred_temps = get_predictions(current_dates, current_temps, year)

    frame = go.Frame(
        data=[
            # State choropleth
            go.Choropleth(
                locations=state_year_data["State_Code"],
                z=state_year_data["AverageTemperature"],
                locationmode="USA-states",
                colorscale="RdBu_r",
                zmin=state_temp_min,
                zmax=state_temp_max,
                hovertemplate="State: %{location}<br>Temperature: %{z:.1f}°C<extra></extra>",
            ),
            # Country choropleth
            go.Choropleth(
                locations=country_year_data["Country"],
                z=country_year_data["AverageTemperature"],
                locationmode="country names",
                colorscale="RdBu_r",
                zmin=country_temp_min,
                zmax=country_temp_max,
                hovertemplate="Country: %{location}<br>Temperature: %{z:.1f}°C<extra></extra>",
            ),
            # State table
            go.Table(
                header=dict(
                    values=["Year", "Avg Temp (°C)", "Change from Start (°C)"],
                    fill_color="paleturquoise",
                    align="left",
                ),
                cells=dict(
                    values=[
                        us_temp[us_temp["Year"].dt.year <= year]["Year"].dt.year,
                        np.round(
                            us_temp[us_temp["Year"].dt.year <= year][
                                "AverageTemperature"
                            ],
                            2,
                        ),
                        np.round(
                            us_temp[us_temp["Year"].dt.year <= year]["TempChange"],
                            2,
                        ),
                    ],
                    fill_color="lavender",
                    align="left",
                ),
            ),
            # Temperature scatter
            go.Scatter(
                x=us_temp[us_temp["Year"].dt.year <= year]["Year"],
                y=us_temp[us_temp["Year"].dt.year <= year]["AverageTemperature"],
                mode="lines+markers",
                line=dict(color="red"),
                name="Temperature",
            ),
            # Prediction scatter
            go.Scatter(
                x=pred_dates,
                y=pred_temps,
                mode="lines+markers",
                line=dict(color="purple", dash="dot"),
                marker=dict(color="purple", size=6),
                name="Prediction",
            ),
        ],
        name=str(year),
    )
    frames.append(frame)

fig.frames = frames

# CSS for dark mode buttons and other style overrides
custom_css = """
    <style>
        /* Remove white borders and margins */
        body, html {
            margin: 0;
            padding: 0;
            background-color: #2d2d2d;
            overflow: hidden;
        }
        /* Style for all buttons, including hover and active */
        .modebar-btn,
        .modebar-btn:hover,
        .modebar-btn:active,
        .modebar-btn:focus,
        .button,
        .button:hover,
        .button:active,
        .button:focus {
            background-color: #404040;
            color: #ffffff;
            border: none;
            box-shadow: none;
            outline: none;
        }
        /* Play and Pause buttons styling */
        .button-container .button {
            background-color: #404040;
            color: #ffffff;
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 14px;
            margin: 0 5px;
            transition: background-color 0.3s;
        }
        /* Hover effect */
        .button-container .button:hover {
            background-color: #606060;
        }
        /* Active state for Play and Pause buttons */
        .button-container .button:active,
        .button-container .button:focus {
            background-color: #505050;
        }
    </style>
"""

# Make sure to inject this CSS at the beginning of your HTML output
output_file = "temperature_analysis_dashboard.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(
        custom_css
        + fig.to_html(
            config={
                "showSendToCloud": False,
                "displayModeBar": False,
                "scrollZoom": False,
            },
        ),
    )

print(f"\nDashboard saved as '{output_file}'")
webbrowser.open("file://" + os.path.realpath(output_file), new=2)


print(
    "\nAnalysis complete. The interactive dashboard has been saved and should open in your default web browser.",
)
print("Key features of this visualization:")
print("- Switch between US States and Countries view")
print("- Interactive temperature map with fixed color scale")
print("- Time slider and animation controls")
print("- Dynamic temperature trend graph")
print("- Predictive modeling with persistent points")
print("- 10-year future predictions")
