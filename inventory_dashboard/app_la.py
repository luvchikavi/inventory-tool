# File: app_la.py

import streamlit as st
from utils.file_management import save_uploaded_file
from utils.data_processing import load_and_process_data
from utils.calculations import calculate_reorder_point_and_eoq
from utils.config import UPLOAD_DIR, CLIENT_LOGO
import pandas as pd
import plotly.express as px

# Streamlit App Configuration
st.set_page_config(page_title="Inventory Management Dashboard", layout="wide")

# --- Persistent Data ---
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

# --- Authentication ---
st.sidebar.title("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if login_button:
    # Dummy users
    users = {"johndoe": "password123", "janedoe": "secret456"}
    if username in users and password == users[username]:
        st.session_state.authenticated = True
        st.sidebar.success(f"Welcome {username}!")
    else:
        st.sidebar.error("Invalid username or password.")

if not st.session_state.authenticated:
    st.stop()

# --- App Title ---
CLIENT_LOGO = "/Users/aviluvchik/Python Projects/inventory_dashboard/uploaded_files/superpharm_logo.png"
try:
    st.image(CLIENT_LOGO, use_column_width=False, width=150)
except Exception:
    st.warning("Client logo not found or inaccessible.")
# --- File Upload ---
st.sidebar.header("Upload Inventory Data")
uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Save and process the uploaded file
    file_path = save_uploaded_file(uploaded_file, UPLOAD_DIR)
    st.sidebar.success(f"File uploaded and saved as {uploaded_file.name}")
    st.session_state.uploaded_data = load_and_process_data(file_path)

# Ensure data is loaded from session state
if st.session_state.uploaded_data is not None:
    data = st.session_state.uploaded_data
else:
    st.write("No data uploaded yet. Please upload a file.")
    st.stop()

# --- Calculate Reorder Point and EOQ ---
try:
    data = calculate_reorder_point_and_eoq(data)
    data["Forecasted Demand"] = data["Stock Level"] * 1.1  # Forecast demand with a simple multiplier
except Exception as e:
    st.error(f"Error calculating Reorder Point and EOQ: {e}")
    st.stop()

# --- Navigation Tabs ---
st.sidebar.header("Navigation")
tabs = ["Overview", "Inventory Insights", "Inventory Tracker", "Financial Analysis (Premium)"]
selected_tab = st.sidebar.radio("Go to", tabs)

# --- Overview Tab ---
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

# --- Inventory Insights Tab (Merged Forecasting and Detailed Analysis) ---
elif selected_tab == "Inventory Insights":
    st.write("### Inventory Insights")
    # Display combined table
    st.dataframe(data[["Item", "Stock Level", "Reorder Point", "EOQ", "Forecasted Demand"]])

# --- Inventory Tracker Tab ---
elif selected_tab == "Inventory Tracker":
    st.write("### Inventory Tracker")

    # Low Stock
    low_stock = data[data["Stock Level"] < data["Reorder Point"]]
    st.write("#### Low Stock Warnings (High Priority)")
    st.dataframe(
        low_stock.style.applymap(lambda _: "background-color: red;", subset=["Stock Level"])
    )

    # Overstock
    overstock = data[data["Stock Level"] > data["Reorder Point"] * 2]
    st.write("#### Overstock Warnings (Medium Priority)")
    st.dataframe(
        overstock.style.applymap(lambda _: "background-color: orange;", subset=["Stock Level"])
    )

    # Normal Stock
    normal_stock = data[
        (data["Stock Level"] >= data["Reorder Point"]) & (data["Stock Level"] <= data["Reorder Point"] * 2)
    ]
    st.write("#### Normal Stock Levels (Low Priority)")
    st.dataframe(
        normal_stock.style.applymap(lambda _: "background-color: green;", subset=["Stock Level"])
    )

# --- Financial Analysis Tab ---
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

# --- Footer ---
st.markdown("---")
st.markdown("**Powered by SG Consulting | Created by Drishti.com Consulting**")
st.markdown("© All Rights Reserved 2025")
