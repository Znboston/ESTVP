import os
import warnings
import webbrowser

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression

warnings.filterwarnings("ignore")

# 1. Data Acquisition and Preprocessing
print("1. Data Acquisition and Preprocessing")
df = pd.read_csv("archive/Trimmed/Threshold/Country-threshold-trimmed.csv")
df["Year"] = pd.to_datetime(df["Year"], format="%Y")
df = df.dropna()

# Prepare data for map
df_map = df.copy()
df_map = df_map.groupby(["Year", "Country"])["AverageTemperature"].mean().reset_index()

# Calculate global average temperature for each year
global_temp = df_map.groupby("Year")["AverageTemperature"].mean().reset_index()
global_temp["TempChange"] = (
    global_temp["AverageTemperature"] - global_temp["AverageTemperature"].iloc[0]
)

# 2. Predictions
print("2. Generating Predictions")
X = global_temp["Year"].dt.year.values.reshape(-1, 1)
y = global_temp["AverageTemperature"].values

model = LinearRegression()
model.fit(X, y)

future_years = np.arange(
    global_temp["Year"].dt.year.max() + 1,
    global_temp["Year"].dt.year.max() + 31,
).reshape(-1, 1)
future_temps = model.predict(future_years)

predicted_data = pd.DataFrame(
    {
        "Year": pd.to_datetime(future_years.flatten(), format="%Y"),
        "AverageTemperature": future_temps,
        "TempChange": future_temps - global_temp["AverageTemperature"].iloc[0],
    },
)

all_data = pd.concat([global_temp, predicted_data]).reset_index(drop=True)

# Calculate temperature range for fixed colorscale
temp_min = df_map["AverageTemperature"].min()
temp_max = df_map["AverageTemperature"].max()

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
        "Global Temperature Map",
        "Temperature Data",
        "Global Temperature Trend",
    ],
)

# Initial choropleth map
initial_year = df_map["Year"].dt.year.min()
choropleth = go.Choropleth(
    locations=df_map[df_map["Year"].dt.year == initial_year]["Country"],
    z=df_map[df_map["Year"].dt.year == initial_year]["AverageTemperature"],
    locationmode="country names",
    colorscale="RdBu_r",
    zmin=temp_min,
    zmax=temp_max,
    colorbar_title="Temperature °C",
    hovertemplate="Country: %{location}<br>Temperature: %{z:.1f}°C<extra></extra>",
)
fig.add_trace(choropleth, row=1, col=1)

# Add table trace
table = go.Table(
    header=dict(
        values=["Year", "Global Avg Temp (°C)", "Change from Start (°C)"],
        fill_color="paleturquoise",
        align="left",
    ),
    cells=dict(
        values=[
            global_temp["Year"].dt.year,
            np.round(global_temp["AverageTemperature"], 2),
            np.round(global_temp["TempChange"], 2),
        ],
        fill_color="lavender",
        align="left",
    ),
)
fig.add_trace(table, row=1, col=2)

# Add scatter plot for global temperature trend
scatter = go.Scatter(
    x=all_data["Year"],
    y=all_data["AverageTemperature"],
    mode="lines+markers",
    name="Global Average Temperature",
    line=dict(color="red"),
)
fig.add_trace(scatter, row=2, col=2)

# Update layout with fixed animation controls
fig.update_layout(
    title_text="Global Country-Level Temperature Dashboard",
    geo=dict(
        scope="world",
        projection_type="natural earth",
        showland=True,
        landcolor="lightgrey",
        showocean=True,
        oceancolor="aliceblue",
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
                for year in df_map["Year"].dt.year.unique()
            ],
        },
    ],
)

# Create frames for animation
frames = []
for year in df_map["Year"].dt.year.unique():
    year_data = df_map[df_map["Year"].dt.year == year]

    frame = go.Frame(
        data=[
            go.Choropleth(
                locations=year_data["Country"],
                z=year_data["AverageTemperature"],
                locationmode="country names",
                colorscale="RdBu_r",
                zmin=temp_min,
                zmax=temp_max,
                hovertemplate="Country: %{location}<br>Temperature: %{z:.1f}°C<extra></extra>",
            ),
            go.Table(
                header=dict(
                    values=["Year", "Global Avg Temp (°C)", "Change from Start (°C)"],
                    fill_color="paleturquoise",
                    align="left",
                ),
                cells=dict(
                    values=[
                        all_data[all_data["Year"].dt.year <= year]["Year"].dt.year,
                        np.round(
                            all_data[all_data["Year"].dt.year <= year][
                                "AverageTemperature"
                            ],
                            2,
                        ),
                        np.round(
                            all_data[all_data["Year"].dt.year <= year]["TempChange"],
                            2,
                        ),
                    ],
                    fill_color="lavender",
                    align="left",
                ),
            ),
            go.Scatter(
                x=all_data[all_data["Year"].dt.year <= year]["Year"],
                y=all_data[all_data["Year"].dt.year <= year]["AverageTemperature"],
                mode="lines+markers",
                name="Global Average Temperature",
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
        "scrollZoom": True,
    },
)
print(f"\nDashboard saved as '{output_file}'")
webbrowser.open("file://" + os.path.realpath(output_file), new=2)

print(
    "\nAnalysis complete. The interactive dashboard has been saved and should open in your default web browser.",
)
print("Key features of this visualization:")
print("- Interactive global map showing country-level temperatures")
print("- Time slider and animation controls")
print("- Real-time temperature data table")
print("- Trend analysis with future predictions")
print("- Hover information showing country details")
