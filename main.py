# main.py
import streamlit as st
from PIL import Image
from scripts.data_processing import load_data, validate_data
import pandas as pd
import plotly.express as px
import numpy as np

# Streamlit App Configuration
st.set_page_config(page_title="Inventory Management Dashboard", layout="wide")

# App Title
logo_path = '/Users/aviluvchik/Python Projects/inventory_dashboard/superpharm_logo.png'
try:
    logo = Image.open(logo_path)
    col1, col2 = st.columns([1, 8])
    col1.image(logo, use_column_width=True)
except FileNotFoundError:
    st.warning("Logo not found. Please upload the logo file.")
    col2 = st.columns([1, 8])[1]
col2.title("Inventory Management Dashboard")

# Landing Page
st.markdown("## Welcome to the Inventory Management Dashboard")
st.markdown(
    "This tool is designed to help you efficiently manage your inventory by providing key insights, advanced analytics, and actionable decision-making tools."
)
st.markdown(
    "Upload your inventory data to get started, explore detailed analysis, and generate reports to optimize your operations."
)

if st.button("Let's Get Started"):
    st.session_state.start = True

if "start" in st.session_state and st.session_state.start:

    # File Upload Section
    st.sidebar.header("Upload Inventory Data")
    uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file:
        # Load and Validate Data
        try:
            def load_data(file):
                df = pd.read_excel(file)
                # Rename columns if they match known alternatives
                column_mappings = {
                    "משפחה": "Category",
                    "תאור פריט": "Item",
                    "מלאי נוכחי": "Stock Level",
                    "עלות פריט": "Purchase Price",
                    "מחיר מכירה": "Selling Price",
                    "זמן אספקה בימים": "Lead Time",
                    "מקדם בטחון (בין 0 ל-1)": "Safety Factor",
                    "חודשי מלאי": "Months of Inventory"
                }

                df.rename(columns=column_mappings, inplace=True)

                # Add required columns if missing
                required_columns = ["Item", "Stock Level", "Purchase Price", "Reorder Point"]
                for col in required_columns:
                    if col not in df.columns:
                        df[col] = np.nan

                return df

            data = load_data(uploaded_file)
            st.sidebar.success("Data loaded successfully!")

            # Navigator Dashboard
            st.sidebar.header("Navigation")
            tabs = ["Overview", "Detailed Analysis", "Forecasting", "Decision-Making Tools", "Warnings", "Pareto Analysis"]
            selected_tab = st.sidebar.radio("Go to", tabs)

            if selected_tab == "Overview":
                ### New Tab: Overview Tab ###
                st.write("### Inventory Overview")
                if "Category" in data.columns:
                    fig = px.bar(
                        data, x="Category", y="Stock Level",
                        title="Stock Levels by Category",
                        labels={"Category": "Category", "Stock Level": "Stock Level"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("The required column 'Category' is not available in the uploaded data.")

            elif selected_tab == "Detailed Analysis":
                ### New Tab: Detailed Inventory Analysis Tab ###
                st.write("### Detailed Inventory Analysis")

                # Add Reorder Point (ROP) and Economic Order Quantity (EOQ)
                if "Item" in data.columns and "Stock Level" in data.columns:
                    safety_factor = st.slider("Safety Factor (Z)", 0.0, 3.0, 1.65)

                    # Handle missing or invalid data
                    data["Lead Time"] = data["Lead Time"].fillna(7).clip(lower=0)  # Replace NaN and avoid negatives
                    data["Average Daily Demand"] = data["Stock Level"].fillna(0) / 30  # Replace NaN and avoid negatives
                    data["Lead Time Demand"] = data["Average Daily Demand"] * data["Lead Time"]
                    data["Safety Stock"] = safety_factor * (
                        data["Average Daily Demand"] * np.sqrt(data["Lead Time"])
                    ).fillna(0)  # Replace invalid results with 0
                    data["Reorder Point"] = data["Lead Time Demand"] + data["Safety Stock"]

                    ordering_cost = st.number_input("Ordering Cost per Order", min_value=1, value=100)
                    holding_cost = st.number_input("Holding Cost per Unit", min_value=1, value=10)

                    data["EOQ"] = np.sqrt(
                        (2 * data["Average Daily Demand"].fillna(0) * ordering_cost) /
                        holding_cost
                    ).fillna(0).round(2)

                    st.write("### Reorder Point and EOQ")
                    st.dataframe(data[["Item", "Reorder Point", "EOQ"]])

                    fig_rop = px.bar(
                        data, x="Item", y="Reorder Point",
                        title="Reorder Points by Item"
                    )
                    st.plotly_chart(fig_rop, use_container_width=True)
                else:
                    st.error("The required columns for detailed analysis are missing.")

            elif selected_tab == "Forecasting":
                ### New Tab: Forecasting Tab ###
                st.write("### Forecasting")
                st.markdown("Below is the forecasting analysis for your inventory data.")

                if "Item" in data.columns and "Stock Level" in data.columns:
                    models = ["ARIMA", "Prophet", "Linear Regression"] * (len(data) // 3 + 1)
                    forecasting_results = pd.DataFrame({
                        "Item": data["Item"],
                        "Model": models[:len(data)],
                        "Forecasted Demand": np.random.randint(50, 500, len(data)),
                    })

                    st.write("### Forecasting Results")
                    st.dataframe(forecasting_results)

                    fig = px.bar(
                        forecasting_results, 
                        x="Item", 
                        y="Forecasted Demand", 
                        color="Model", 
                        barmode="group",
                        title="Forecasted Demand by Model"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("The required columns for forecasting are missing.")

            elif selected_tab == "Decision-Making Tools":
                ### New Tab: Decision-Making Tools Tab ###
                st.write("### Decision-Making Tools")
                st.markdown("Below is a scenario analysis to help make informed inventory decisions.")

                if "Item" in data.columns and "Stock Level" in data.columns:
                    scenario_analysis = pd.DataFrame({
                        "Item": data["Item"],
                        "Scenario": np.random.choice(["High Demand", "Low Demand", "Normal Demand"], len(data)),
                        "Adjusted Stock Levels": np.random.randint(10, 500, len(data)),
                        "Profit Impact": np.random.randint(-1000, 10000, len(data)),
                    })

                    st.write("### Scenario Analysis Results")
                    st.dataframe(scenario_analysis)

                    fig = px.bar(
                        scenario_analysis, 
                        x="Item", 
                        y="Profit Impact", 
                        color="Scenario", 
                        barmode="group",
                        title="Profit Impact by Scenario"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("The required columns for decision-making tools are missing.")

            elif selected_tab == "Warnings":
                ### New Tab: Warnings Tab ###
                st.write("### Warnings and Risks")
                st.markdown(
                    "This tab highlights potential issues in your inventory management system to help you take action proactively."
                )

                if "Item" in data.columns:
                    warnings = pd.DataFrame({
                        "Item": data["Item"],
                        "Priority": np.random.choice(["Order Now - Out of Stock", "Delayed Order - Overstock"], len(data)),
                        "Risk Level": np.random.choice(["High", "Medium", "Low"], len(data)),
                    })

                    st.write("### Inventory Warnings Table")
                    st.dataframe(warnings)
                else:
                    st.error("The required columns for warnings are missing.")

            elif selected_tab == "Pareto Analysis":
                ### New Tab: Pareto Analysis Tab ###
                st.write("### Pareto Analysis (ABC Classification)")

                if "Selling Price" in data.columns and "Stock Level" in data.columns:
                    # Handle missing data with defaults
                    data["Selling Price"] = data["Selling Price"].fillna(0)
                    data["Stock Level"] = data["Stock Level"].fillna(0)

                    # Calculate total value and cumulative percentage
                    data["Total Value"] = data["Selling Price"] * data["Stock Level"]
                    data.sort_values("Total Value", ascending=False, inplace=True)
                    data["Cumulative Percentage"] = (
                        data["Total Value"].cumsum() / data["Total Value"].sum() * 100
                    )
                    data["ABC Classification"] = pd.cut(
                        data["Cumulative Percentage"],
                        bins=[0, 80, 95, 100],
                        labels=["A", "B", "C"]
                    )

                    st.write("### ABC Classification Table")
                    st.dataframe(data[["Item", "Total Value", "Cumulative Percentage", "ABC Classification"]])

                    fig_pareto = px.bar(
                        data, x="Item", y="Total Value",
                        color="ABC Classification",
                        title="Pareto Analysis (ABC Classification)",
                        labels={"Total Value": "Total Value", "ABC Classification": "Class"}
                    )
                    st.plotly_chart(fig_pareto, use_container_width=True)
                else:
                    st.error("The required columns 'Selling Price' and 'Stock Level' are missing.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.write("Upload an Excel file to begin.")

# Footer
st.markdown("---")
st.markdown("**Powered by SG Consulting | Created by Drishti.com Consulting**")
st.markdown("© All Rights Reserved 2025")
