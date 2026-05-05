
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Inventory Dashboard", layout="wide")
st.title("📦 Inventory Dashboard")
st.markdown("---")

@st.cache_data
def load_data():
    inv    = pd.read_csv("data/inventory_optimization.csv")
    reorder= pd.read_csv("data/reorder_recommendations.csv")
    return inv, reorder

inv, reorder = load_data()

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Products Analyzed", f"{len(inv):,}")
col2.metric("Critical (A) Items", f"{(inv['ABC_Category']=='A — Critical').sum():,}")
col3.metric("High Risk Items",
            f"{(inv['Stock_Risk']=='🔴 HIGH RISK').sum():,}")
col4.metric("Total Reorder Value",
            f"£{(inv['EOQ'] * inv['Avg_UnitPrice']).sum():,.0f}")

st.markdown("---")

col_left, col_right = st.columns(2)

# ABC pie chart
with col_left:
    abc = inv["ABC_Category"].value_counts().reset_index()
    abc.columns = ["Category", "Count"]
    fig1 = px.pie(abc, names="Category", values="Count",
                  title="ABC Category Distribution",
                  color_discrete_sequence=["#e74c3c","#f39c12","#2ecc71"])
    st.plotly_chart(fig1, use_container_width=True)

# Risk breakdown
with col_right:
    risk = inv["Stock_Risk"].value_counts().reset_index()
    risk.columns = ["Risk", "Count"]
    fig2 = px.bar(risk, x="Risk", y="Count",
                  title="Stock Risk Distribution",
                  color="Risk",
                  color_discrete_map={
                      "🔴 HIGH RISK": "#e74c3c",
                      "🟡 MEDIUM RISK": "#f39c12",
                      "🟢 LOW RISK": "#2ecc71"})
    st.plotly_chart(fig2, use_container_width=True)

# EOQ scatter
fig3 = px.scatter(inv, x="Avg_Daily_Demand", y="EOQ",
                  size="Total_Revenue", color="ABC_Category",
                  hover_data=["Description","Reorder_Point","Safety_Stock"],
                  title="Daily Demand vs Optimal Order Quantity",
                  labels={"Avg_Daily_Demand": "Avg Daily Demand (units)",
                          "EOQ": "Economic Order Quantity"},
                  color_discrete_map={
                      "A — Critical": "#e74c3c",
                      "B — Important": "#f39c12",
                      "C — Monitor": "#2ecc71"})
st.plotly_chart(fig3, use_container_width=True)

# Reorder table
st.subheader("📋 Reorder Recommendations")
abc_filter = st.selectbox("Filter by Category",
                           ["All","A — Critical","B — Important","C — Monitor"])
risk_filter = st.selectbox("Filter by Risk",
                            ["All","🔴 HIGH RISK","🟡 MEDIUM RISK","🟢 LOW RISK"])

display = reorder.copy()
if abc_filter  != "All": display = display[display["ABC_Category"] == abc_filter]
if risk_filter != "All": display = display[display["Stock_Risk"]   == risk_filter]

st.dataframe(display[[
    "Description","ABC_Category","Stock_Risk",
    "Avg_Daily_Demand","Safety_Stock","Reorder_Point","EOQ","Est_Order_Cost"
]].head(50), use_container_width=True, height=400)
