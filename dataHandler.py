import os
import webbrowser

import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dash_table import DataTable
from dash.dependencies import Input, Output, State
from scipy.stats import zscore
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from tqdm import tqdm

# Base directory setup
base_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths for each dataset
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

# Threshold for uncertainty based on the desired human-level accuracy
uncertainty_threshold = 1.1  # Degrees Celsius

# Dictionary to store preprocessed data
data_dict = {}

# Load and process each dataset with a progress bar
print("Loading datasets...")
for name, path in tqdm(file_paths.items(), desc="Loading Data"):
    try:
        df = pd.read_csv(path)
        df = df.dropna(subset=[temp_uncertainty_cols[name]])
        df["Year"] = pd.to_datetime(df["dt"]).dt.year
        data_dict[name] = df  # Store preloaded data in the dictionary
    except Exception as e:
        print(f"Error loading {name}: {e}")


# Define outlier detection functions
def threshold_filter(data, uncertainty_col, threshold=uncertainty_threshold):
    data["Outlier"] = data[uncertainty_col] > threshold
    return data


def z_score_outliers(data, uncertainty_col):
    threshold = 3  # Z-score threshold
    z_scores = np.abs(zscore(data[uncertainty_col]))
    data["Outlier"] = z_scores > threshold
    return data


def iqr_outliers(data, uncertainty_col):
    Q1 = data[uncertainty_col].quantile(0.25)
    Q3 = data[uncertainty_col].quantile(0.75)
    IQR = Q3 - Q1
    data["Outlier"] = (data[uncertainty_col] < (Q1 - 1.5 * IQR)) | (
        data[uncertainty_col] > (Q3 + 1.5 * IQR)
    )
    return data


def isolation_forest_outliers(data, uncertainty_col):
    model = IsolationForest(contamination=0.05)
    data["Outlier"] = model.fit_predict(data[[uncertainty_col]]) == -1
    return data


def knn_outliers(data, uncertainty_col):
    model = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
    data["Outlier"] = model.fit_predict(data[[uncertainty_col]]) == -1
    return data


# Export trimmed datasets based on selected method
def export_trimmed_datasets(selected_method):
    output_dir = os.path.join(
        base_dir,
        "archive",
        "Trimmed",
        selected_method.capitalize(),
    )
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
    print(f"Exporting trimmed datasets using {selected_method} method...")

    for name, df in tqdm(data_dict.items(), desc="Exporting Trimmed Data"):
        uncertainty_col = temp_uncertainty_cols[name]
        trimmed_df = df.copy()

        # Apply the selected method to detect outliers
        if selected_method == "threshold":
            trimmed_df = threshold_filter(trimmed_df, uncertainty_col)
        elif selected_method == "z_score":
            trimmed_df = z_score_outliers(trimmed_df, uncertainty_col)
        elif selected_method == "iqr":
            trimmed_df = iqr_outliers(trimmed_df, uncertainty_col)
        elif selected_method == "isolation_forest":
            trimmed_df = isolation_forest_outliers(trimmed_df, uncertainty_col)
        elif selected_method == "knn":
            trimmed_df = knn_outliers(trimmed_df, uncertainty_col)

        # Keep only non-outliers and drop the 'Outlier' column
        trimmed_df = trimmed_df[trimmed_df["Outlier"] == False].drop(
            columns=["Outlier"],
        )

        # Create the filename with "-(method)-trimmed.csv"
        trimmed_filename = f"{name}-{selected_method}-trimmed.csv"
        trimmed_path = os.path.join(output_dir, trimmed_filename)

        # Export the trimmed data
        trimmed_df.to_csv(trimmed_path, index=False)
    print(
        f"All trimmed datasets have been exported to archive/Trimmed/{selected_method.capitalize()}.",
    )


