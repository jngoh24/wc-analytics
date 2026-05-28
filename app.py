"""
wc-analytics · Page 1: Tournament Leaderboard
FIFA World Cup 2022 team rankings, filterable by any stat.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import inject_css, page_header, kpi_row, source_note, plotly_base, ACCENT, GREEN, RED, BLUE
from utils.data_loader import load_team_leaderboard, fmt, delta_str
from utils.flags import get_flag_url

st.set_page_config(
    page_title="wc-analytics · Leaderboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ wc-analytics")
    st.markdown("---")
    st.page_link("app.py",                        label="🏆 Leaderboard",    )
    st.page_link("pages/1_Team_Deep_Dive.py",     label="🔍 Team Deep Dive", )
    st.page_link("pages/2_Player_Profile.py",     label="👤 Player Profile", )
    st.page_link("pages/3_WC26_Predicted.py",     label="🔮 WC26 Predicted", )
    st.markdown("---")
    st.markdown('<p class="eyebrow">Data Sources</p>', unsafe_allow_html=True)
    st.caption("GradientSports tracking · StatsBomb open data")
    st.caption("FIFA World Cup 2022 · 64 matches · 32 teams")

# ── Page header ───────────────────────────────────────────────────────────────
page_header(
    "FIFA World Cup 2022 · Team Leaderboard",
    "Powered by GradientSports tracking + StatsBomb event data"
)

# ── Load data ─────────────────────────────────────────────────────────────────
lb = load_team_leaderboard()

# ── Tournament KPIs ───────────────────────────────────────────────────────────
total_goals  = int(lb["total_goals"].sum())          if "total_goals" in lb.columns else 0
avg_xg       = round(lb["xg_per_game"].mean(), 2)    if "xg_per_game" in lb.columns else 0
avg_hsr      = round(lb["rel_hsr_runs_per_game"].mean(), 1) if "rel_hsr_runs_per_game" in lb.columns else 0
avg_hsr_dist = round(lb["rel_hsr_dist_m_per_game"].mean(), 0) if "rel_hsr_dist_m_per_game" in lb.columns else 0

kpi_row([
    {"label": "Total Goals",    "value": total_goals,          "delta": f"{total_goals/64:.2f}/game"},
    {"label": "Avg xG / Game",  "value": avg_xg,               "delta": "StatsBomb model"},
    {"label": "Avg Rel HSR/G",  "value": avg_hsr,              "delta": "≥80% vMax · ≥1 sec"},
    {"label": "Avg HSR Dist/G", "value": f"{int(avg_hsr_dist)} m", "delta": "GradientSports tracking"},
])

st.markdown("---")

# ── Stat selector ─────────────────────────────────────────────────────────────
STAT_OPTIONS = {
    # Tracking — physical
    "Rel. HSR Runs / Game":         ("rel_hsr_runs_per_game",     "tracking"),
    "Rel. HSR Distance / Game (m)": ("rel_hsr_dist_m_per_game",   "tracking"),
    "Abs. HSR Runs / Game":         ("abs_hsr_runs_per_game",     "tracking"),
    "Abs. HSR Distance / Game (m)": ("abs_hsr_dist_m_per_game",   "tracking"),
    "Δ Rel vs Abs HSR Runs":        ("delta_hsr_runs_per_game",   "tracking"),
    "Δ Rel vs Abs Distance (m)":    ("delta_hsr_dist_m_per_game", "tracking"),
    # Event — tactical
    "Goals / Game":                 ("goals_per_game",            "event"),
    "xG / Game":                    ("xg_per_game",               "event"),
    "Shots / Game":                 ("shots_per_game",            "event"),
    "Shots on Target / Game":       ("shots_on_target_per_game",  "event"),
    "Possession %":                 ("avg_possession_pct",        "event"),
    "Pass Completion %":            ("avg_pass_completion_pct",   "event"),
    "Passes / Game":                ("passes_per_game",           "event"),
    "Crosses / Game":               ("crosses_per_game",          "event"),
    "Through Balls / Game":         ("through_balls_per_game",    "event"),
    "Pressures / Game":             ("pressures_per_game",        "event"),
    "PPDA":                         ("avg_ppda",                  "event"),
    "Interceptions / Game":         ("interceptions_per_game",    "event"),
    "Dribbles / Game":              ("dribbles_per_game",         "event"),
}

col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    selected_stat = st.selectbox("Sort leaderboard by", list(STAT_OPTIONS.keys()), index=0)
with col2:
    top_n = st.selectbox("Show top", [10, 16, 32], index=0)
with col3:
    ascending = st.checkbox("Ascending", value=False)

stat_col, stat_type = STAT_OPTIONS[selected_stat]

if stat_col not in lb.columns:
    st.warning(f"Column `{stat_col}` not found in data.")
    st.stop()

lb_sorted = (
    lb.dropna(subset=[stat_col])
    .sort_values(stat_col, ascending=ascending)
    .head(top_n)
    .reset_index(drop=True)
)
lb_sorted["rank"] = lb_sorted.index + 1

# ── Bar chart ─────────────────────────────────────────────────────────────────
st.markdown(f"### Top {top_n} Teams · {selected_stat}")

color = GREEN if stat_type == "tracking" else BLUE

fig = px.bar(
    lb_sorted,
    x=stat_col,
    y="team_name",
    orientation="h",
    color_discrete_sequence=[color],
    text=stat_col,
)
fig.update_traces(texttemplate="%{x:.1f}", textposition="outside")
fig.update_layout(
    height=max(300, top_n * 36),
    paper_bgcolor="#f7f7f5",
    plot_bgcolor="#ffffff",
    font=dict(family="Inter, sans-serif", size=12, color="#666666"),
    margin=dict(l=0, r=60, t=10, b=10),
    xaxis=dict(showgrid=True, gridcolor="#eeeeec", title=""),
    yaxis=dict(title="", categoryorder="total ascending" if not ascending else "total descending"),
    showlegend=False,
)
st.plotly_chart(fig, width="stretch")

# ── Leaderboard table ─────────────────────────────────────────────────────────
st.markdown("### Full Rankings Table")

display_cols = [
    "rank", "team_name", "games_played",
    "rel_hsr_runs_per_game", "abs_hsr_runs_per_game", "delta_hsr_runs_per_game",
    "goals_per_game", "xg_per_game",
    "avg_possession_pct", "avg_pass_completion_pct",
    "pressures_per_game", "avg_ppda",
]
display_cols = [c for c in display_cols if c in lb_sorted.columns]
display_df = lb_sorted[display_cols].copy()

# Add flags
display_df["team_name"] = display_df["team_name"].apply(
    lambda t: f'<img src="{get_flag_url(t, 40)}" width="20" style="vertical-align:middle;border-radius:2px;margin-right:6px;">{t}'
)

display_df = display_df.rename(columns={
    "rank":                    "#",
    "team_name":               "Team",
    "games_played":            "GP",
    "rel_hsr_runs_per_game":   "Rel HSR/G",
    "abs_hsr_runs_per_game":   "Abs HSR/G",
    "delta_hsr_runs_per_game": "Δ HSR",
    "goals_per_game":          "Goals/G",
    "xg_per_game":             "xG/G",
    "avg_possession_pct":      "Poss %",
    "avg_pass_completion_pct": "Pass %",
    "pressures_per_game":      "Press/G",
    "avg_ppda":                "PPDA",
})

table_html = display_df.to_html(escape=False, index=False, classes="gs-data-table", border=0)
st.markdown(f"""
<style>
.gs-data-table {{
    width: 100%; border-collapse: collapse;
    font-size: 13px; font-family: Inter, sans-serif;
    background: #ffffff;
}}
.gs-data-table th {{
    background: #f9fafb; color: #888; font-weight: 500;
    padding: 8px 12px; text-align: left;
    border-bottom: 1px solid #e5e5e3;
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;
    white-space: nowrap;
}}
.gs-data-table td {{
    padding: 8px 12px; border-bottom: 0.5px solid #f3f4f6;
    color: #111; white-space: nowrap;
}}
.gs-data-table tr:hover td {{ background: #fafaf9; }}
.gs-data-table tr:last-child td {{ border-bottom: none; }}
</style>
{table_html}
""", unsafe_allow_html=True)

source_note(tracking=True, event=True)

# ── Rel vs Abs scatter ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Your Metric vs Industry Standard")
st.caption(
    "Teams **above** the diagonal are underrated by the flat 20 km/h threshold — "
    "your relative metric sees them working harder than the standard measure suggests."
)

if "rel_hsr_runs_per_game" in lb.columns and "abs_hsr_runs_per_game" in lb.columns:
    scatter_df = lb.dropna(subset=["rel_hsr_runs_per_game", "abs_hsr_runs_per_game"]).copy()
    scatter_df["delta"] = scatter_df["rel_hsr_runs_per_game"] - scatter_df["abs_hsr_runs_per_game"]

    fig2 = px.scatter(
        scatter_df,
        x="abs_hsr_runs_per_game",
        y="rel_hsr_runs_per_game",
        text="team_name",
        color="delta",
        color_continuous_scale=["#c0392b", "#f3f4f6", "#1a6b3c"],
        color_continuous_midpoint=0,
        labels={
            "abs_hsr_runs_per_game": "Absolute HSR Runs/Game (20 km/h)",
            "rel_hsr_runs_per_game": "Relative HSR Runs/Game (≥80% vMax)",
            "delta": "Δ Rel vs Abs",
        }
    )
    max_val = max(
        scatter_df["rel_hsr_runs_per_game"].max(),
        scatter_df["abs_hsr_runs_per_game"].max()
    ) * 1.05
    fig2.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val],
        mode="lines",
        line=dict(color="#e5e5e3", width=1, dash="dash"),
        showlegend=False, hoverinfo="skip",
    ))
    fig2.update_traces(
        textposition="top center",
        marker=dict(size=10),
        selector=dict(mode="markers+text"),
    )
    fig2.update_layout(
        **plotly_base(height=480),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig2, width="stretch")

source_note()
