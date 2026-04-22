from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import warnings
warnings.filterwarnings("ignore")

# ✅ ADD THIS LINE
COHERE_API_KEY = os.getenv("COHERE_API_KEY") or st.secrets["COHERE_API_KEY"]
# ==================== PAGE CONFIG ===================
st.set_page_config(
    page_title="LogiTrack - Variance Insights",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ==================== THEME ====================
st.markdown("""
<style>
    :root {
        --primary-bg:    #f5f2ec;
        --secondary-bg:  #eee9df;
        --card-bg:       #f9f6f0;

        --accent-olive:  #7a8c3a;
        --accent-mustard:#c9a227;
        --accent-orange: #e07b39;
        --accent-red:    #d95f4b;
        --accent-blue:   #5b8fa8;

        --border-color:  #d4cbbf;
        --text-dark:     #3a3228;
        --text-muted:    #7a6e62;
    }

    .main { background-color: var(--primary-bg); color: var(--text-dark); }

    [data-testid="stSidebar"] {
        background-color: var(--secondary-bg) !important;
        border-right: 1px solid var(--border-color);
    }

    .sidebar-logo { font-size: 1.4rem; font-weight: 800; color: var(--accent-olive); letter-spacing: -0.5px; margin-bottom: 2px; }
    .sidebar-sub  { color: var(--text-muted); font-size: 0.78rem; margin-bottom: 14px; }
    .sidebar-divider { border-top: 1px solid var(--border-color); margin: 12px 0; }

    .sidebar-info-pill {
        background: #f0ece3;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 8px;
        font-size: 0.8rem;
        color: var(--text-dark);
    }
    .sidebar-info-pill strong { color: var(--accent-olive); }

    .filter-label {
        color: var(--text-muted);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin: 14px 0 4px 0;
    }

    .header-banner {
        background: linear-gradient(135deg, #eee9df 0%, #e8e0d0 50%, #dfd6c4 100%);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--accent-olive);
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .header-banner h2 { font-size: 1.3rem; margin: 0 0 4px 0; color: var(--accent-olive); font-weight: 800; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--secondary-bg);
        padding: 4px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-muted);
        font-size: 0.85rem;
        font-weight: 600;
        padding: 8px 16px;
        border-radius: 8px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: #e0d8c8 !important;
        color: var(--accent-olive) !important;
    }

    .section-title {
        font-size: 1rem;
        font-weight: 800;
        color: var(--accent-olive);
        letter-spacing: 0.3px;
        margin: 24px 0 14px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #d4cbbf;
    }

    [data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; }
    [data-testid="stMetricValue"] { color: var(--text-dark) !important; font-size: 1.8rem !important; font-weight: 800; }

    .ibox { border-radius: 10px; padding: 16px 18px; color: var(--text-dark); font-size: 0.88rem; line-height: 1.65; border-left: 4px solid transparent; margin-bottom: 10px; }
    .ibox-olive   { background: #eef1e4; border-left-color: #7a8c3a; }
    .ibox-mustard { background: #fdf5df; border-left-color: #c9a227; }
    .ibox-orange  { background: #fdf0e6; border-left-color: #e07b39; }
    .ibox-red     { background: #fdecea; border-left-color: #d95f4b; }
    .ibox-blue    { background: #e8f1f5; border-left-color: #5b8fa8; }
    .ibox-title { font-weight: 700; font-size: 0.9rem; margin-bottom: 6px; display: flex; align-items: center; gap: 7px; }
    .ibox-title.olive   { color: #7a8c3a; }
    .ibox-title.mustard { color: #c9a227; }
    .ibox-title.orange  { color: #e07b39; }
    .ibox-title.red     { color: #d95f4b; }
    .ibox-title.blue    { color: #5b8fa8; }

    .ai-panel {
        background: #f9f6f0;
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 16px;
    }
    .ai-panel-title { color: var(--accent-olive); font-weight: 800; font-size: 1rem; margin-bottom: 12px; }
    .ai-response {
        background: #f0ece3;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 14px 16px;
        color: var(--text-dark);
        font-size: 0.9rem;
        line-height: 1.7;
    }

    .footer { text-align: center; color: var(--text-muted); font-size: 0.75rem; margin-top: 40px; padding-top: 14px; border-top: 1px solid var(--border-color); }
</style>
""", unsafe_allow_html=True)

# ==================== LOAD DATA ====================
EXCEL_PATH = "Shipping dataset.xlsx"

@st.cache_data
def load_all_data():
    xl       = pd.read_excel(EXCEL_PATH, sheet_name=None)
    ships    = xl["Fact_Shipments"].copy()
    carriers = xl["Dim_Carriers"].copy()
    delays_d = xl["Dim_Delays"].copy()
    ship_del = xl["Dim_Shipment_Delays"].copy()

    ships = ships.merge(carriers[["carrier_id","carrier_name","service_level_agreement_days","contract_type"]], on="carrier_id", how="left")
    ships["promised_date"]  = pd.to_datetime(ships["promised_date"],  errors="coerce")
    ships["reported_date"]  = pd.to_datetime(ships["reported_date"],  errors="coerce")
    ships["transit_days"]   = (ships["reported_date"] - ships["promised_date"]).dt.days.clip(lower=0)
    ships["is_late"]        = ships["transit_days"] > ships["service_level_agreement_days"]
    ships["year_month"]     = ships["reported_date"].dt.to_period("M").astype(str)
    ships["year"]           = ships["reported_date"].dt.year

    merged_del = ship_del.merge(delays_d, on="delay_id", how="left")
    ships = ships.merge(merged_del[["shipment_id","delay_days","reason_category"]], on="shipment_id", how="left")
    return ships, carriers, delays_d

df_all, carriers_df, delays_dim_df = load_all_data()

# ==================== CHART DEFAULTS ====================
PALETTE  = ["#7a8c3a","#c9a227","#e07b39","#d95f4b","#5b8fa8","#a3b86c","#e8c97a","#f0a87a","#e89090","#8bbccc"]
CHART_BG = "#f5f2ec"
TEXT_CLR = "#3a3228"
GRID_CLR = "#d4cbbf"

def bl(title="", h=380):
    return dict(title=dict(text=title, font=dict(color=TEXT_CLR, size=13)),
                paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(color=TEXT_CLR, size=11), height=h,
                margin=dict(l=10, r=10, t=40 if title else 20, b=10),
                xaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
                yaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)))

