# File: app_la.py

import streamlit as st
from utils.file_management import save_uploaded_file
from utils.data_processing import load_and_process_data
from utils.calculations import calculate_reorder_point_and_eoq
from utils.config import UPLOAD_DIR, CLIENT_LOGO
from fpdf import FPDF  # Fix: Import PDF library
import os
import pandas as pd
import plotly.express as px
# Simple Authentication Logic
import bcrypt

# Predefined users
users = {
    "johndoe": bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
    "janedoe": bcrypt.hashpw("secret456".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
}

# Authentication Form
st.sidebar.title("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if login_button:
    if username in users and bcrypt.checkpw(password.encode("utf-8"), users[username].encode("utf-8")):
        st.session_state.authenticated = True
        st.sidebar.success(f"Welcome {username}!")
    else:
        st.sidebar.error("Invalid username or password.")

if not st.session_state.authenticated:
    st.stop()

# --- App Title ---
st.image(CLIENT_LOGO, use_column_width=False, width=150)
st.title("Inventory Management Dashboard")

# File Upload Section
st.sidebar.header("Upload Inventory Data")
uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=["xlsx"])

if not uploaded_file:
    st.title("Welcome to the Inventory Management Dashboard!")
    st.write("Please upload an Excel file using the sidebar to get started.")
    st.stop()

# Save the uploaded file
file_path = save_uploaded_file(uploaded_file, UPLOAD_DIR)
st.sidebar.success(f"File uploaded and saved as {uploaded_file.name}")

# Load and process the data
try:
    data = load_and_process_data(file_path)
    data.columns = data.columns.map(str)  # Fix column name warnings
    st.write("File successfully processed!")
    st.dataframe(data.head())
except Exception as e:
    st.error(f"Error processing file: {e}")
    st.stop()

# Calculate Reorder Point and EOQ (Global)
try:
    data = calculate_reorder_point_and_eoq(data)
except Exception as e:
    st.error(f"Error calculating Reorder Point and EOQ: {e}")
    st.stop()

# Navigator Dashboard
st.sidebar.header("Navigation")
tabs = ["Overview", "Detailed Analysis", "Forecasting", "Warnings", "Pareto Analysis", "Financial Analysis (Premium)"]
selected_tab = st.sidebar.radio("Go to", tabs)

if selected_tab == "Overview":
    st.write("### Inventory Overview")
    st.write("#### Key Metrics")
    st.metric("Total Stock", int(data["Stock Level"].sum()))
    st.metric("Total Categories", int(data["Category"].nunique()))
    st.metric("Total Reorder Points", int(data["Reorder Point"].count()))

    # Bar Chart
    fig_bar = px.bar(data, x="Category", y="Stock Level", title="Stock Levels by Category")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Pie Chart
    fig_pie = px.pie(data, values="Stock Level", names="Category", title="Stock Distribution by Category")
    st.plotly_chart(fig_pie, use_container_width=True)

elif selected_tab == "Detailed Analysis":
    st.write("### Detailed Inventory Analysis")
    st.dataframe(data[["Item", "Reorder Point", "EOQ"]])

elif selected_tab == "Forecasting":
    st.write("### Forecasting")
    data["Forecasted Demand"] = data["Stock Level"] * 1.1
    st.dataframe(data[["Item", "Stock Level", "Forecasted Demand"]])

elif selected_tab == "Warnings":
    st.write("### Warnings and Risks")

    # Low Stock Warnings
    low_stock = data[data["Stock Level"] < data["Reorder Point"]]
    st.write("#### Low Stock Warnings")
    st.dataframe(low_stock.style.applymap(lambda v: "color: red;" if v else "", subset=["Stock Level"]))

    # Overstock Warnings
    overstock = data[data["Stock Level"] > data["Reorder Point"] * 2]
    st.write("#### Overstock Warnings")
    st.dataframe(overstock.style.applymap(lambda v: "color: orange;" if v else "", subset=["Stock Level"]))

elif selected_tab == "Pareto Analysis":
    st.write("### Pareto Analysis (ABC Classification)")
    data["Total Value"] = data["Stock Level"] * data["Purchase Price"]
    data.sort_values("Total Value", ascending=False, inplace=True)
    data["Cumulative Percentage"] = (
        data["Total Value"].cumsum() / data["Total Value"].sum() * 100
    )
    data["ABC Classification"] = pd.cut(
        data["Cumulative Percentage"], bins=[0, 80, 95, 100], labels=["A", "B", "C"]
    )
    st.dataframe(data[["Item", "Total Value", "Cumulative Percentage", "ABC Classification"]])

elif selected_tab == "Financial Analysis (Premium)":
    st.write("### Financial Analysis")
    st.write("#### Profit Optimization Tool")

    # User Inputs
    price_adjustment = st.slider("Adjust Selling Price (%)", 80, 150, 100)
    demand_growth = st.slider("Expected Demand Growth (%)", -20, 50, 10)
    cost_reduction = st.slider("Cost Reduction (%)", 0, 20, 0)

    # Simulate Adjustments
    adjusted_data = data.copy()
    adjusted_data["Adjusted Selling Price"] = adjusted_data["Selling Price"] * (price_adjustment / 100)
    adjusted_data["Adjusted Demand"] = adjusted_data["Stock Level"] * (1 + demand_growth / 100)
    adjusted_data["Adjusted Cost"] = adjusted_data["Purchase Price"] * (1 - cost_reduction / 100)
    adjusted_data["Profit"] = (adjusted_data["Adjusted Selling Price"] - adjusted_data["Adjusted Cost"]) * adjusted_data["Adjusted Demand"]

    # Display Results
    st.write("### Simulation Results")
    st.dataframe(adjusted_data[["Item", "Adjusted Selling Price", "Adjusted Demand", "Adjusted Cost", "Profit"]])

    # Profit Visualization
    fig_simulation = px.bar(adjusted_data, x="Item", y="Profit", title="Profit by Item (After Simulation)")
    st.plotly_chart(fig_simulation, use_container_width=True)

    # Export to Excel
    st.download_button(
        label="Download Excel Report",
        data=adjusted_data.to_csv(index=False).encode("utf-8"),
        file_name="financial_analysis.csv",
        mime="text/csv",
    )

    # Export to PDF
    from fpdf import FPDF

    def generate_pdf(dataframe):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Financial Analysis Report", ln=True, align="C")
        for index, row in dataframe.iterrows():
            # Sanitize data to prevent encoding errors
            sanitized_row = {k: str(v).encode("latin1", "replace").decode("latin1") for k, v in row.to_dict().items()}
            pdf.cell(200, 10, txt=str(sanitized_row), ln=True, align="L")
        return pdf.output(dest="S").encode("latin1")

    st.download_button(
        label="Download PDF Report",
        data=generate_pdf(adjusted_data),
        file_name="financial_analysis.pdf",
        mime="application/pdf",
    )
# Footer
st.markdown("---")
st.markdown("**Powered by SG Consulting | Created by Drishti.com Consulting**")
st.markdown("© All Rights Reserved 2025")