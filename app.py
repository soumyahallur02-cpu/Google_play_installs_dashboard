from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# --------------------------- PAGE CONFIG ---------------------------
st.set_page_config(
    page_title="PlayMetrics | Google Play Analytics",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "googleplaystore_merged_with_subjectivity.csv"
IST = ZoneInfo("Asia/Kolkata")

CATEGORY_TRANSLATIONS = {
    "BEAUTY": "सौंदर्य",
    "BUSINESS": "வணிகம்",
    "DATING": "Partnersuche",
}

# --------------------------- CUSTOM DESIGN ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
  --ink: #172033;
  --muted: #78839a;
  --line: #e8edf5;
  --violet: #7257f5;
  --cyan: #25b8c7;
  --surface: #ffffff;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp {
  background:
    radial-gradient(circle at 7% 0%, rgba(114,87,245,.09), transparent 26rem),
    radial-gradient(circle at 95% 5%, rgba(37,184,199,.08), transparent 25rem),
    #f5f7fc;
  color: var(--ink);
}
.block-container { padding-top: 1.35rem; padding-bottom: 3rem; max-width: 1500px; }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #171d35 0%, #202947 100%);
  border-right: 0;
}
[data-testid="stSidebar"] * { color: #eef1ff !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #c2c9df !important; }
[data-testid="stSidebar"] .stMultiSelect div,
[data-testid="stSidebar"] .stSelectbox div { color: #20263a !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #dce2f7 !important; }
[data-testid="stMetric"] {
  background: #fff;
  border: 1px solid #e9edf6;
  padding: 18px 20px;
  border-radius: 18px;
  box-shadow: 0 8px 24px rgba(34, 47, 84, .045);
}
[data-testid="stMetricLabel"] { color: #77829a !important; font-weight: 600; }
[data-testid="stMetricValue"] { color: #18223b !important; font-family: 'Manrope', sans-serif; font-weight: 800; }
[data-testid="stMetricDelta"] { font-size: .78rem; }
div[data-testid="stDataFrame"] {
  border: 1px solid #e8edf5;
  border-radius: 14px;
  overflow: hidden;
}
.stButton button {
  border-radius: 10px;
  border: 1px solid #deddfd;
  background: #f4f2ff;
  color: #6247e8;
  font-weight: 700;
}
.hero {
  background: linear-gradient(115deg, #202849 0%, #413a82 55%, #426e9a 100%);
  padding: 30px 34px;
  border-radius: 24px;
  color: white;
  box-shadow: 0 16px 40px rgba(36, 43, 91, .18);
  margin-bottom: 22px;
  position: relative;
  overflow: hidden;
}
.hero:after {
  content: ""; position: absolute; width: 250px; height: 250px;
  border: 1px solid rgba(255,255,255,.15); border-radius: 50%;
  right: 7%; top: -125px; box-shadow: 0 0 0 28px rgba(255,255,255,.035), 0 0 0 58px rgba(255,255,255,.025);
}
.hero-kicker { color: #c9c9ff; font-size: .75rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
.hero-title { font-family: 'Manrope', sans-serif; font-size: clamp(1.8rem, 3vw, 2.65rem); font-weight: 800; line-height: 1.15; margin: 8px 0; }
.hero-sub { color: #e0e5ff; font-size: .98rem; max-width: 720px; }
.section-heading {
  font-family: 'Manrope', sans-serif; font-weight: 800; font-size: 1.25rem;
  color: #202944; margin: 18px 0 4px;
}
.section-sub { color: #8490a6; font-size: .86rem; margin-bottom: 12px; }
.panel {
  background: white; border: 1px solid #e9edf5; border-radius: 18px;
  padding: 18px 20px; box-shadow: 0 8px 24px rgba(34,47,84,.035);
}
.pill {
  display: inline-block; padding: 6px 11px; border-radius: 99px;
  background: rgba(255,255,255,.13); border: 1px solid rgba(255,255,255,.22);
  color: #f4f5ff; font-size: .75rem; font-weight: 700; margin-right: 6px;
}
.notice {
  border-radius: 14px; padding: 14px 16px; background: #fff8e9;
  border: 1px solid #f5e5bd; color: #75551a; font-size: .9rem;
}
.small-muted { color: #8590a5; font-size: .78rem; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --------------------------- DATA ---------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path)
    required = {"App", "Category", "Reviews", "Installs", "Last Updated"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")

    data["Reviews"] = pd.to_numeric(data["Reviews"], errors="coerce")
    data["Installs"] = pd.to_numeric(data["Installs"], errors="coerce")
    data["Last Updated"] = pd.to_datetime(data["Last Updated"], errors="coerce")
    data["App"] = data["App"].astype("string").str.strip()
    data["Category"] = data["Category"].astype("string").str.strip().str.upper()

    valid = (
        data["App"].notna()
        & ~data["App"].str.contains("s", case=False, na=False)
        & ~data["App"].str.match(r"^[xyz]", case=False, na=False)
        & (data["Reviews"] > 500)
        & data["Installs"].notna()
        & data["Last Updated"].notna()
        & data["Category"].str.startswith(("E", "C", "B"), na=False)
    )
    return data.loc[valid].copy()

# --------------------------- SIDEBAR ---------------------------
with st.sidebar:
    st.markdown("## ◈ PlayMetrics")
    st.markdown("<p style='font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:#9da9cb!important;font-weight:700'>Analytics workspace</p>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### Dashboard controls")
    st.caption("Your requested filters are applied by default.")
    show_records = st.toggle("Show filtered app records", value=False)
    st.divider()
    st.markdown("### Filter rules")
    st.markdown("""
    - Reviews **greater than 500**
    - App name excludes **S**
    - App name does not start with **X / Y / Z**
    - Category begins with **E / C / B**
    """)
    st.divider()
    st.markdown("### Access window")
    st.markdown("**6:00 PM – 9:00 PM IST**")
    st.caption("The chart is hidden outside this window.")

# --------------------------- HEADER ---------------------------
now_ist = datetime.now(IST)
allowed_time = 18 <= now_ist.hour < 21

st.markdown(f"""
<div class="hero">
  <div class="hero-kicker">Google Play Store · Data intelligence</div>
  <div class="hero-title">App Install Trends</div>
  <div class="hero-sub">Explore category-wise install patterns, identify high-growth months, and monitor the apps that meet your selected data criteria.</div>
  <div style="margin-top:18px">
    <span class="pill">✦ Interactive analytics</span>
    <span class="pill">◷ {now_ist.strftime('%d %b %Y · %I:%M %p')} IST</span>
  </div>
</div>
""", unsafe_allow_html=True)

try:
    df = load_data(str(DATA_PATH))
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

if df.empty:
    st.warning("No rows match all the requested filters.")
    st.stop()

df["Month"] = df["Last Updated"].dt.to_period("M").dt.to_timestamp()
df["Display Category"] = df["Category"].map(CATEGORY_TRANSLATIONS).fillna(df["Category"])

monthly = (
    df.groupby(["Month", "Category", "Display Category"], as_index=False)
      .agg(Total_Installs=("Installs", "sum"), App_Count=("App", "nunique"))
      .sort_values(["Category", "Month"])
)
monthly["MoM_Growth"] = monthly.groupby("Category")["Total_Installs"].pct_change() * 100
monthly["High_Growth"] = monthly["MoM_Growth"] > 20

# --------------------------- STATUS + KPI CARDS ---------------------------
if allowed_time:
    st.success("Chart access is active · 6 PM–9 PM IST")
else:
    st.markdown(
        '<div class="notice">◷ <b>Chart currently locked.</b> The time-series visualization is displayed only between 6:00 PM and 9:00 PM IST. Your filtered summary and records remain available.</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-heading">At a glance</div><div class="section-sub">Snapshot of records matching every filter condition</div>', unsafe_allow_html=True)
total_installs = df["Installs"].sum()
peak_month = monthly.loc[monthly["Total_Installs"].idxmax(), "Month"].strftime("%b %Y") if not monthly.empty else "—"
growth_count = int(monthly["High_Growth"].sum())
k1, k2, k3, k4 = st.columns(4)
k1.metric("Matching app records", f"{len(df):,}", help="Rows remaining after all requested filters")
k2.metric("Install-count total", f"{total_installs:,.0f}", help="Sum of current install-count values")
k3.metric("Categories covered", f"{df['Category'].nunique():,}")
k4.metric("High-growth months", f"{growth_count:,}", help="Category-month observations with growth above 20%")

# --------------------------- CHART ---------------------------
st.markdown('<div class="section-heading">Install trend by category</div><div class="section-sub">Monthly aggregation · orange shading marks month-over-month growth above 20%</div>', unsafe_allow_html=True)

if allowed_time:
    categories = sorted(monthly["Category"].dropna().unique())
    palette = ["#7057F5", "#18A7B5", "#F19A38", "#E46D91", "#4C83D6", "#49A77B", "#9A6BD8", "#D16B4D"]
    fig = go.Figure()

    for idx, category in enumerate(categories):
        part = monthly[monthly["Category"] == category].sort_values("Month")
        label = part["Display Category"].iloc[0]
        color = palette[idx % len(palette)]

        # Shade only observations whose month-over-month growth exceeds 20%.
        highlight = part["Total_Installs"].where(part["High_Growth"])
        fig.add_trace(go.Scatter(
            x=part["Month"], y=highlight,
            mode="lines",
            line=dict(width=0, color=color),
            fill="tozeroy",
            fillcolor="rgba(245, 158, 55, 0.18)",
            name=f"{label} · >20% growth",
            showlegend=False,
            hoverinfo="skip",
            connectgaps=False,
        ))
        fig.add_trace(go.Scatter(
            x=part["Month"], y=part["Total_Installs"],
            mode="lines+markers",
            name=label,
            line=dict(color=color, width=3, shape="spline", smoothing=0.55),
            marker=dict(size=6, color="#ffffff", line=dict(color=color, width=2)),
            customdata=part[["MoM_Growth", "App_Count"]].fillna(0).to_numpy(),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "%{x|%b %Y}<br>"
                "Install count sum: <b>%{y:,.0f}</b><br>"
                "MoM change: %{customdata[0]:.2f}%<br>"
                "Apps: %{customdata[1]:.0f}<extra></extra>"
            ),
        ))

    fig.update_layout(
        height=590,
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        hovermode="x unified",
        margin=dict(l=18, r=20, t=24, b=20),
        font=dict(family="DM Sans, sans-serif", color="#59657d", size=12),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            bgcolor="rgba(255,255,255,0)", font=dict(size=11)
        ),
        xaxis=dict(
            title="Month (from Last Updated)",
            showgrid=False, linecolor="#e9edf5", tickfont=dict(color="#7d879b")
        ),
        yaxis=dict(
            title="Total installs (sum)",
            gridcolor="#edf0f6", zeroline=False, tickformat="~s",
            tickfont=dict(color="#7d879b")
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "displaylogo": False})
    st.markdown(
        '<div class="small-muted">Highlight key: orange shaded regions represent category-month totals with more than 20% growth compared with the preceding available month.</div>',
        unsafe_allow_html=True,
    )
else:
    st.info("The chart is intentionally not rendered outside the permitted time window.")

# --------------------------- DATA TABLES ---------------------------
left, right = st.columns([1.2, 1])
with left:
    st.markdown('<div class="section-heading">Category performance</div><div class="section-sub">Aggregated install totals for each category</div>', unsafe_allow_html=True)
    category_summary = (
        df.groupby(["Category", "Display Category"], as_index=False)
          .agg(Apps=("App", "nunique"), Total_Installs=("Installs", "sum"), Avg_Reviews=("Reviews", "mean"))
          .sort_values("Total_Installs", ascending=False)
    )
    category_summary["Avg_Reviews"] = category_summary["Avg_Reviews"].round(0).astype("Int64")
    category_summary = category_summary.rename(columns={
        "Display Category": "Graph label", "Total_Installs": "Install count sum",
        "Avg_Reviews": "Average reviews"
    })
    st.dataframe(category_summary[["Graph label", "Apps", "Install count sum", "Average reviews"]],
                 use_container_width=True, hide_index=True)

with right:
    st.markdown(
        '<div class="section-heading">Growth highlights</div>'
        '<div class="section-sub">Category-month periods above the 20% threshold</div>',
        unsafe_allow_html=True
    )

    # Select only required columns to prevent duplicate column names
    highlights = monthly.loc[
        monthly["High_Growth"],
        ["Month", "Display Category", "MoM_Growth", "Total_Installs"]
    ].copy()

    if highlights.empty:
        st.write("No qualifying growth periods were found.")
    else:
        highlights["Month"] = highlights["Month"].dt.strftime("%b %Y")
        highlights["MoM_Growth"] = highlights["MoM_Growth"].round(1)

        highlights = highlights.rename(columns={
            "Display Category": "Category",
            "MoM_Growth": "Growth (%)",
            "Total_Installs": "Install count sum"
        })

        highlights = highlights.sort_values(
            "Growth (%)", ascending=False
        )

        st.dataframe(
            highlights[
                ["Month", "Category", "Growth (%)", "Install count sum"]
            ],
            use_container_width=True,
            hide_index=True
        )

if show_records:
    st.markdown('<div class="section-heading">Filtered app records</div><div class="section-sub">Apps satisfying all name, category, review and date conditions</div>', unsafe_allow_html=True)
    st.dataframe(
        df[["App", "Category", "Reviews", "Installs", "Last Updated"]]
          .sort_values(["Category", "Last Updated"]),
        use_container_width=True, hide_index=True
    )

# --------------------------- FOOTNOTE ---------------------------
st.markdown("""
<div class="panel" style="margin-top:22px">
  <b style="color:#293451">Data interpretation note</b>
  <p style="color:#7c879d;font-size:.86rem;margin:7px 0 0">
  This dataset contains a current install-count snapshot and a <i>Last Updated</i> date,
  not a historical monthly install log. The chart groups current install counts by the
  app's last-updated month. It is therefore a proxy trend and should not be described
  as actual installs acquired during each month.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align:center;color:#9aa3b5;font-size:.75rem;padding:22px 0 0'>PLAYMETRICS · GOOGLE PLAY STORE ANALYTICS</div>",
    unsafe_allow_html=True,
)
