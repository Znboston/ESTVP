# ESTVP — Earth Surface Temperature Visualization Project

Interactive temperature analysis dashboard built for CSC 422 (Automated Learning & Data Analysis) at NC State University, Fall 2024.

## Overview

ESTVP processes decades of historical meteorological data and presents it through an animated, interactive dashboard. Users can explore temperature trends at both US state and global country levels, with linear regression predictions projected 10 years forward.

## Features

- **Animated Choropleth Maps** — US state-level and global country-level temperature heatmaps with year-by-year animation
- **Dynamic Predictions** — Linear regression model generates 10-year forward projections that update as the timeline progresses
- **Interactive Controls** — Play/pause animation, year slider, view switching (US/Global), and togglable prediction overlay
- **Data Pipeline** — Preprocessing with Pandas and NumPy including cleaning, outlier detection (Z-score, IQR, Isolation Forest, KNN), and threshold-based trimming

## Tech Stack

- **Python** — Pandas, NumPy, scikit-learn, Plotly, Dash, SciPy
- **Visualization** — Plotly choropleth maps, subplots, animated frames
- **ML** — scikit-learn LinearRegression for trend prediction; Isolation Forest and Local Outlier Factor for data cleaning

## Project Structure

```
├── Combined.py              # Final consolidated dashboard
├── FinalPrototype/          # Dash-based interactive prototype
│   ├── app.py               # Prototype v1
│   └── app2.py              # Prototype v2
├── dataHandler.py           # Data preprocessing and outlier detection pipeline
├── dataPrep.py              # Dataset preparation utilities
├── Noise.py                 # Noise analysis and visualization
├── archive/                 # Temperature datasets (raw + trimmed variants)
│   ├── Trimmed/             # Cleaned datasets by method (Threshold, Z-score, IQR, etc.)
│   └── Raw/                 # Original source CSVs (not included — see Data below)
├── assets/                  # CSS stylesheets
└── Documents/               # Project proposal and midterm report
```

## Data

This project uses the [Climate Change: Earth Surface Temperature Data](https://www.kaggle.com/datasets/berkeleyearth/climate-change-earth-surface-temperature-data) dataset from Kaggle. Raw CSV files are not included in this repository due to size (~600MB). The trimmed/processed datasets used by the dashboard are included.

## Usage

```bash
pip install pandas numpy plotly scikit-learn scipy dash tqdm
python Combined.py
```

The dashboard will be generated as an HTML file and opened in your default browser.