# Set up Dash app
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.H1(
            "Outlier Detection for Temperature Data",
            style={"text-align": "center"},
        ),
        dcc.Dropdown(
            id="dataset-dropdown",
            options=[{"label": name, "value": name} for name in data_dict],
            value="Global",
            clearable=False,
            style={"width": "50%", "margin": "auto"},
        ),
        dcc.RadioItems(
            id="method-radio",
            options=[
                {"label": "Threshold Filter", "value": "threshold"},
                {"label": "Z-Score", "value": "z_score"},
                {"label": "IQR", "value": "iqr"},
                {"label": "Isolation Forest", "value": "isolation_forest"},
                {"label": "KNN", "value": "knn"},
            ],
            value="threshold",
            labelStyle={"display": "inline-block", "margin-right": "10px"},
        ),
        dcc.Graph(id="outlier-graph"),
        html.H2("Outlier Summary", style={"text-align": "center"}),
        DataTable(
            id="outlier-summary",
            style_cell={"background-color": "#333333", "color": "#ffffff"},
            style_header={"backgroundColor": "#444444", "color": "#ffffff"},
        ),
        # Export section
        html.Div(
            [
                html.Button(
                    "Export Trimmed CSV Files",
                    id="export-trimmed-button",
                    style={"margin": "10px"},
                ),
                html.Button(
                    "Export Table Summaries",
                    id="export-summary-button",
                    style={"margin": "10px"},
                ),
                dcc.Checklist(
                    id="export-all-checkbox",
                    options=[
                        {
                            "label": "Export all summaries for this method",
                            "value": "all",
                        },
                    ],
                    style={"margin-top": "10px", "color": "#ffffff"},
                ),
                html.Div(id="export-confirmation", style={"margin-top": "10px"}),
            ],
            style={"text-align": "center"},
        ),
    ],
)


@app.callback(
    [Output("outlier-graph", "figure"), Output("outlier-summary", "data")],
    [Input("dataset-dropdown", "value"), Input("method-radio", "value")],
)
def update_outliers(dataset_name, method):
    # Use preloaded data for selected dataset
    df = data_dict[dataset_name].copy()
    uncertainty_col = temp_uncertainty_cols[dataset_name]

    # Apply the selected outlier detection method
    if method == "threshold":
        df = threshold_filter(df, uncertainty_col)
    elif method == "z_score":
        df = z_score_outliers(df, uncertainty_col)
    elif method == "iqr":
        df = iqr_outliers(df, uncertainty_col)
    elif method == "isolation_forest":
        df = isolation_forest_outliers(df, uncertainty_col)
    elif method == "knn":
        df = knn_outliers(df, uncertainty_col)

    # Color-code points based on outlier status
    df["Color"] = df["Outlier"].apply(lambda x: "red" if x else "blue")

    # Plot results with color distinction and dark theme
    fig = px.scatter(
        df,
        x="Year",
        y=uncertainty_col,
        color="Color",
        title=f"{method.capitalize()} Outlier Detection",
        color_discrete_map={"red": "red", "blue": "blue"},
    )
    fig.update_traces(marker=dict(size=6))
    fig.update_layout(
        plot_bgcolor="#2d2d2d",
        paper_bgcolor="#2d2d2d",
        font=dict(color="#ffffff"),
        title_font=dict(color="#ffffff"),
    )

    # Update summary table
    outliers = df[df["Outlier"]]
    summary = {
        "Dataset": dataset_name,
        "Method": method.capitalize(),
        "Total Points": len(df),
        "Outliers Detected": len(outliers),
        "Outliers Percentage": round(100 * len(outliers) / len(df), 2),
        "Average Uncertainty (Outliers)": outliers[uncertainty_col].mean(),
    }
    summary_data = [summary]

    return fig, summary_data


