import pandas as pd

def calculate_inventory_metrics(data):
    """Calculate key metrics for inventory management."""
    data["Overstock"] = data["Stock Level"] - data["Reorder Point"]
    data["Understock"] = data["Reorder Point"] - data["Stock Level"]
    return data
