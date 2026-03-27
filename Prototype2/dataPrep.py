import json
import os

import pandas as pd

# Define the path to the city-level trimmed CSV file
file_path = "archive/Trimmed/Threshold/City-threshold-trimmed.csv"
output_dir = "data"
output_path = os.path.join(output_dir, "temperature_data_city.json")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load the CSV file and check the structure
df = pd.read_csv(file_path)

# Display the initial structure of the data for verification
print("Initial structure of the data:")
print(df.head())
print("\nData types:")
print(df.dtypes)

# Normalize column names for consistency
df.columns = df.columns.str.strip().str.lower()

# Define the columns to keep based on the city-level data with latitude and longitude
columns = [
    "year",
    "city",
    "country",
    "latitude",
    "longitude",
    "averagetemperature",
    "averagetemperatureuncertainty",
]

# Filter the DataFrame to include only the selected columns
df = df[columns]

# Group data by year and convert to JSON format
data = {}
for year, group in df.groupby("year"):
    data[year] = group.to_dict(orient="records")

# Save the processed data as JSON
with open(output_path, "w") as f:
    json.dump(data, f)

print(f"City-level data saved to {output_path}")