@app.callback(
    Output("export-confirmation", "children"),
    [
        Input("export-trimmed-button", "n_clicks"),
        Input("export-summary-button", "n_clicks"),
    ],
    [State("method-radio", "value"), State("export-all-checkbox", "value")],
)
def handle_export_buttons(trimmed_clicks, summary_clicks, selected_method, export_all):
    # Export trimmed CSV files if the "Export Trimmed CSV Files" button was clicked
    if trimmed_clicks:
        export_trimmed_datasets(selected_method)
        return f"Trimmed CSV files have been exported to archive/Trimmed/{selected_method.capitalize()}."

    # Export table summaries if the "Export Table Summaries" button was clicked
    if summary_clicks:
        summary_list = []

        # Export summary data for all datasets if checkbox is selected
        if export_all and "all" in export_all:
            for dataset_name, df in data_dict.items():
                uncertainty_col = temp_uncertainty_cols[dataset_name]
                trimmed_df = df.copy()

                # Apply the selected method to detect outliers
                if selected_method == "threshold":
                    trimmed_df = threshold_filter(trimmed_df, uncertainty_col)
                elif selected_method == "z_score":
                    trimmed_df = z_score_outliers(trimmed_df, uncertainty_col)
                elif selected_method == "iqr":
                    trimmed_df = iqr_outliers(trimmed_df, uncertainty_col)
                elif selected_method == "isolation_forest":
                    trimmed_df = isolation_forest_outliers(trimmed_df, uncertainty_col)
                elif selected_method == "knn":
                    trimmed_df = knn_outliers(trimmed_df, uncertainty_col)

                # Calculate summary statistics
                outliers = trimmed_df[trimmed_df["Outlier"]]
                summary = {
                    "Dataset": dataset_name,
                    "Method": selected_method.capitalize(),
                    "Total Points": len(trimmed_df),
                    "Outliers Detected": len(outliers),
                    "Outliers Percentage": round(
                        100 * len(outliers) / len(trimmed_df),
                        2,
                    ),
                    "Average Uncertainty (Outliers)": outliers[uncertainty_col].mean(),
                }
                summary_list.append(summary)

            # Export all summaries to one CSV
            summary_df = pd.DataFrame(summary_list)
            summary_filename = f"all_datasets_{selected_method}_outlier_summary.csv"
            summary_df.to_csv(summary_filename, index=False)
            return f"All dataset summaries exported as {summary_filename}."

        # Otherwise, only export the summary for the currently selected dataset
        df = data_dict["Global"].copy()
        uncertainty_col = temp_uncertainty_cols["Global"]
        trimmed_df = df.copy()

        # Apply selected method
        if selected_method == "threshold":
            trimmed_df = threshold_filter(trimmed_df, uncertainty_col)
        elif selected_method == "z_score":
            trimmed_df = z_score_outliers(trimmed_df, uncertainty_col)
        elif selected_method == "iqr":
            trimmed_df = iqr_outliers(trimmed_df, uncertainty_col)
        elif selected_method == "isolation_forest":
            trimmed_df = isolation_forest_outliers(trimmed_df, uncertainty_col)
        elif selected_method == "knn":
            trimmed_df = knn_outliers(trimmed_df, uncertainty_col)

        # Summary for current dataset
        outliers = trimmed_df[trimmed_df["Outlier"]]
        summary = {
            "Dataset": "Global",
            "Method": selected_method.capitalize(),
            "Total Points": len(trimmed_df),
            "Outliers Detected": len(outliers),
            "Outliers Percentage": round(100 * len(outliers) / len(trimmed_df), 2),
            "Average Uncertainty (Outliers)": outliers[uncertainty_col].mean(),
        }

        # Export the current dataset summary
        summary_df = pd.DataFrame([summary])
        summary_filename = f"Global_{selected_method}_outlier_summary.csv"
        summary_df.to_csv(summary_filename, index=False)
        return f"Summary for Global dataset exported as {summary_filename}."


# Automatically open the web browser when the app runs
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")


if __name__ == "__main__":
    open_browser()
    app.run_server(debug=False)  # Set debug=False to prevent auto-reloading
