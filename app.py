import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os

st.set_page_config(
    page_title="ED Performance Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

PRIMARY = "#002664"
SECONDARY = "#C00000"
ACCENT_GREEN = "#00843D"
ACCENT_AMBER = "#F7931E"
BG_LIGHT = "#F5F5F5"
TEXT_DARK = "#1A1A2E"

st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #002664;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #002664;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #002664;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .alert-red { border-left-color: #C00000 !important; }
    .alert-red .metric-value { color: #C00000 !important; }
    .alert-green { border-left-color: #00843D !important; }
    .alert-green .metric-value { color: #00843D !important; }
    div[data-testid="stSidebar"] {
        background-color: #002664;
    }
    div[data-testid="stSidebar"] .stMarkdown { color: white; }
    div[data-testid="stSidebar"] label { color: white !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "data", "ed_visits.csv")
    if not os.path.exists(data_path):
        data_path = os.path.join(os.path.dirname(__file__), "ed_visits.csv")
    if not os.path.exists(data_path):
        st.error("Data file not found. Run `python data/generate_data.py` first.")
        st.stop()
    df = pd.read_csv(data_path)
    df["arrival_datetime"] = pd.to_datetime(df["arrival_datetime"])
    df["arrival_date"] = pd.to_datetime(df["arrival_date"])
    return df


def render_metric(label, value, suffix="", alert_class=""):
    css_class = f"metric-card {alert_class}"
    st.markdown(f"""
    <div class="{css_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}{suffix}</div>
    </div>
    """, unsafe_allow_html=True)


def page_overview(df):
    st.markdown('<div class="main-header">Executive Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Statewide Health — Emergency Department Performance Summary</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric("Total ED Visits", f"{len(df):,}")
    with c2:
        render_metric("Median Wait", f"{df['wait_time_minutes'].median():.0f}", " min")
    with c3:
        render_metric("Median LOS", f"{df['los_minutes'].median():.0f}", " min")
    with c4:
        compliance = df["four_hour_compliant"].mean()
        alert = "alert-green" if compliance >= 0.9 else "alert-red"
        render_metric("4-Hour Compliance", f"{compliance:.1%}", alert_class=alert)
    with c5:
        triage_comp = df["seen_within_target"].mean()
        alert = "alert-green" if triage_comp >= 0.8 else "alert-red"
        render_metric("Triage Target", f"{triage_comp:.1%}", alert_class=alert)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        monthly = df.groupby("arrival_month").agg(
            visits=("visit_id", "count"),
            compliance=("four_hour_compliant", "mean"),
            wait=("wait_time_minutes", "median")
        ).reset_index()
        monthly = monthly.sort_values("arrival_month")

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=monthly["arrival_month"], y=monthly["visits"],
                   name="ED Visits", marker_color=PRIMARY, opacity=0.7),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=monthly["arrival_month"], y=monthly["compliance"] * 100,
                       name="4-Hr Compliance %", line=dict(color=SECONDARY, width=3),
                       mode="lines+markers"),
            secondary_y=True
        )
        fig.update_layout(
            title="Monthly ED Volume & 4-Hour Compliance",
            template="plotly_white",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(t=60, b=40)
        )
        fig.update_yaxes(title_text="ED Visits", secondary_y=False)
        fig.update_yaxes(title_text="Compliance %", secondary_y=True, range=[50, 100])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        hosp_perf = df.groupby("hospital").agg(
            compliance=("four_hour_compliant", "mean"),
            median_wait=("wait_time_minutes", "median"),
            visits=("visit_id", "count")
        ).reset_index().sort_values("compliance", ascending=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=hosp_perf["hospital"],
            x=hosp_perf["compliance"] * 100,
            orientation="h",
            marker_color=[SECONDARY if v < 0.8 else ACCENT_GREEN for v in hosp_perf["compliance"]],
            text=[f"{v:.1%}" for v in hosp_perf["compliance"]],
            textposition="auto"
        ))
        fig.add_vline(x=90, line_dash="dash", line_color="gray", annotation_text="Target 90%")
        fig.update_layout(
            title="4-Hour Compliance by Hospital",
            xaxis_title="Compliance %",
            template="plotly_white",
            height=400,
            margin=dict(t=60, b=40, l=200)
        )
        st.plotly_chart(fig, use_container_width=True)


def page_wait_times(df):
    st.markdown('<div class="main-header">Wait Time Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Triage-based wait time performance against targets</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        triage_stats = df.groupby(["triage_category", "triage_name"]).agg(
            median_wait=("wait_time_minutes", "median"),
            p90_wait=("wait_time_minutes", lambda x: np.percentile(x, 90)),
            compliance=("seen_within_target", "mean")
        ).reset_index().sort_values("triage_category")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[f"Cat {r['triage_category']}: {r['triage_name']}" for _, r in triage_stats.iterrows()],
            y=triage_stats["median_wait"],
            name="Median Wait",
            marker_color=PRIMARY
        ))
        fig.add_trace(go.Bar(
            x=[f"Cat {r['triage_category']}: {r['triage_name']}" for _, r in triage_stats.iterrows()],
            y=triage_stats["p90_wait"],
            name="90th Percentile",
            marker_color=SECONDARY,
            opacity=0.7
        ))
        fig.update_layout(
            title="Wait Times by Triage Category",
            yaxis_title="Minutes",
            template="plotly_white",
            barmode="group",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[f"Cat {r['triage_category']}: {r['triage_name']}" for _, r in triage_stats.iterrows()],
            y=triage_stats["compliance"] * 100,
            marker_color=[ACCENT_GREEN if v >= 0.8 else ACCENT_AMBER if v >= 0.6 else SECONDARY
                          for v in triage_stats["compliance"]],
            text=[f"{v:.0%}" for v in triage_stats["compliance"]],
            textposition="auto"
        ))
        fig.add_hline(y=80, line_dash="dash", line_color="gray", annotation_text="Target 80%")
        fig.update_layout(
            title="Triage Target Compliance Rate",
            yaxis_title="Compliance %",
            template="plotly_white",
            height=400,
            yaxis_range=[0, 100]
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Wait Time Heatmap — Hour of Day × Day of Week")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_data = df.groupby(["arrival_day", "arrival_hour"])["wait_time_minutes"].median().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="arrival_day", columns="arrival_hour", values="wait_time_minutes")
    heatmap_pivot = heatmap_pivot.reindex(day_order)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=[f"{h:02d}:00" for h in range(24)],
        y=day_order,
        colorscale=[[0, ACCENT_GREEN], [0.5, ACCENT_AMBER], [1, SECONDARY]],
        colorbar_title="Median Wait (min)",
        hovertemplate="Day: %{y}<br>Hour: %{x}<br>Wait: %{z:.0f} min<extra></extra>"
    ))
    fig.update_layout(
        template="plotly_white",
        height=350,
        margin=dict(t=20, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)


def page_flow(df):
    st.markdown('<div class="main-header">Patient Flow Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Arrival patterns, departure outcomes, and presenting complaints</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        hourly = df.groupby("arrival_hour")["visit_id"].count().reset_index()
        hourly.columns = ["hour", "visits"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[f"{h:02d}:00" for h in hourly["hour"]],
            y=hourly["visits"],
            marker_color=[PRIMARY if 8 <= h <= 20 else "#8896AB" for h in hourly["hour"]],
        ))
        fig.update_layout(
            title="ED Arrivals by Hour of Day",
            yaxis_title="Total Visits",
            template="plotly_white",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        dept = df["departure_status"].value_counts().reset_index()
        dept.columns = ["status", "count"]

        colors = [PRIMARY, SECONDARY, ACCENT_AMBER, "#8896AB", "#333", ACCENT_GREEN]
        fig = go.Figure(data=[go.Pie(
            labels=dept["status"],
            values=dept["count"],
            hole=0.4,
            marker_colors=colors[:len(dept)]
        )])
        fig.update_layout(
            title="Departure Status Distribution",
            template="plotly_white",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        complaints = df["presenting_complaint"].value_counts().head(10).reset_index()
        complaints.columns = ["complaint", "count"]

        fig = go.Figure(go.Bar(
            y=complaints["complaint"][::-1],
            x=complaints["count"][::-1],
            orientation="h",
            marker_color=PRIMARY
        ))
        fig.update_layout(
            title="Top 10 Presenting Complaints",
            xaxis_title="Visits",
            template="plotly_white",
            height=400,
            margin=dict(l=200)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        mode = df.groupby(["arrival_mode", "triage_name"])["visit_id"].count().reset_index()
        mode.columns = ["mode", "triage", "count"]

        fig = px.sunburst(
            mode, path=["mode", "triage"], values="count",
            color="mode",
            color_discrete_map={
                "Ambulance": SECONDARY,
                "Walk-in": PRIMARY,
                "Police/Corrections": ACCENT_AMBER,
                "Helicopter": ACCENT_GREEN,
                "Other": "#8896AB"
            }
        )
        fig.update_layout(
            title="Arrival Mode × Triage Category",
            template="plotly_white",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)


def page_predictions(df):
    st.markdown('<div class="main-header">Demand Forecasting</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Historical trends and projected ED demand</div>', unsafe_allow_html=True)

    daily = df.groupby("arrival_date").agg(
        visits=("visit_id", "count"),
        median_wait=("wait_time_minutes", "median"),
        compliance=("four_hour_compliant", "mean")
    ).reset_index()
    daily = daily.sort_values("arrival_date")
    daily["rolling_7d"] = daily["visits"].rolling(7, center=True).mean()
    daily["rolling_30d"] = daily["visits"].rolling(30, center=True).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["arrival_date"], y=daily["visits"],
        name="Daily Visits", mode="lines",
        line=dict(color=PRIMARY, width=0.5), opacity=0.3
    ))
    fig.add_trace(go.Scatter(
        x=daily["arrival_date"], y=daily["rolling_7d"],
        name="7-Day Average", mode="lines",
        line=dict(color=SECONDARY, width=2)
    ))
    fig.add_trace(go.Scatter(
        x=daily["arrival_date"], y=daily["rolling_30d"],
        name="30-Day Average", mode="lines",
        line=dict(color=ACCENT_GREEN, width=3)
    ))
    fig.update_layout(
        title="Daily ED Volume with Moving Averages",
        yaxis_title="ED Visits per Day",
        template="plotly_white",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        monthly_fy = df.groupby(["financial_year", "arrival_month"]).agg(
            visits=("visit_id", "count")
        ).reset_index()

        fig = px.line(
            monthly_fy, x="arrival_month", y="visits",
            color="financial_year",
            color_discrete_map={
                "FY2024-25": PRIMARY,
                "FY2025-26": SECONDARY,
            },
            markers=True
        )
        fig.update_layout(
            title="Year-over-Year Monthly Comparison",
            yaxis_title="ED Visits",
            template="plotly_white",
            height=400,
            legend_title="Financial Year"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow = df.groupby("arrival_day").agg(
            avg_visits=("visit_id", "count"),
            avg_wait=("wait_time_minutes", "median"),
            compliance=("four_hour_compliant", "mean")
        ).reset_index()
        n_weeks = df["arrival_date"].nunique() / 7
        dow["avg_daily"] = dow["avg_visits"] / n_weeks
        dow["day_order"] = dow["arrival_day"].map({d: i for i, d in enumerate(day_order)})
        dow = dow.sort_values("day_order")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=dow["arrival_day"], y=dow["avg_daily"],
            marker_color=[SECONDARY if d in ["Saturday", "Sunday"] else PRIMARY for d in dow["arrival_day"]],
            text=[f"{v:.0f}" for v in dow["avg_daily"]],
            textposition="auto"
        ))
        fig.update_layout(
            title="Average Daily Volume by Day of Week",
            yaxis_title="Avg Visits/Day",
            template="plotly_white",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)


def main():
    df = load_data()

    with st.sidebar:
        st.markdown("## 🏥 ED Dashboard")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            ["Overview", "Wait Times", "Patient Flow", "Demand Forecast"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### Filters")

        hospitals = st.multiselect(
            "Hospital",
            options=sorted(df["hospital"].unique()),
            default=sorted(df["hospital"].unique())
        )

        lhds = st.multiselect(
            "Local Health District",
            options=sorted(df["lhd"].unique()),
            default=sorted(df["lhd"].unique())
        )

        fy_options = sorted(df["financial_year"].unique())
        financial_year = st.multiselect(
            "Financial Year",
            options=fy_options,
            default=fy_options
        )

        triage_options = sorted(df["triage_category"].unique())
        triage = st.multiselect(
            "Triage Category",
            options=triage_options,
            default=triage_options,
            format_func=lambda x: f"Cat {x}: {df[df['triage_category']==x]['triage_name'].iloc[0]}"
        )

        st.markdown("---")
        st.markdown(
            "<div style='color: rgba(255,255,255,0.6); font-size: 0.75rem;'>"
            "Built with Claude Code<br>"
            "Data: Synthetic (150K records)<br>"
            "© 2026 Yuji Yamane"
            "</div>",
            unsafe_allow_html=True
        )

    mask = (
        df["hospital"].isin(hospitals) &
        df["lhd"].isin(lhds) &
        df["financial_year"].isin(financial_year) &
        df["triage_category"].isin(triage)
    )
    filtered = df[mask]

    if len(filtered) == 0:
        st.warning("No data matches the selected filters. Adjust filters in the sidebar.")
        return

    if page == "Overview":
        page_overview(filtered)
    elif page == "Wait Times":
        page_wait_times(filtered)
    elif page == "Patient Flow":
        page_flow(filtered)
    elif page == "Demand Forecast":
        page_predictions(filtered)


if __name__ == "__main__":
    main()