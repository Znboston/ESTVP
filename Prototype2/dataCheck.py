import pandas as pd

# Load the CSV file
file_path = (
    "archive/Trimmed/Threshold/State-threshold-trimmed.csv"  # Update the path if needed
)
df = pd.read_csv(file_path)

# Display the first few rows and column names to verify structure
print("First few rows of the data:")
print(df.head())
print("\nColumn names and data types:")
print(df.dtypes)

# Convert 'dt' to datetime format and extract the year
df["dt"] = pd.to_datetime(
    df["dt"],
    errors="coerce",
)  # Use 'coerce' to handle invalid dates as NaT
df["year"] = df["dt"].dt.year

# Check for NaN values in 'year' column
nan_years = df["year"].isna().sum()
print(f"\nNumber of NaN values in 'year' column: {nan_years}")

# Drop rows where 'year' is NaN, if any
if nan_years > 0:
    df = df.dropna(subset=["year"])
    print(f"Dropped {nan_years} rows with NaN values in 'year' column.")

# Ensure 'year' column is integer type
df["year"] = df["year"].astype(int)
print("\nData types after processing:")
print(df.dtypes)

# Check if everything looks good
print("\nFirst few rows after processing:")
print(df.head())