# ==================== AI HELPER ====================
def call_ai(prompt_text):
    groq_key   = os.getenv("GROQ_API_KEY", "")
    cohere_key = os.getenv("COHERE_API_KEY", "")
    system_msg = ("You are LogiTrust AI, a concise logistics analytics assistant. "
                  "Answer in 4-5 bullet points using the data context. Be specific and practical. Max 160 words.")
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            resp = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role":"system","content":system_msg},{"role":"user","content":prompt_text}],
                max_tokens=320, temperature=0.4)
            return resp.choices[0].message.content.strip()
        except Exception:
            pass
    if cohere_key:
        try:
            import cohere
            co = cohere.Client(cohere_key)
            resp = co.chat(model="command-r", preamble=system_msg, message=prompt_text, max_tokens=320, temperature=0.4)
            return resp.text.strip()
        except Exception:
            pass
    return None

# ==================== SIDEBAR ====================
st.sidebar.markdown('<div class="sidebar-logo">🚚 LogiTrack</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-sub">Variance Insights</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
st.sidebar.markdown(f"""
<div class="sidebar-info-pill">📦 <strong>{len(df_all):,}</strong> Total Records</div>
<div class="sidebar-info-pill">🚚 <strong>{df_all['carrier_name'].nunique()}</strong> Carriers &nbsp;|&nbsp; <strong>{df_all['item_category'].nunique()}</strong> Categories</div>
<div class="sidebar-info-pill">📅 <strong>{df_all['reported_date'].min().strftime('%Y-%m-%d')}</strong> → <strong>{df_all['reported_date'].max().strftime('%Y-%m-%d')}</strong></div>
""", unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

st.sidebar.markdown('<div class="filter-label">🗓️ Month</div>', unsafe_allow_html=True)

month_opts = ["All Months"] + sorted(df_all["year_month"].dropna().unique().tolist())
month_sel  = st.sidebar.selectbox("Month", month_opts, label_visibility="collapsed")

st.sidebar.markdown('<div class="filter-label">🔍 Tracking Number</div>', unsafe_allow_html=True)
# Dynamically filter tracking numbers by selected month
if month_sel != "All Months":
    _track_pool = df_all[df_all["year_month"] == month_sel]["tracking_number"].dropna().unique()
else:
    _track_pool = df_all["tracking_number"].dropna().unique()
track_opts = ["All Shipments"] + sorted(_track_pool.tolist())
track_sel = st.sidebar.selectbox("Tracking Number", track_opts, label_visibility="collapsed")

st.sidebar.markdown('<div class="filter-label">🚚 Carrier</div>', unsafe_allow_html=True)
carrier_opts = ["All Carriers"] + sorted(df_all["carrier_name"].dropna().unique().tolist())
carrier_sel  = st.sidebar.selectbox("Carrier", carrier_opts, label_visibility="collapsed")

st.sidebar.markdown('<div class="filter-label">📦 Item Category</div>', unsafe_allow_html=True)
cat_opts = ["All Categories"] + sorted(df_all["item_category"].dropna().unique().tolist())
cat_sel  = st.sidebar.selectbox("Category", cat_opts, label_visibility="collapsed")

st.sidebar.markdown('<div class="filter-label">🏷️ Item Name</div>', unsafe_allow_html=True)
item_pool = (df_all["item_name"].dropna().unique().tolist() if cat_sel == "All Categories"
             else df_all[df_all["item_category"]==cat_sel]["item_name"].dropna().unique().tolist())
item_opts = ["All Items"] + sorted(item_pool)
item_sel  = st.sidebar.selectbox("Item", item_opts, label_visibility="collapsed")

st.sidebar.markdown('<div class="filter-label">📊 Status</div>', unsafe_allow_html=True)
status_opts = ["All Statuses"] + sorted(df_all["status"].dropna().unique().tolist())
status_sel  = st.sidebar.selectbox("Status", status_opts, label_visibility="collapsed")

st.sidebar.markdown('<div class="filter-label">🤝 Contract Type</div>', unsafe_allow_html=True)
ctype_opts = ["All Types"] + sorted(df_all["contract_type"].dropna().unique().tolist())
ctype_sel  = st.sidebar.selectbox("Contract", ctype_opts, label_visibility="collapsed")

st.sidebar.markdown("---")
only_late = st.sidebar.checkbox("⚠️ Only Late Shipments")
only_fail = st.sidebar.checkbox("🔴 Only Failed / Cancelled")

# ==================== APPLY FILTERS ====================
df = df_all.copy()
if month_sel != "All Months":
    df = df[df["year_month"] == month_sel]
if track_sel != "All Shipments":
    df = df[df["tracking_number"] == track_sel]
if carrier_sel != "All Carriers":
    df = df[df["carrier_name"] == carrier_sel]
if cat_sel != "All Categories":
    df = df[df["item_category"] == cat_sel]
if item_sel != "All Items":
    df = df[df["item_name"] == item_sel]
if status_sel != "All Statuses":
    df = df[df["status"] == status_sel]
if ctype_sel != "All Types":
    df = df[df["contract_type"] == ctype_sel]
if only_late:
    df = df[df["is_late"] == True]
if only_fail:
    df = df[df["status"].isin(["Cancelled","Failed Delivery"])]

# ==================== KPIs ====================
n_total     = len(df)
n_delivered = (df["status"]=="Delivered").sum()
n_delayed   = (df["status"]=="Delayed").sum()
n_transit   = (df["status"]=="In Transit").sum()
n_failed    = df["status"].isin(["Cancelled","Failed Delivery"]).sum()
del_rate    = n_delivered/n_total*100 if n_total else 0
delay_pct   = n_delayed/n_total*100   if n_total else 0
avg_transit = df["transit_days"].mean() if n_total else 0
avg_cost    = df["shipping_cost"].mean() if n_total else 0
total_cost  = df["shipping_cost"].sum()
top_carrier = df["carrier_name"].value_counts().idxmax() if n_total else "N/A"
top_cat     = df["item_category"].value_counts().idxmax() if n_total else "N/A"
risk_val    = df[df["status"].isin(["Delayed","Cancelled","Failed Delivery"])]["shipping_cost"].sum()

# ==================== HEADER ====================
st.markdown("""
<div class="header-banner">
  <h2>🚚 LogiTrack — Variance Insights</h2>
  Advanced analytics for shipment tracking · carrier performance · delay profiling · product correlation · AI-powered recommendations
</div>
""", unsafe_allow_html=True)

# ==================== TABS ====================
t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
    "📊 Summary", "📦 Shipments", "🚚 Carriers",
    "⚠️ Delays", "🏷️ Categories", "📍 Tracking View", "🤖 AI Insights", "📖 About"
])

