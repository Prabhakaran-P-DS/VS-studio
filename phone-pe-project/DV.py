import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="PhonePe Analysis", layout="wide")
st.title("PhonePe  Data Analysis ")

# ---------------- DATABASE CONNECTION ----------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",   
        database="phonepe"
    )

conn = get_connection()

aggregated_transaction = pd.read_sql("SELECT * FROM aggregated_transaction", conn)
aggregated_insurance = pd.read_sql("SELECT * FROM aggregated_insurance", conn)
map_transaction = pd.read_sql("SELECT * FROM map_transaction", conn)
map_user = pd.read_sql("SELECT * FROM map_user", conn)

conn.close()

# ---------------- SIDEBAR ----------------
st.sidebar.title(" Select Analysis")

analysis = st.sidebar.radio(
    "Choose Scenario",
    [
        "1️⃣ Transaction Dynamics",
        "2️⃣ Insurance Growth",
        "3️⃣ Market Expansion",
        "4️⃣ User Engagement"
    ]
)

state = st.sidebar.selectbox("Select State", ["All"] + list(aggregated_transaction["States"].unique()))
year = st.sidebar.selectbox("Select Year", ["All"] + list(aggregated_transaction["Years"].unique()))
quarter = st.sidebar.selectbox("Select Quarter", ["All"] + list(aggregated_transaction["Quarter"].unique()))

# =====================================================
# 1️⃣ TRANSACTION DYNAMICS
# =====================================================
if analysis == "1️⃣ Transaction Dynamics":

    st.header("📈 Decoding Transaction Dynamics")

    df = aggregated_transaction.copy()

    if state != "All":
        df = df[df["States"] == state]
    if year != "All":
        df = df[df["Years"] == year]
    if quarter != "All":
        df = df[df["Quarter"] == quarter]

    total_amt = df["Transaction_amount"].sum()
    total_cnt = df["Transaction_count"].sum()

    col1, col2 = st.columns(2)
    col1.metric("💰 Total Transaction Amount", f"₹ {total_amt:,.0f}")
    col2.metric("🔢 Total Transaction Count", f"{total_cnt:,.0f}")

    # ---- Transaction Type Analysis
    type_df = df.groupby("Transaction_type").sum().reset_index()

    fig1 = px.bar(type_df, x="Transaction_type", y="Transaction_amount",
                  color="Transaction_type",
                  title="Transaction Amount by Type")
    st.plotly_chart(fig1, use_container_width=True)

    # ---- Trend Over Time
    trend_df = df.groupby(["Years", "Quarter"]).sum().reset_index()
    trend_df["Year_Q"] = trend_df["Years"].astype(str) + "-Q" + trend_df["Quarter"].astype(str)

    fig2 = px.line(trend_df, x="Year_Q", y="Transaction_amount",
                   markers=True, title="Quarterly Growth Trend")
    st.plotly_chart(fig2, use_container_width=True)

    # ---- Top 5 States
    top_states = df.groupby("States")["Transaction_amount"].sum().reset_index()
    top5 = top_states.sort_values("Transaction_amount", ascending=False).head(5)

    fig3 = px.bar(top5, x="States", y="Transaction_amount",
                  title="Top 5 Performing States")
    st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# 2️⃣ INSURANCE ANALYSIS
# =====================================================
elif analysis == "2️⃣ Insurance Growth":

    st.header("🛡 Insurance Penetration & Growth")

    df = aggregated_insurance.copy()

    if state != "All":
        df = df[df["States"] == state]
    if year != "All":
        df = df[df["Years"] == year]
    if quarter != "All":
        df = df[df["Quarter"] == quarter]

    total_amt = df["Insurance_amount"].sum()
    total_cnt = df["Insurance_count"].sum()

    col1, col2 = st.columns(2)
    col1.metric("💰 Total Insurance Amount", f"₹ {total_amt:,.0f}")
    col2.metric("📄 Policies Sold", f"{total_cnt:,.0f}")

    # ---- State Contribution
    state_df = df.groupby("States")["Insurance_amount"].sum().reset_index()

    fig1 = px.pie(state_df, names="States", values="Insurance_amount",
                  title="Insurance Contribution by State")
    st.plotly_chart(fig1, use_container_width=True)

    # ---- Growth Trend
    trend_df = df.groupby(["Years", "Quarter"]).sum().reset_index()
    trend_df["Year_Q"] = trend_df["Years"].astype(str) + "-Q" + trend_df["Quarter"].astype(str)

    fig2 = px.line(trend_df, x="Year_Q", y="Insurance_amount",
                   markers=True, title="Insurance Growth Trend")
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# 3️⃣ MARKET EXPANSION
# =====================================================
elif analysis == "3️⃣ Market Expansion":

    st.header("🌍 Transaction Analysis for Market Expansion")

    df = map_transaction.copy()

    if state != "All":
        df = df[df["States"] == state]
    if year != "All":
        df = df[df["Years"] == year]
    if quarter != "All":
        df = df[df["Quarter"] == quarter]

    district_df = df.groupby("District")["Transaction_amount"].sum().reset_index()

    fig1 = px.bar(district_df.sort_values("Transaction_amount", ascending=False).head(10),
                  x="District", y="Transaction_amount",
                  title="Top 10 Districts by Transaction Volume")
    st.plotly_chart(fig1, use_container_width=True)

    # ---- Heatmap style comparison
    heat_df = df.groupby(["States", "Quarter"])["Transaction_amount"].sum().reset_index()

    fig2 = px.density_heatmap(heat_df,
                              x="Quarter",
                              y="States",
                              z="Transaction_amount",
                              title="State vs Quarter Transaction Heatmap")
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# 4️⃣ USER ENGAGEMENT
# =====================================================
elif analysis == "4️⃣ User Engagement":

    st.header("👥 User Engagement & Growth Strategy")

    df = map_user.copy()

    if state != "All":
        df = df[df["States"] == state]
    if year != "All":
        df = df[df["Years"] == year]
    if quarter != "All":
        df = df[df["Quarter"] == quarter]

    total_users = df["RegisteredUser"].sum()
    total_opens = df["AppOpens"].sum()
    engagement = total_opens / total_users if total_users > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("👤 Registered Users", f"{total_users:,.0f}")
    col2.metric("📲 App Opens", f"{total_opens:,.0f}")
    col3.metric("📊 Engagement Rate", f"{engagement:.2f}")

    # ---- State Engagement
    state_df = df.groupby("States").agg({
        "RegisteredUser": "sum",
        "AppOpens": "sum"
    }).reset_index()

    state_df["Engagement_Rate"] = state_df["AppOpens"] / state_df["RegisteredUser"]

    fig1 = px.scatter(state_df,
                      x="RegisteredUser",
                      y="AppOpens",
                      size="Engagement_Rate",
                      color="States",
                      title="State-wise Engagement")
    st.plotly_chart(fig1, use_container_width=True)

    # ---- Growth Trend
    trend_df = df.groupby(["Years", "Quarter"]).sum().reset_index()
    trend_df["Year_Q"] = trend_df["Years"].astype(str) + "-Q" + trend_df["Quarter"].astype(str)

    fig2 = px.line(trend_df, x="Year_Q", y="RegisteredUser",
                   markers=True, title="User Growth Trend")
    st.plotly_chart(fig2, use_container_width=True)
