import pandas as pd

# Load city-level temperature data
data_path = "data/temperature_data_city.csv"
df = pd.read_csv(data_path)

# Aggregate temperature data by state and year (or just by state)
state_data = df.groupby(["year", "state"])["averagetemperature"].mean().reset_index()

# Filter data for a specific year (e.g., 2012) for the visualization
state_data_2012 = state_data[state_data["year"] == 2012]

# Save the data for the chosen year
state_data_2012.to_csv("data/state_temperature_2012.csv", index=False)
