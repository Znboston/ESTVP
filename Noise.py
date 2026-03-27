import os

import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dash_table import DataTable
from dash.dash_table.Format import Format
from dash.dependencies import Input, Output

# Get the base directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct relative file paths
file_paths = {
    "Global": os.path.join(base_dir, "archive", "Raw", "GlobalTemperatures.csv"),
    "Country": os.path.join(
        base_dir,
        "archive",
        "Raw",
        "GlobalLandTemperaturesByCountry.csv",
    ),
    "State": os.path.join(
        base_dir,
        "archive",
        "Raw",
        "GlobalLandTemperaturesByState.csv",
    ),
    "Major City": os.path.join(
        base_dir,
        "archive",
        "Raw",
        "GlobalLandTemperaturesByMajorCity.csv",
    ),
    "City": os.path.join(
        base_dir,
        "archive",
        "Raw",
        "GlobalLandTemperaturesByCity.csv",
    ),
}

# Temperature uncertainty column names for each dataset
temp_uncertainty_cols = {
    "Global": "LandAverageTemperatureUncertainty",
    "Country": "AverageTemperatureUncertainty",
    "State": "AverageTemperatureUncertainty",
    "Major City": "AverageTemperatureUncertainty",
    "City": "AverageTemperatureUncertainty",
}

# Dictionary to hold processed data
data_dict = {}

# Process each dataset and store it in data_dict
for name, path in file_paths.items():
    try:
        # Load the dataset
        df = pd.read_csv(path)

        # Handle missing values by removing rows with missing uncertainties
        df = df.dropna(subset=[temp_uncertainty_cols[name]])

        # Convert 'dt' column to datetime format
        df["dt"] = pd.to_datetime(df["dt"])

        # Extract year from 'dt' column for plotting
        df["Year"] = df["dt"].dt.year

        # Group by year and calculate mean uncertainty
        annual_uncertainty = (
            df.groupby("Year")[temp_uncertainty_cols[name]].mean().reset_index()
        )

        # Add to data_dict
        data_dict[name] = annual_uncertainty

    except Exception as e:
        print(f"Error processing {name}: {e}")

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Temperature Uncertainty Over Years", style={"text-align": "center"}),
        dcc.Checklist(
            id="all-datasets-checkbox",
            options=[{"label": "Plot All Datasets", "value": "all"}],
            value=[],
            style={"margin": "10px", "color": "#ffffff"},
        ),
        dcc.Dropdown(
            id="dataset-dropdown",
            options=[{"label": name, "value": name} for name in data_dict],
            value="Global",
            clearable=False,
            style={"width": "50%", "margin": "auto"},
        ),
        dcc.Graph(id="uncertainty-graph"),
        html.H2("Uncertainty Table", style={"text-align": "center"}),
        DataTable(
            id="uncertainty-table",
            style_cell={"background-color": "#333333", "color": "#ffffff"},
            style_header={"backgroundColor": "#444444", "color": "#ffffff"},
            style_table={"overflowX": "auto"},
        ),
        html.Button(
            "Export Table to CSV",
            id="export-button",
            style={"margin-top": "10px"},
        ),
        html.Div(id="export-confirmation", style={"margin-top": "10px"}),
    ],
)


@app.callback(
    [
        Output("uncertainty-graph", "figure"),
        Output("uncertainty-table", "data"),
        Output("uncertainty-table", "columns"),
    ],
    [Input("dataset-dropdown", "value"), Input("all-datasets-checkbox", "value")],
)
def update_graph_and_table(selected_dataset, all_datasets):
    if "all" in all_datasets:
        # Plot all datasets together
        fig = px.line()
        for name, df in data_dict.items():
            fig.add_scatter(
                x=df["Year"],
                y=df[temp_uncertainty_cols[name]],
                mode="lines",
                name=name,
            )
        fig.update_layout(
            title="Temperature Uncertainty - All Datasets",
            xaxis_title="Year",
            yaxis_title="Uncertainty (°C)",
            plot_bgcolor="#2d2d2d",
            paper_bgcolor="#2d2d2d",
            font={"color": "#ffffff"},
        )
        table_data = []
        table_columns = [{"name": "Year", "id": "Year"}]
    else:
        # Plot only the selected dataset
        df = data_dict[selected_dataset]
        fig = px.line(
            df,
            x="Year",
            y=temp_uncertainty_cols[selected_dataset],
            title=f"Temperature Uncertainty - {selected_dataset}",
            labels={
                "Year": "Year",
                temp_uncertainty_cols[selected_dataset]: "Uncertainty (°C)",
            },
            template="plotly_dark",
        )

        # Filter data for major years (e.g., every 10 years)
        major_years = df[df["Year"] % 10 == 0]

        # Prepare data for the DataTable
        table_data = major_years.to_dict("records")
        table_columns = [
            {"name": "Year", "id": "Year"},
            {
                "name": "Uncertainty (°C)",
                "id": temp_uncertainty_cols[selected_dataset],
                "type": "numeric",
                "format": Format(precision=2),
            },
        ]

    return fig, table_data, table_columns


@app.callback(
    Output("export-confirmation", "children"),
    [Input("export-button", "n_clicks"), Input("dataset-dropdown", "value")],
)
def export_table_to_csv(n_clicks, selected_dataset):
    if n_clicks:
        df = data_dict[selected_dataset]
        major_years = df[df["Year"] % 10 == 0]
        filename = f"{selected_dataset}_uncertainty_major_years.csv"
        df.to_csv(filename, index=False)
        return f"Table exported as {filename}"


# Automatically open the web browser when the app runs
# def open_browser():
#    webbrowser.open_new("http://127.0.0.1:8050/")


if __name__ == "__main__":
    # open_browser()
    app.run_server(debug=True)
