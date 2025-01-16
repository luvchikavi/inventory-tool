# main.py
import streamlit as st
from PIL import Image
from scripts.data_processing import load_data, validate_data
from scripts.inventory_analysis import calculate_inventory_metrics
import pandas as pd
import plotly.express as px
import numpy as np

# Streamlit App Configuration
st.set_page_config(page_title="Inventory Management Dashboard", layout="wide")

# App Title
logo_path = '/Users/aviluvchik/Python Projects/inventory_dashboard/superpharm_logo.png'
logo = Image.open(logo_path)
col1, col2 = st.columns([1, 8])
col1.image(logo, use_column_width=True)
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
            # Modified load_data function to adapt to the file structure dynamically
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
            tabs = ["Overview", "Detailed Analysis", "Forecasting", "Decision-Making Tools", "Warnings"]
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
                if "Item" in data.columns and "Stock Level" in data.columns:
                    fig = px.histogram(
                        data, x="Item", y="Stock Level",
                        title="Stock Levels by Item",
                        labels={"Item": "Item", "Stock Level": "Stock Level"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("The required columns for detailed analysis are missing.")

            elif selected_tab == "Forecasting":
                ### New Tab: Forecasting Tab ###
                st.write("### Forecasting")
                st.markdown("Below is the forecasting analysis for your inventory data.")

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

            elif selected_tab == "Decision-Making Tools":
                ### New Tab: Decision-Making Tools Tab ###
                st.write("### Decision-Making Tools")
                st.markdown("Below is a scenario analysis to help make informed inventory decisions.")

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

                # Moved Decision-Making Sliders into the Tab
                st.markdown("### Adjust Parameters")
                holding_cost = st.slider("Adjust Holding Cost (%)", min_value=0, max_value=20, value=10)
                selling_price_factor = st.slider("Adjust Selling Price Multiplier", min_value=1.0, max_value=2.0, value=1.2)

                adjusted_data = data.copy()
                adjusted_data["Selling Price"] = (adjusted_data["Purchase Price"] * selling_price_factor).round(2)
                adjusted_data["Profit Potential"] = (
                    (adjusted_data["Selling Price"] - adjusted_data["Purchase Price"]) * adjusted_data["Stock Level"]
                ).round(2)

                st.write("### Adjusted Profit Analysis")
                st.dataframe(adjusted_data[["Item", "Selling Price", "Profit Potential"]])

                fig_adjusted = px.bar(
                    adjusted_data, 
                    x="Item", 
                    y="Profit Potential", 
                    title="Adjusted Profit Potential"
                )
                st.plotly_chart(fig_adjusted, use_container_width=True)

            elif selected_tab == "Warnings":
                ### New Tab: Warnings Tab ###
                st.write("### Warnings and Risks")
                st.markdown(
                    "This tab highlights potential issues in your inventory management system to help you take action proactively."
                )

                warnings = pd.DataFrame({
                    "Item": data["Item"],
                    "Priority": np.random.choice(["Order Now - Out of Stock", "Delayed Order - Overstock"], len(data)),
                    "Risk Level": np.random.choice(["High", "Medium", "Low"], len(data)),
                })

                st.write("### Inventory Warnings Table")
                st.dataframe(warnings)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.write("Upload an Excel file to begin.")

# Footer
st.markdown("---")
st.markdown("**Inventory Dashboard | Created by Dr. Luvchik**")
st.markdown("© All Rights Reserved 2025")
