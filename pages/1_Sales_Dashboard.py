
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📈 Sales Dashboard")
st.markdown("---")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "df_clean.csv"),
                     parse_dates=["InvoiceDate"])
    df["Year"]      = df["InvoiceDate"].dt.year
    df["Month"]     = df["InvoiceDate"].dt.month
    df["DayOfWeek"] = df["InvoiceDate"].dt.dayofweek
    df["Hour"]      = df["InvoiceDate"].dt.hour
    df["YearMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    return df

df = load_data()

st.sidebar.header("Filters")
years = sorted(df["Year"].unique())
selected_years = st.sidebar.multiselect("Select Year", years, default=years)
df_filtered = df[df["Year"].isin(selected_years)]

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue",   f"£{df_filtered['TotalPrice'].sum():,.0f}")
col2.metric("Total Orders",    f"{df_filtered['Invoice'].nunique():,}")
col3.metric("Avg Order Value",
            f"£{df_filtered.groupby('Invoice')['TotalPrice'].sum().mean():,.0f}")
st.markdown("---")

monthly = df_filtered.groupby("YearMonth")["TotalPrice"].sum().reset_index()
fig1 = px.line(monthly, x="YearMonth", y="TotalPrice",
               title="Monthly Revenue Trend",
               labels={"TotalPrice": "Revenue (£)", "YearMonth": "Month"},
               markers=True, color_discrete_sequence=["#0066cc"])
fig1.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig1, use_container_width=True)

col_left, col_right = st.columns(2)

with col_left:
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow  = df_filtered.groupby("DayOfWeek")["TotalPrice"].sum().reset_index()
    dow["Day"] = dow["DayOfWeek"].apply(lambda x: days[x])
    fig2 = px.bar(dow, x="Day", y="TotalPrice",
                  title="Revenue by Day of Week",
                  labels={"TotalPrice": "Revenue (£)"},
                  color="TotalPrice", color_continuous_scale="Blues")
    st.plotly_chart(fig2, use_container_width=True)

with col_right:
    country = df_filtered[df_filtered["Country"] != "United Kingdom"]              .groupby("Country")["TotalPrice"].sum()              .sort_values(ascending=False).head(10).reset_index()
    fig3 = px.bar(country, x="TotalPrice", y="Country", orientation="h",
                  title="Top 10 Countries by Revenue (excl. UK)",
                  labels={"TotalPrice": "Revenue (£)"},
                  color="TotalPrice", color_continuous_scale="Blues")
    fig3.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig3, use_container_width=True)

top_prod = df_filtered.groupby("Description")["TotalPrice"].sum()           .sort_values(ascending=False).head(10).reset_index()
fig4 = px.bar(top_prod, x="TotalPrice", y="Description", orientation="h",
              title="Top 10 Products by Revenue",
              labels={"TotalPrice": "Revenue (£)"},
              color="TotalPrice", color_continuous_scale="Oranges")
fig4.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig4, use_container_width=True)

hourly = df_filtered.groupby("Hour")["TotalPrice"].sum().reset_index()
fig5 = px.area(hourly, x="Hour", y="TotalPrice",
               title="Revenue by Hour of Day",
               labels={"TotalPrice": "Revenue (£)", "Hour": "Hour of Day"},
               color_discrete_sequence=["#0066cc"])
st.plotly_chart(fig5, use_container_width=True)
