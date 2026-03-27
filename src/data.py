"""Data loading, cleaning, and transformation pipeline."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from .config import COUNTRY_CSV, STATE_CSV, US_STATE_CODES


def load_state_data() -> pd.DataFrame:
    """Load and preprocess US state temperature data."""
    df = pd.read_csv(STATE_CSV)
    df = df.dropna()
    df["State"] = df["State"].replace("Georgia (State)", "Georgia")

    us_data = df[df["Country"] == "United States"].copy()
    us_data["State_Code"] = us_data["State"].map(US_STATE_CODES)
    us_data["Year"] = pd.to_datetime(us_data["Year"], format="%Y")
    return us_data


def load_country_data() -> pd.DataFrame:
    """Load and preprocess country-level temperature data."""
    df = pd.read_csv(COUNTRY_CSV)
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df = df.dropna()
    return df.groupby(["Year", "Country"])["AverageTemperature"].mean().reset_index()


def compute_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Compute average temperatures and change-from-start per year."""
    trend = df.groupby("Year")["AverageTemperature"].mean().reset_index()
    trend["TempChange"] = trend["AverageTemperature"] - trend["AverageTemperature"].iloc[0]
    return trend


def predict_temperatures(
    dates: pd.Series,
    temperatures: pd.Series,
    current_year: int,
    predict_years: int = 10,
) -> tuple[list, np.ndarray]:
    """Fit linear regression and project temperatures forward."""
    X = np.array([(d.year + d.dayofyear / 365) for d in dates]).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, temperatures)

    future_years = np.arange(
        min(dates).year, current_year + predict_years + 1, 1
    ).reshape(-1, 1)
    y_pred = model.predict(future_years)

    prediction_dates = [
        pd.Timestamp(year=int(y), month=1, day=1) for y in future_years.flatten()
    ]
    return prediction_dates, y_pred
