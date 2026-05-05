
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Customer Dashboard", layout="wide")
st.title("👥 Customer Dashboard")
st.markdown("---")

@st.cache_data
def load_data():
    rfm   = pd.read_csv("data/rfm_segments.csv")
    churn = pd.read_csv("data/churn_predictions.csv")
    return rfm, churn

rfm, churn = load_data()

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers",   f"{len(rfm):,}")
col2.metric("Champions",         f"{(rfm['Segment']=='Champions').sum():,}")
col3.metric("At-Risk Customers",
            f"{churn['Churn_Risk'].isin(['High','Critical']).sum():,}")
col4.metric("Lost Customers",    f"{(rfm['Segment']=='Lost').sum():,}")

st.markdown("---")

col_left, col_right = st.columns(2)

# Chart 1 — Segment distribution
with col_left:
    seg_counts = rfm["Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Count"]
    colors = {
        "Champions": "#2ecc71", "Loyal Customers": "#27ae60",
        "Potential Loyalists": "#3498db", "New Customers": "#9b59b6",
        "At Risk": "#e67e22", "Needs Attention": "#e74c3c",
        "Cant Lose Them": "#c0392b", "Lost": "#95a5a6"
    }
    fig1 = px.bar(seg_counts, x="Segment", y="Count",
                  title="Customers per Segment",
                  color="Segment",
                  color_discrete_map=colors)
    fig1.update_layout(xaxis_tickangle=45, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

# Chart 2 — Revenue per segment
with col_right:
    seg_rev = rfm.groupby("Segment")["Monetary"].sum()              .sort_values(ascending=False).reset_index()
    fig2 = px.bar(seg_rev, x="Segment", y="Monetary",
                  title="Revenue per Segment",
                  color="Monetary", color_continuous_scale="Greens",
                  labels={"Monetary": "Total Revenue (£)"})
    fig2.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig2, use_container_width=True)

# Chart 3 — RFM scatter
st.subheader("RFM Analysis — Recency vs Frequency")
fig3 = px.scatter(rfm, x="Recency", y="Frequency",
                  size="Monetary", color="Segment",
                  color_discrete_map=colors,
                  hover_data=["CustomerID","Monetary"],
                  title="Customer Map — Recency vs Frequency (bubble = spend)",
                  labels={"Recency": "Days since last purchase",
                          "Frequency": "Number of orders"})
st.plotly_chart(fig3, use_container_width=True)

# Churn Risk Table
st.subheader("🚨 At-Risk Customers — Priority Win-Back List")
risk_filter = st.selectbox("Filter by Risk Level",
                            ["All", "Critical", "High", "Medium", "Low"])

churn_display = churn[["CustomerID","Recency","Frequency",
                        "Monetary","Churn_Probability","Churn_Risk",
                        "Segment"]].copy()
churn_display["Churn_Probability"] = (
    churn_display["Churn_Probability"] * 100
).round(1).astype(str) + "%"

if risk_filter != "All":
    churn_display = churn_display[churn_display["Churn_Risk"] == risk_filter]

churn_display = churn_display.sort_values("Churn_Probability", ascending=False)
st.dataframe(churn_display.head(50), use_container_width=True, height=400)
