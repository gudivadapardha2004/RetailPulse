
import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="RetailPulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        border-left: 4px solid #0066cc;
    }
</style>
""", unsafe_allow_html=True)

# Get absolute path to data folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

@st.cache_data
def load_summary():
    df    = pd.read_csv(os.path.join(DATA_DIR, "df_clean.csv"),
                        parse_dates=["InvoiceDate"])
    rfm   = pd.read_csv(os.path.join(DATA_DIR, "rfm_segments.csv"))
    churn = pd.read_csv(os.path.join(DATA_DIR, "churn_predictions.csv"))
    inv   = pd.read_csv(os.path.join(DATA_DIR, "inventory_optimization.csv"))
    return df, rfm, churn, inv

df, rfm, churn, inv = load_summary()

st.title("📊 RetailPulse")
st.subheader("AI-Powered Customer Analytics & Demand Forecasting Platform")
st.markdown("---")

# KPI Row 1
st.subheader("Business Overview")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Revenue",
              f"£{df['TotalPrice'].sum()/1e6:.2f}M",
              delta="2 years of data")
with col2:
    st.metric("Total Transactions",
              f"{len(df):,}",
              delta=f"{df['Invoice'].nunique():,} unique orders")
with col3:
    st.metric("Unique Customers",
              f"{rfm.shape[0]:,}",
              delta=f"{rfm['Segment'].nunique()} segments identified")
with col4:
    st.metric("Countries Served",
              f"{df['Country'].nunique()}",
              delta="Global B2B wholesale")

st.markdown("---")

# KPI Row 2
col5, col6, col7, col8 = st.columns(4)
with col5:
    champions = rfm[rfm["Segment"] == "Champions"]
    st.metric("Champion Customers",
              f"{len(champions):,}",
              delta=f"£{champions['Monetary'].sum():,.0f} revenue")
with col6:
    at_risk = churn[churn["Churn_Risk"].isin(["High","Critical"])]
    st.metric("At-Risk Customers",
              f"{len(at_risk):,}",
              delta="Need win-back campaign",
              delta_color="inverse")
with col7:
    critical_inv = inv[inv["ABC_Category"] == "A — Critical"]
    st.metric("Critical Products",
              f"{len(critical_inv):,}",
              delta="80% of revenue")
with col8:
    avg_order = df.groupby("Invoice")["TotalPrice"].sum().mean()
    st.metric("Avg Order Value",
              f"£{avg_order:,.0f}",
              delta="Per transaction")

st.markdown("---")

st.subheader("Navigate the Dashboard")
col_a, col_b = st.columns(2)
with col_a:
    st.info("**📈 Sales Dashboard**\nRevenue trends, top products, country analysis, hourly patterns")
    st.info("**🔮 Forecast Dashboard**\nProphet demand forecast, 8-week prediction, seasonality breakdown")
with col_b:
    st.info("**👥 Customer Dashboard**\nRFM segments, churn risk scores, at-risk customer table")
    st.info("**📦 Inventory Dashboard**\nABC analysis, reorder recommendations, safety stock levels")

st.markdown("---")
st.caption("Built with Python · Prophet · XGBoost · Streamlit | Zidio Development 2026")
