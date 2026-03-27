"""Dashboard configuration: paths, constants, and theme settings."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dataset paths (trimmed threshold data used by the dashboard)
DATA_DIR = os.path.join(BASE_DIR, "archive", "Trimmed", "Threshold")
STATE_CSV = os.path.join(DATA_DIR, "State-threshold-trimmed.csv")
COUNTRY_CSV = os.path.join(DATA_DIR, "Country-threshold-trimmed.csv")

# Prediction settings
PREDICTION_YEARS = 10

# Animation settings
FRAME_DURATION_MS = 500
TRANSITION_DURATION_MS = 300

# Dark theme colors
THEME = {
    "bg": "#2d2d2d",
    "surface": "#1f1f1f",
    "border": "#555555",
    "button": "#404040",
    "button_hover": "#606060",
    "text": "#ffffff",
    "grid": "#404040",
    "land": "#444444",
}

# US state name to FIPS code mapping
US_STATE_CODES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}
