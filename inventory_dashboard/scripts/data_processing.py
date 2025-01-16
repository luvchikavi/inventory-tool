import pandas as pd

def load_data(file):
    """Load Excel file and return a DataFrame."""
    return pd.read_excel(file)

def validate_data(data):
    """Validate data to ensure required columns are present."""
    required_columns = ["Item", "Category", "Stock Level", "Reorder Point", "Lead Time"]
    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"Missing required column: {col}")
    return True
