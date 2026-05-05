
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Forecast Dashboard", layout="wide")
st.title("🔮 Forecast Dashboard")
st.markdown("---")

@st.cache_data
def load_data():
    daily  = pd.read_csv("data/forecast_prophet.csv", parse_dates=["ds"])
    weekly = pd.read_csv("data/forecast_weekly.csv",  parse_dates=["ds"])
    actual = pd.read_csv("data/df_clean.csv", parse_dates=["InvoiceDate"])
    return daily, weekly, actual

daily, weekly, actual = load_data()

col1, col2 = st.columns(2)
col1.metric("Forecast Horizon", "30 days ahead")
col2.metric("Model", "Facebook Prophet")

st.markdown("---")

# Daily forecast chart
st.subheader("Daily Revenue Forecast")
actual_daily = actual.groupby(actual["InvoiceDate"].dt.date)["TotalPrice"]               .sum().reset_index()
actual_daily.columns = ["ds", "actual"]
actual_daily["ds"] = pd.to_datetime(actual_daily["ds"])

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=actual_daily["ds"], y=actual_daily["actual"],
    name="Actual Revenue", line=dict(color="#0066cc", width=1),
    mode="lines"))
fig1.add_trace(go.Scatter(
    x=daily["ds"], y=daily["yhat"].clip(lower=0),
    name="Forecast", line=dict(color="#e74c3c", width=1.5, dash="dash")))
fig1.add_trace(go.Scatter(
    x=daily["ds"], y=daily["yhat_upper"].clip(lower=0),
    fill=None, line=dict(color="rgba(231,76,60,0)"), showlegend=False))
fig1.add_trace(go.Scatter(
    x=daily["ds"], y=daily["yhat_lower"].clip(lower=0),
    fill="tonexty", fillcolor="rgba(231,76,60,0.1)",
    line=dict(color="rgba(231,76,60,0)"), name="Confidence Interval"))
fig1.update_layout(title="Daily Revenue — Actual vs Forecast",
                   xaxis_title="Date", yaxis_title="Revenue (£)",
                   hovermode="x unified")
st.plotly_chart(fig1, use_container_width=True)

# Weekly forecast
st.subheader("Weekly Revenue Forecast — 8 Weeks Ahead")
future_weekly = weekly[weekly["ds"] > actual["InvoiceDate"].max()]
fig2 = px.bar(future_weekly.head(8), x="ds", y="yhat",
              error_y="yhat_upper", error_y_minus="yhat_lower",
              title="8-Week Revenue Prediction",
              labels={"ds": "Week", "yhat": "Predicted Revenue (£)"},
              color_discrete_sequence=["#0066cc"])
st.plotly_chart(fig2, use_container_width=True)

# 30-day future table
st.subheader("30-Day Revenue Forecast Table")
future_30 = daily[daily["ds"] > actual["InvoiceDate"].max()].head(30)[[
    "ds", "yhat", "yhat_lower", "yhat_upper"
]].copy()
future_30.columns = ["Date", "Predicted (£)", "Lower Bound", "Upper Bound"]
for col in ["Predicted (£)", "Lower Bound", "Upper Bound"]:
    future_30[col] = future_30[col].clip(lower=0).round(0).astype(int)
st.dataframe(future_30, use_container_width=True)
st.metric("Total Predicted Revenue (Next 30 Days)",
          f"£{future_30['Predicted (£)'].sum():,}")
