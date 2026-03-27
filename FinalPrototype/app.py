import os
import warnings
import webbrowser

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

# 1. Data Acquisition and Preprocessing
print("1. Data Acquisition and Preprocessing")
df = pd.read_csv("archive/Trimmed/Threshold/State-threshold-trimmed.csv")
df = df.dropna()

# Adding ISO country codes - this helps with mapping
country_code_map = {
    "United States": "USA",
    "Canada": "CAN",
    "Brazil": "BRA",
    "Russia": "RUS",
    "China": "CHN",
}

# For US states, we'll add state codes
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

# Print unique countries and states
print("\nUnique countries in dataset:")
print(df["Country"].unique())
print("\nSample of states in dataset:")
print(df["State"].unique()[:10])

# Create US-specific dataset
us_data = df[df["Country"] == "United States"].copy()
us_data["State_Code"] = us_data["State"].map(us_state_code_map)

# Calculate global average temperature for each year
global_temp = df.groupby("Year")["AverageTemperature"].mean().reset_index()
global_temp["TempChange"] = (
    global_temp["AverageTemperature"] - global_temp["AverageTemperature"].iloc[0]
)

# Calculate temperature range for fixed colorscale
temp_min = us_data["AverageTemperature"].min()
temp_max = us_data["AverageTemperature"].max()

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
        "US State Temperature Map",
        "Temperature Data",
        "Temperature Trend",
    ],
)

# Initial choropleth map
initial_year = us_data["Year"].min()
initial_data = us_data[us_data["Year"] == initial_year]

choropleth = go.Choropleth(
    locations=initial_data["State_Code"],
    z=initial_data["AverageTemperature"],
    locationmode="USA-states",
    colorscale="RdBu_r",
    zmin=temp_min,
    zmax=temp_max,
    colorbar_title="Temperature °C",
    text=initial_data["State"],
    hovertemplate="State: %{text}<br>Temperature: %{z:.1f}°C<extra></extra>",
)
fig.add_trace(choropleth, row=1, col=1)

# Add table trace
table = go.Table(
    header=dict(
        values=["Year", "Avg Temp (°C)", "Change from Start (°C)"],
        fill_color="paleturquoise",
        align="left",
    ),
    cells=dict(
        values=[
            global_temp["Year"],
            np.round(global_temp["AverageTemperature"], 2),
            np.round(global_temp["TempChange"], 2),
        ],
        fill_color="lavender",
        align="left",
    ),
)
fig.add_trace(table, row=1, col=2)

# Add temperature trend plot
fig.add_trace(
    go.Scatter(
        x=global_temp["Year"],
        y=global_temp["AverageTemperature"],
        mode="lines+markers",
        name="Average Temperature",
        line=dict(color="red"),
    ),
    row=2,
    col=2,
)

# Update layout with fixed animation controls
fig.update_layout(
    title_text="US State Temperature Dashboard",
    geo=dict(
        scope="usa",
        projection=go.layout.geo.Projection(type="albers usa"),
        showlakes=True,
        lakecolor="rgb(255, 255, 255)",
    ),
    updatemenus=[
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
            "showactive": True,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top",
            "bgcolor": "white",
            "bordercolor": "gray",
            "font": {"size": 12},
        },
    ],
    sliders=[
        {
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 20},
                "prefix": "Year: ",
                "visible": True,
                "xanchor": "right",
            },
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
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
                for year in sorted(us_data["Year"].unique())
            ],
        },
    ],
)

# Create frames for animation
frames = []
for year in sorted(us_data["Year"].unique()):
    year_data = us_data[us_data["Year"] == year]

    frame = go.Frame(
        data=[
            go.Choropleth(
                locations=year_data["State_Code"],
                z=year_data["AverageTemperature"],
                locationmode="USA-states",
                colorscale="RdBu_r",
                zmin=temp_min,
                zmax=temp_max,
                text=year_data["State"],
                hovertemplate="State: %{text}<br>Temperature: %{z:.1f}°C<extra></extra>",
            ),
            go.Table(
                header=dict(
                    values=["Year", "Avg Temp (°C)", "Change from Start (°C)"],
                    fill_color="paleturquoise",
                    align="left",
                ),
                cells=dict(
                    values=[
                        global_temp[global_temp["Year"] <= year]["Year"],
                        np.round(
                            global_temp[global_temp["Year"] <= year][
                                "AverageTemperature"
                            ],
                            2,
                        ),
                        np.round(
                            global_temp[global_temp["Year"] <= year]["TempChange"], 2
                        ),
                    ],
                    fill_color="lavender",
                    align="left",
                ),
            ),
            go.Scatter(
                x=global_temp[global_temp["Year"] <= year]["Year"],
                y=global_temp[global_temp["Year"] <= year]["AverageTemperature"],
                mode="lines+markers",
                name="Average Temperature",
                line=dict(color="red"),
            ),
        ],
        name=str(year),
    )
    frames.append(frame)

fig.frames = frames

# Save with new configuration
output_file = "temperature_analysis_dashboard.html"
fig.write_html(
    output_file,
    config={
        "showSendToCloud": False,
        "displayModeBar": False,
        "scrollZoom": False,
    },
)
print(f"\nDashboard saved as '{output_file}'")
webbrowser.open("file://" + os.path.realpath(output_file), new=2)