# ════════════════════════════════════════
# TAB 1 — SUMMARY
# ════════════════════════════════════════
with t1:
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("TOTAL SHIPMENTS", f"{n_total:,}",        "Selected period")
    c2.metric("DELIVERY RATE",   f"{del_rate:.1f}%",    f"{n_delivered:,} delivered")
    c3.metric("DELAYED",         f"{n_delayed:,}",      "Flagged")
    c4.metric("IN TRANSIT",      f"{n_transit:,}",      "Active")
    c5.metric("AVG DELIVERY",    f"{avg_transit:.1f}d", "Transit time")
    c6.metric("FAILED/CANCELLED",f"{n_failed:,}",       "At-risk")

    st.markdown('<div class="section-title">🎯 Smart Insights</div>', unsafe_allow_html=True)
    cl, cr = st.columns(2)
    with cl:
        st.markdown(f"""
        <div class="ibox ibox-olive"><div class="ibox-title olive">📍 Highest volume carrier</div>
        <b>{top_carrier}</b> handles the most shipments in the selected period.</div>
        <div class="ibox ibox-mustard"><div class="ibox-title mustard">📦 Top item category</div>
        <b>{top_cat}</b> accounts for the highest shipment volume.</div>
        <div class="ibox ibox-orange"><div class="ibox-title orange">⏱️ SLA Performance</div>
        Avg transit <b>{avg_transit:.1f} days</b> · Delay rate <b>{delay_pct:.1f}%</b> · Avg cost <b>₹{avg_cost:,.0f}</b></div>
        """, unsafe_allow_html=True)
    with cr:
        st.markdown(f"""
        <div class="ibox ibox-blue"><div class="ibox-title blue">ℹ️ Performance Overview</div>
        Delivery rate is <b>{del_rate:.1f}%</b> with <b>{delay_pct:.1f}%</b> delayed.
        Average transit of {avg_transit:.1f} days reflects the current carrier and filter mix.</div>
        <div class="ibox ibox-olive"><div class="ibox-title olive">💡 Suggestions</div>
        Focus on delayed <b>{top_cat}</b> shipments via <b>{top_carrier}</b>.
        Review SLA contracts for carriers exceeding average transit times.</div>
        <div class="ibox ibox-red"><div class="ibox-title red">🛡️ Risk Analysis</div>
        Value at risk from delays & failures: <b>₹{risk_val:,.0f}</b>.
        Consider SLA-based contracts for high-value item categories.</div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    cg, ct = st.columns(2)
    with cg:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=del_rate,
            delta={"reference":90,"valueformat":".1f"},
            title={"text":"Delivery Success Rate (%)"},
            gauge={"axis":{"range":[0,100],"tickcolor":TEXT_CLR},
                   "bar":{"color":"#7a8c3a"},
                   "steps":[{"range":[0,60],"color":"#fdecea"},{"range":[60,80],"color":"#fdf5df"},{"range":[80,100],"color":"#eef1e4"}],
                   "threshold":{"line":{"color":"#d95f4b","width":4},"value":90,"thickness":0.75}}))
        fig_g.update_layout(paper_bgcolor=CHART_BG, font=dict(color=TEXT_CLR), height=300, margin=dict(t=30,b=0))
        st.plotly_chart(fig_g, use_container_width=True)
    with ct:
        st.markdown("**📋 Recent Shipments**")
        st.dataframe(df[["tracking_number","carrier_name","item_category","item_name","status","transit_days","shipping_cost"]].head(12).rename(columns={
            "tracking_number":"Tracking","carrier_name":"Carrier","item_category":"Category",
            "item_name":"Item","status":"Status","transit_days":"Days","shipping_cost":"Cost (₹)"}),
            hide_index=True, use_container_width=True)

    st.markdown('<div class="section-title">📈 Monthly Shipment Trend</div>', unsafe_allow_html=True)
    monthly = df.groupby("year_month").agg(
        Shipments=("shipment_id","count"),
        Delivered=("status", lambda x:(x=="Delivered").sum()),
        Delayed=("status",   lambda x:(x=="Delayed").sum()),
    ).reset_index().sort_values("year_month")
    fig_tr = go.Figure()
    fig_tr.add_trace(go.Scatter(x=monthly["year_month"],y=monthly["Shipments"],name="Total",    line=dict(color="#5b8fa8",width=2)))
    fig_tr.add_trace(go.Scatter(x=monthly["year_month"],y=monthly["Delivered"],name="Delivered",line=dict(color="#7a8c3a",width=2)))
    fig_tr.add_trace(go.Scatter(x=monthly["year_month"],y=monthly["Delayed"],  name="Delayed",  line=dict(color="#d95f4b",width=2,dash="dot")))
    fig_tr.update_layout(**bl(h=320))
    st.plotly_chart(fig_tr, use_container_width=True)

# ════════════════════════════════════════
# TAB 2 — SHIPMENTS
# ════════════════════════════════════════
with t2:
    st.markdown('<div class="section-title">📦 Shipment Status & Volume</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        sc = df["status"].value_counts().reset_index(); sc.columns=["Status","Count"]
        fig=px.pie(sc,names="Status",values="Count",color_discrete_sequence=PALETTE,hole=0.45)
        fig.update_layout(**bl("Shipment Status Distribution")); fig.update_traces(textfont_color=TEXT_CLR)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        cv=df["carrier_name"].value_counts().reset_index(); cv.columns=["Carrier","Shipments"]
        fig=px.bar(cv,x="Carrier",y="Shipments",color="Shipments",color_continuous_scale=["#eef1e4","#7a8c3a"])
        fig.update_layout(**bl("Shipments by Carrier")); fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">💰 Cost & Day Patterns</div>', unsafe_allow_html=True)
    c3,c4 = st.columns(2)
    with c3:
        fig=px.histogram(df,x="shipping_cost",nbins=40,color_discrete_sequence=["#e07b39"])
        fig.update_layout(**bl("Shipping Cost Distribution (₹)"))
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        df2=df.copy(); df2["day_name"]=df2["reported_date"].dt.day_name()
        day_order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dv=df2.groupby("day_name").size().reindex(day_order).reset_index(); dv.columns=["Day","Shipments"]
        fig=px.bar(dv,x="Day",y="Shipments",color_discrete_sequence=["#c9a227"])
        fig.update_layout(**bl("Shipments by Day of Week"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">📅 SLA: Promised vs Reported Delivery</div>', unsafe_allow_html=True)
    c5,c6 = st.columns(2)
    with c5:
        sla=df.groupby("carrier_name").agg(SLA=("service_level_agreement_days","mean"),Actual=("transit_days","mean")).reset_index()
        fig=go.Figure()
        fig.add_trace(go.Bar(name="SLA Promised",x=sla["carrier_name"],y=sla["SLA"],   marker_color="#5b8fa8"))
        fig.add_trace(go.Bar(name="Actual Avg",  x=sla["carrier_name"],y=sla["Actual"],marker_color="#e07b39"))
        fig.update_layout(**bl("SLA Promised vs Actual Days"),barmode="group")
        st.plotly_chart(fig, use_container_width=True)
    with c6:
        fig=px.box(df,x="carrier_name",y="transit_days",color="carrier_name",color_discrete_sequence=PALETTE)
        fig.update_layout(**bl("Transit Days Distribution by Carrier"),showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">📋 Shipment Records</div>', unsafe_allow_html=True)
    disp=df[["tracking_number","carrier_name","item_category","item_name","status","promised_date","reported_date","transit_days","shipping_cost"]].copy()
    disp.columns=["Tracking","Carrier","Category","Item","Status","Promised","Reported","Transit Days","Cost (₹)"]
    disp["Promised"]=pd.to_datetime(disp["Promised"]).dt.date
    disp["Reported"]=pd.to_datetime(disp["Reported"]).dt.date
    st.dataframe(disp, hide_index=True, use_container_width=True)

# ════════════════════════════════════════
# TAB 3 — CARRIERS
# ════════════════════════════════════════
with t3:
    st.markdown('<div class="section-title">🚚 Carrier Performance Summary</div>', unsafe_allow_html=True)
    cp=df.groupby("carrier_name").agg(
        Total=("shipment_id","count"),
        Delivered=("status",lambda x:(x=="Delivered").sum()),
        Delayed=("status",  lambda x:(x=="Delayed").sum()),
        AvgDays=("transit_days","mean"),
        AvgCost=("shipping_cost","mean"),
    ).reset_index()
    cp["Delivery_%"]=(cp["Delivered"]/cp["Total"]*100).round(1)
    cp["Delay_%"]   =(cp["Delayed"]  /cp["Total"]*100).round(1)
    cp["OnTime_%"]  =(100-cp["Delay_%"]).round(1)
    cp["AvgDays"]   =cp["AvgDays"].round(1)
    cp["AvgCost"]   =cp["AvgCost"].round(0)
    st.dataframe(cp[["carrier_name","Total","Delivered","Delayed","Delivery_%","Delay_%","AvgDays","AvgCost"]].rename(columns={
        "carrier_name":"Carrier","Delivery_%":"Delivery %","Delay_%":"Delay %",
        "AvgDays":"Avg Days","AvgCost":"Avg Cost (₹)"}), hide_index=True, use_container_width=True)

    st.markdown('<div class="section-title">📊 Delivery · Delay · On-Time Rates</div>', unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        fig=go.Figure()
        fig.add_trace(go.Bar(name="On-Time %",x=cp["carrier_name"],y=cp["OnTime_%"], marker_color="#7a8c3a"))
        fig.add_trace(go.Bar(name="Delay %",  x=cp["carrier_name"],y=cp["Delay_%"],  marker_color="#d95f4b"))
        fig.update_layout(**bl("On-Time vs Delay Rate by Carrier"),barmode="stack")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig=px.bar(cp.sort_values("AvgDays"),x="carrier_name",y="AvgDays",color="AvgDays",
                   color_continuous_scale=["#eef1e4","#c9a227","#d95f4b"])
        fig.update_layout(**bl("Avg Delivery Days by Carrier")); fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">💰 Carrier Efficiency Matrix & Cost</div>', unsafe_allow_html=True)
    c3,c4=st.columns(2)
    with c3:
        fig=px.scatter(cp,x="AvgDays",y="Delivery_%",size="Total",text="carrier_name",color="Delay_%",
                       color_continuous_scale=["#7a8c3a","#c9a227","#d95f4b"],
                       labels={"AvgDays":"Avg Days","Delivery_%":"Delivery %"})
        fig.update_traces(textposition="top center",textfont_size=9)
        fig.update_layout(**bl("Carrier Efficiency Matrix (bubble = volume)"))
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig=px.bar(cp.sort_values("AvgCost"),x="AvgCost",y="carrier_name",orientation="h",color="AvgCost",
                   color_continuous_scale=["#e8f1f5","#5b8fa8"])
        fig.update_layout(**bl("Avg Shipping Cost by Carrier (₹)")); fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">📈 Monthly Carrier Volume Trend</div>', unsafe_allow_html=True)
    mct=df.groupby(["year_month","carrier_name"]).size().reset_index(name="Shipments")
    fig=px.line(mct,x="year_month",y="Shipments",color="carrier_name",color_discrete_sequence=PALETTE)
    fig.update_layout(**bl(h=380))
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════
# TAB 4 — DELAYS
# ════════════════════════════════════════
with t4:
    st.markdown('<div class="section-title">⚠️ Delay Reason Analysis</div>', unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        rc=df["reason_category"].dropna().value_counts().reset_index(); rc.columns=["Reason","Count"]
        fig=px.bar(rc,x="Count",y="Reason",orientation="h",color="Count",
                   color_continuous_scale=["#fdf0e6","#d95f4b"])
        fig.update_layout(**bl("Delay Reasons Frequency")); fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        di=df.groupby("reason_category")["delay_days"].mean().dropna().sort_values(ascending=False).reset_index()
        di.columns=["Reason","Avg Delay Days"]
        fig=px.bar(di,x="Reason",y="Avg Delay Days",color="Avg Delay Days",
                   color_continuous_scale=["#fdf5df","#c9a227","#d95f4b"])
        fig.update_layout(**bl("Avg Delay Days by Reason"),xaxis_tickangle=-30); fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">🚚 Carrier Delay Breakdown</div>', unsafe_allow_html=True)
    c3,c4=st.columns(2)
    with c3:
        cd=df.groupby("carrier_name").apply(lambda x: pd.Series({
            "On-Time":(x["status"]=="Delivered").sum(),
            "Delayed":(x["status"]=="Delayed").sum(),
            "Failed": x["status"].isin(["Cancelled","Failed Delivery"]).sum()})).reset_index()
        fig=go.Figure()
        fig.add_trace(go.Bar(name="On-Time",x=cd["carrier_name"],y=cd["On-Time"],marker_color="#7a8c3a"))
        fig.add_trace(go.Bar(name="Delayed",x=cd["carrier_name"],y=cd["Delayed"],marker_color="#c9a227"))
        fig.add_trace(go.Bar(name="Failed", x=cd["carrier_name"],y=cd["Failed"], marker_color="#d95f4b"))
        fig.update_layout(**bl("Carrier: On-Time vs Delayed vs Failed"),barmode="group")
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        hp=df.groupby(["carrier_name","reason_category"]).size().reset_index(name="Count")
        hpv=hp.pivot(index="carrier_name",columns="reason_category",values="Count").fillna(0)
        fig=px.imshow(hpv,color_continuous_scale=["#f5f2ec","#c9a227","#d95f4b"],aspect="auto")
        fig.update_layout(**bl("Delay Reason Heatmap: Carrier × Reason",h=380))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">📅 Monthly Delay Trend</div>', unsafe_allow_html=True)
    dm=df.groupby("year_month").apply(lambda x: pd.Series({
        "Delayed":(x["status"]=="Delayed").sum(),
        "Delay_Pct":(x["status"]=="Delayed").sum()/len(x)*100})).reset_index().sort_values("year_month")
    c5,c6=st.columns(2)
    with c5:
        fig=px.line(dm,x="year_month",y="Delayed",color_discrete_sequence=["#d95f4b"])
        fig.update_layout(**bl("Monthly Delayed Shipments"))
        st.plotly_chart(fig, use_container_width=True)
    with c6:
        fig=px.area(dm,x="year_month",y="Delay_Pct",color_discrete_sequence=["#e07b39"])
        fig.update_layout(**bl("Monthly Delay Rate (%)"))
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════
# TAB 5 — CATEGORIES
# ════════════════════════════════════════
with t5:
    st.markdown('<div class="section-title">🏷️ Category Distribution</div>', unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        cv2=df["item_category"].value_counts().reset_index(); cv2.columns=["Category","Shipments"]
        fig=px.bar(cv2,x="Category",y="Shipments",color="Shipments",color_continuous_scale=["#eef1e4","#7a8c3a"])
        fig.update_layout(**bl("Shipments by Category"),xaxis_tickangle=-30); fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        cr2=df.groupby("item_category")["shipping_cost"].sum().reset_index(); cr2.columns=["Category","Total Cost"]
        fig=px.pie(cr2,names="Category",values="Total Cost",color_discrete_sequence=PALETTE,hole=0.4)
        fig.update_layout(**bl("Shipping Revenue Share by Category")); fig.update_traces(textfont_color=TEXT_CLR)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">🔗 Product Correlation Map (Co-occurrence)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="ibox ibox-blue">
        <div class="ibox-title blue">ℹ️ What is this?</div>
        This heatmap shows how strongly item categories correlate in shipping patterns across carrier/month combinations.
        High positive correlation (bright) = categories frequently shipped together or in the same volume cycles —
        suggesting bundling or cross-sell opportunities.
    </div>""", unsafe_allow_html=True)
    corr_proxy  = df.groupby(["year_month","carrier_name","item_category"]).size().unstack(fill_value=0)
    corr_matrix = corr_proxy.corr()
    fig=px.imshow(corr_matrix,text_auto=".2f",color_continuous_scale=["#f5f2ec","#c9a227","#7a8c3a"],aspect="auto",zmin=-1,zmax=1)
    fig.update_layout(**bl("Category Correlation / Co-occurrence Matrix",h=480))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">🛍️ Top Items & Category Risk Matrix</div>', unsafe_allow_html=True)
    c3,c4=st.columns(2)
    with c3:
        ti=df["item_name"].value_counts().head(15).reset_index(); ti.columns=["Item","Count"]
        fig=px.bar(ti,x="Count",y="Item",orientation="h",color="Count",color_continuous_scale=["#fdf0e6","#e07b39"])
        fig.update_layout(**bl("Top 15 Most Shipped Items",h=420)); fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        cat_risk=df.groupby("item_category").apply(lambda x: pd.Series({
            "Delay_Rate":(x["status"]=="Delayed").sum()/len(x)*100,
            "Avg_Cost":  x["shipping_cost"].mean(),
            "Volume":    len(x)})).reset_index()
        fig=px.scatter(cat_risk,x="Avg_Cost",y="Delay_Rate",size="Volume",text="item_category",
                       color="Delay_Rate",color_continuous_scale=["#7a8c3a","#c9a227","#d95f4b"],
                       labels={"Avg_Cost":"Avg Shipping Cost (₹)","Delay_Rate":"Delay Rate %"})
        fig.update_traces(textposition="top center",textfont_size=8)
        fig.update_layout(**bl("Category Risk Matrix (bubble = volume)",h=420))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">🚚 Category × Carrier Volume Heatmap</div>', unsafe_allow_html=True)
    cch=df.groupby(["item_category","carrier_name"]).size().reset_index(name="Count")
    ccp=cch.pivot(index="item_category",columns="carrier_name",values="Count").fillna(0)
    fig=px.imshow(ccp,text_auto=True,color_continuous_scale=["#f5f2ec","#c9a227","#7a8c3a"],aspect="auto")
    fig.update_layout(**bl("Category × Carrier Volume Heatmap",h=400))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">📈 Category Volume Over Time</div>', unsafe_allow_html=True)
    ct2=df.groupby(["year_month","item_category"]).size().reset_index(name="Shipments")
    fig=px.line(ct2,x="year_month",y="Shipments",color="item_category",color_discrete_sequence=PALETTE)
    fig.update_layout(**bl(h=380))
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════
# TAB 6 — TRACKING VIEW
# ════════════════════════════════════════
with t6:
    st.markdown('<div class="section-title">📍 Shipment Tracking View</div>', unsafe_allow_html=True)

    # Month filter for tracking view
    tv_month_opts = ["All Months"] + sorted(df_all["year_month"].dropna().unique().tolist())
    tv_month = st.selectbox("📅 Filter by Month", tv_month_opts, key="tv_month")

    tv_pool = df_all if tv_month == "All Months" else df_all[df_all["year_month"] == tv_month]
    tv_track_opts = sorted(tv_pool["tracking_number"].dropna().unique().tolist())

    if not tv_track_opts:
        st.warning("No tracking numbers available for this month.")
    else:
        sel_track = st.selectbox("🔍 Select Tracking Number", tv_track_opts, key="tv_track")
        ship = tv_pool[tv_pool["tracking_number"] == sel_track].iloc[0]

        promised = ship["promised_date"].strftime("%d-%m-%Y")
        reported = ship["reported_date"].strftime("%d-%m-%Y")

        if ship["promised_date"].date() == ship["reported_date"].date():
            final_status = "Successfully Delivered ✅"
            status_color = "#e6f4ea"
            status_border = "#34a853"
            delay_reason = "No Delay"
        else:
            final_status = ship["status"]
            status_color = "#fdecea"
            status_border = "#d95f4b"
            delay_reason = ship.get("reason_category", "—") or "—"

        # — Metrics row —
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Tracking #", sel_track)
        c2.metric("Promised Date", promised)
        c3.metric("Reported Date", reported)
        c4.metric("Transit Days", int(ship["transit_days"]))
        c5.metric("Delay Days", int(ship["delay_days"]) if pd.notna(ship.get("delay_days")) else 0)

        # — Route —
        st.markdown("### 🗺️ Route Details")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Origin City", ship["origin_city"])
        r2.metric("Destination City", ship["dest_city"])
        r3.metric("Carrier", ship["carrier_name"])
        r4.metric("Contract Type", ship["contract_type"])

        # — Status banner —
        st.markdown(
            f'<div style="background:{status_color};border-left:8px solid {status_border};'
            f'border-radius:12px;padding:22px;font-size:22px;font-weight:900;text-align:center;margin:18px 0;">'
            f'Status: {final_status}</div>',
            unsafe_allow_html=True
        )

        # — Delay Reason —
        st.markdown(
            f'<div style="background:#fff8e6;padding:16px;border-radius:10px;'
            f'border-left:6px solid #c2a83e;font-weight:800;text-align:center;margin-bottom:20px;">'
            f'Delay Reason: {delay_reason}</div>',
            unsafe_allow_html=True
        )

        # ── Monthly Visuals for Tracking View ──
        st.markdown('<div class="section-title">📊 Monthly Performance for This Month</div>', unsafe_allow_html=True)

        month_data = tv_pool.copy() if tv_month != "All Months" else df_all[df_all["year_month"] == ship["year_month"]].copy()

        mv1, mv2, mv3 = st.columns(3)

        with mv1:
            st.metric("Total Shipments This Month", f"{len(month_data):,}")
            st.metric("Delivery Rate", f"{(month_data['status']=='Delivered').mean()*100:.1f}%")

        with mv2:
            st.metric("Delayed This Month", f"{(month_data['status']=='Delayed').sum():,}")
            st.metric("Avg Transit Days", f"{month_data['transit_days'].mean():.1f}")

        with mv3:
            st.metric("Avg Shipping Cost", f"₹{month_data['shipping_cost'].mean():,.0f}")
            st.metric("Total Revenue", f"₹{month_data['shipping_cost'].sum():,.0f}")

        mv_c1, mv_c2 = st.columns(2)
        with mv_c1:
            # Status distribution for that month
            sc_m = month_data["status"].value_counts().reset_index(); sc_m.columns = ["Status","Count"]
            fig = px.pie(sc_m, names="Status", values="Count", color_discrete_sequence=PALETTE, hole=0.45)
            fig.update_layout(**bl("Shipment Status This Month", h=320))
            fig.update_traces(textfont_color=TEXT_CLR)
            st.plotly_chart(fig, use_container_width=True)

        with mv_c2:
            # Delay reasons this month
            dr_m = month_data["reason_category"].dropna().value_counts().reset_index()
            dr_m.columns = ["Reason","Count"]
            if not dr_m.empty:
                fig = px.bar(dr_m, x="Count", y="Reason", orientation="h",
                             color="Count", color_continuous_scale=["#fdf0e6","#d95f4b"])
                fig.update_layout(**bl("Delay Reasons This Month", h=320))
                fig.update_coloraxes(showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No delay data for this month.")

        # Carrier performance this month
        st.markdown('<div class="section-title">🚚 Carrier Performance This Month</div>', unsafe_allow_html=True)
        cp_m = month_data.groupby("carrier_name").agg(
            Total=("shipment_id","count"),
            OnTime=("status", lambda x:(x=="Delivered").sum()),
            Delayed=("status", lambda x:(x=="Delayed").sum()),
            AvgDays=("transit_days","mean")
        ).reset_index()
        cp_m["OnTime_%"] = (cp_m["OnTime"]/cp_m["Total"]*100).round(1)
        cp_m["Delay_%"]  = (cp_m["Delayed"]/cp_m["Total"]*100).round(1)

        fig = go.Figure()
        fig.add_trace(go.Bar(name="On-Time", x=cp_m["carrier_name"], y=cp_m["OnTime_%"], marker_color="#7a8c3a"))
        fig.add_trace(go.Bar(name="Delayed", x=cp_m["carrier_name"], y=cp_m["Delay_%"],  marker_color="#d95f4b"))
        fig.update_layout(**bl("Carrier On-Time vs Delay % — This Month", h=340), barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        # Reliability trend across all months for same carrier
        st.markdown(f'<div class="section-title">📈 Reliability Trend — {ship["carrier_name"]}</div>', unsafe_allow_html=True)
        carrier_trend = df_all[df_all["carrier_name"] == ship["carrier_name"]].groupby("year_month").apply(
            lambda x: pd.Series({
                "OnTime_Pct": (x["status"]=="Delivered").sum()/len(x)*100,
                "Delay_Pct":  (x["status"]=="Delayed").sum()/len(x)*100,
                "Avg_Transit": x["transit_days"].mean()
            })
        ).reset_index().sort_values("year_month")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=carrier_trend["year_month"], y=carrier_trend["OnTime_Pct"],
                                 name="On-Time %", line=dict(color="#7a8c3a", width=2)))
        fig.add_trace(go.Scatter(x=carrier_trend["year_month"], y=carrier_trend["Delay_Pct"],
                                 name="Delay %", line=dict(color="#d95f4b", width=2, dash="dot")))
        fig.update_layout(**bl(f"{ship['carrier_name']} — Monthly Reliability", h=340))
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════
# TAB 7 — AI INSIGHTS
# ════════════════════════════════════════
with t7:
    st.markdown('<div class="section-title">🤖 Cohere AI — Logistics Insights Engine</div>', unsafe_allow_html=True)

    filtered = df.copy()

    # =========================
    # SMART SUMMARIES (JSON)
    # =========================
    carrier_summary = (
        filtered.groupby("carrier_name")
        .agg(
            shipments=("shipment_id", "count"),
            delivery_rate=("status", lambda x: (x == "Delivered").mean() * 100),
            delay_rate=("status", lambda x: (x == "Delayed").mean() * 100),
            avg_cost=("shipping_cost", "mean"),
            avg_transit=("transit_days", "mean"),
        )
        .round(2)
        .reset_index()
        .to_dict(orient="records")
    )

    category_summary = (
        filtered.groupby("item_category")
        .agg(
            shipments=("shipment_id", "count"),
            delay_rate=("status", lambda x: (x == "Delayed").mean() * 100),
            avg_cost=("shipping_cost", "mean"),
        )
        .round(2)
        .reset_index()
        .to_dict(orient="records")
    )

    overall_stats = {
        "total_shipments": int(len(filtered)),
        "delivered": int((filtered["status"] == "Delivered").sum()),
        "delayed": int((filtered["status"] == "Delayed").sum()),
        "failed_cancelled": int(filtered["status"].isin(["Cancelled", "Failed Delivery"]).sum()),
        "delivery_rate": round((filtered["status"] == "Delivered").mean() * 100, 2),
        "delay_rate": round((filtered["status"] == "Delayed").mean() * 100, 2),
        "avg_shipping_cost": round(filtered["shipping_cost"].mean(), 2),
        "avg_transit_days": round(filtered["transit_days"].mean(), 2),
    }

    # =========================
    # ANALYSIS OPTIONS
    # =========================
    analysis_type = st.selectbox(
        "Choose Analysis Type",
        [
            "Executive Summary",
            "Carrier Performance",
            "Category Analysis",
            "Risk Analysis",
            "Recommendations",
            "Custom Question",
        ],
    )

    custom_q = ""
    if analysis_type == "Custom Question":
        custom_q = st.text_area(
            "Ask anything about this shipment data:",
            placeholder="Which carrier should we reduce for electronics?",
        )

    # =========================
    # PROMPT BUILDER
    # =========================
    def build_prompt(question=None):
        base = f"""
You are a senior logistics data analyst.

Dataset Statistics:
{overall_stats}

Carrier Performance Data:
{carrier_summary}

Category Performance Data:
{category_summary}
"""
        if question:
            base += f"\nUser Question:\n{question}\n"
        else:
            base += f"\nProvide: {analysis_type}\n"

        return base

    # =========================
    # COHERE CALL
    # =========================
    if st.button("🚀 Generate AI Analysis"):
        if not COHERE_API_KEY:
            st.error("⚠️ Add COHERE_API_KEY to your .env file")
        else:
            try:
                import cohere

                with st.spinner("Analyzing with Cohere AI..."):
                    co = cohere.Client(COHERE_API_KEY)

                    final_prompt = build_prompt(custom_q if analysis_type == "Custom Question" else None)

                    response = co.chat(
                        model="command-r-plus-08-2024",
                        message=final_prompt,
                        temperature=0.3,
                        max_tokens=600,
                    )

                    # ✅ Correct way to read chat response
                    ai_text = response.text

                    st.markdown(
                        f'<div class="ai-response">{ai_text}</div>',
                        unsafe_allow_html=True,
                    )

            except Exception as e:
                st.error(f"Cohere API Error: {str(e)}")

    # =========================
    # DEBUG VIEW
    # =========================
    st.markdown("---")
    with st.expander("📊 View Data Sent to AI"):
        st.json(overall_stats)
        st.json(carrier_summary)
        st.json(category_summary)
