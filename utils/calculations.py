# File: utils/calculations.py

import numpy as np

def calculate_reorder_point_and_eoq(data, safety_factor=1.65, ordering_cost=100, holding_cost=10):
    """Calculate reorder point and EOQ for inventory data."""
    try:
        data["Stock Level"] = data["Stock Level"].fillna(0).clip(lower=0)
        data["Lead Time"] = data["Lead Time"].fillna(7).clip(lower=0)

        # Calculations
        data["Average Daily Demand"] = data["Stock Level"] / 30
        data["Lead Time Demand"] = data["Average Daily Demand"] * data["Lead Time"]
        data["Safety Stock"] = safety_factor * np.sqrt(data["Lead Time"]) * data["Average Daily Demand"]
        data["Reorder Point"] = data["Lead Time Demand"] + data["Safety Stock"]
        data["EOQ"] = np.sqrt((2 * data["Average Daily Demand"] * ordering_cost) / holding_cost)

        return data
    except Exception as e:
        raise ValueError(f"Error calculating Reorder Point and EOQ: {e}")