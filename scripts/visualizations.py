import plotly.express as px

def create_overview_charts(data):
    """Generate overview charts for inventory metrics."""
    fig1 = px.bar(data, x="Category", y="Stock Level", title="Stock Levels by Category")
    fig2 = px.pie(data, values="Stock Level", names="Category", title="Stock Distribution by Category")
    return [fig1, fig2]

def create_inventory_analysis(data):
    """Generate detailed inventory analysis charts."""
    fig1 = px.bar(data, x="Item", y="Overstock", title="Overstock Analysis")
    fig2 = px.bar(data, x="Item", y="Understock", title="Understock Analysis")
    return [fig1, fig2]