# ════════════════════════════════════════
# TAB 8 — ABOUT
# ════════════════════════════════════════
with t8:
    st.markdown('<div class="section-title">📖 About LogiTrack</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="ibox ibox-olive">
        <div class="ibox-title olive">🚚 What is LogiTrack?</div>
        LogiTrack is an advanced logistics analytics platform built with Streamlit and Python.
        It provides real-time insights into shipment performance, carrier efficiency, delay patterns,
        and product distribution — powered by Excel data and optional AI analysis via Cohere.
    </div>
    <div class="ibox ibox-mustard">
        <div class="ibox-title mustard">📊 Dashboard Sections</div>
        <ul style="margin:6px 0 0 0;padding-left:18px;line-height:2.1">
            <li><b>📊 Summary</b> — KPI cards, smart insights, monthly trend</li>
            <li><b>📦 Shipments</b> — Status, cost analysis, SLA vs actual, day-of-week patterns</li>
            <li><b>🚚 Carriers</b> — Delivery %, delay %, avg days, cost, efficiency matrix, trend</li>
            <li><b>⚠️ Delays</b> — Reason frequency, carrier heatmap, monthly delay trend</li>
            <li><b>🏷️ Categories</b> — Distribution, product correlation map, risk matrix, category×carrier heatmap</li>
            <li><b>📍 Tracking View</b> — Per-shipment tracking with month filter, status banner, and monthly analytics</li>
            <li><b>🤖 AI Insights</b> — Natural language Q&A via Cohere (Command-R)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown("""
        <div class="ibox ibox-blue">
            <div class="ibox-title blue">🔑 Key Features</div>
            <ul style="margin:6px 0 0 0;padding-left:18px;line-height:2">
                <li>Real carrier names from Excel Dim_Carriers sheet</li>
                <li>Multi-filter sidebar (carrier, category, item, status, contract)</li>
                <li>Tracking number selectbox filtered by selected month</li>
                <li>Per-shipment tracking view with monthly performance visuals</li>
                <li>Product correlation / co-occurrence heatmap</li>
                <li>Category risk & efficiency scatter matrix</li>
                <li>Cohere AI with rule-based fallback</li>
                <li>API keys securely loaded from .env — never in frontend</li>
            </ul>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="ibox ibox-orange">
            <div class="ibox-title orange">📁 Data Model (Shipping_dataset.xlsx)</div>
            <ul style="margin:6px 0 0 0;padding-left:18px;line-height:2">
                <li><code>Fact_Shipments</code> — 32,921 records, core shipment facts</li>
                <li><code>Dim_Carriers</code> — 7 carriers with SLA & contract info</li>
                <li><code>Dim_Delays</code> — delay reason categories + impact scores</li>
                <li><code>Dim_Shipment_Delays</code> — delay days per shipment</li>
                <li><code>Dim_Calendar</code> — date dimension table</li>
            </ul>
        </div>""", unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown('<div class="footer">LogiTrack · Variance Insights · Built with Streamlit</div>', unsafe_allow_html=True)
