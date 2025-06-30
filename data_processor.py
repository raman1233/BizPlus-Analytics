import pandas as pd

REQUIRED_COLUMNS = {"Order Date", "Product", "Customer ID", "Quantity", "Unit Price"}

def process_data(df: pd.DataFrame):
    # Check for required columns
    if not REQUIRED_COLUMNS.issubset(set(df.columns)):
        return False

    # Convert Order Date to datetime
    df["Order Date"] = pd.to_datetime(df["Order Date"])

    # Create a new column: Total Revenue
    df["Total Revenue"] = df["Quantity"] * df["Unit Price"]

    return True

