# File: utils/data_processing.py

import pandas as pd

def load_and_process_data(file_path):
    """Load and process the uploaded Excel file."""
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.map(str)  # Ensure all column names are strings
        column_mappings = {
            "משפחה": "Category",
            "תאור פריט": "Item",
            "מלאי נוכחי": "Stock Level",
            "עלות פריט": "Purchase Price",
            "מחיר מכירה": "Selling Price",
            "זמן אספקה בימים": "Lead Time",
        }
        df.rename(columns=column_mappings, inplace=True)
        return df
    except Exception as e:
        raise ValueError(f"Error loading and processing data: {e}")