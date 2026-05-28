"""
wc-analytics · Page 1: Tournament Leaderboard
FIFA World Cup 2022 team rankings, filterable by any stat.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import render_header, hero, source_note, ACCENT, CSS
from utils.data_loader import (
    load_team_leaderboard, load_match_metadata, fmt, delta_str
)
from utils.flags import get_flag_url, team_with_flag

st.set_page_config(
    page_title="wc-analytics · Leaderboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Header ──────────────────────────────────────────────────────────────────
render_header(active="Leaderboard")

# ── Load data ───────────────────────────────────────────────────────────────
lb = load_team_leaderboard()
meta = load_match_metadata()

# ── Tournament KPIs ─────────────────────────────────────────────────────────
total_goals   = int(lb["total_goals"].sum()) if "total_goals" in lb.columns else 0
avg_xg        = round(lb["xg_per_game"].mean(), 2) if "xg_per_game" in lb.columns else 0
avg_hsr       = round(lb["rel_hsr_runs_per_game"].mean(), 1) if "rel_hsr_runs_per_game" in lb.columns else 0
avg_hsr_dist  = round(lb["rel_hsr_dist_m_per_game"].mean(), 0) if "rel_hsr_dist_m_per_game" in lb.columns else 0

hero(
    title="FIFA World Cup 2022 · Team Leaderboard",
    subtitle="GradientSports tracking + StatsBomb event data · 64 matches · 32 teams",
    kpis=[
        {"label": "Total Goals",      "value": total_goals,       "sub": f"{total_goals/64:.2f} per game"},
        {"label": "Avg xG / Game",    "value": avg_xg,            "sub": "StatsBomb model"},
        {"label": "Avg Rel. HSR/G",   "value": avg_hsr,           "sub": "≥80% vMax · ≥1 sec"},
        {"label": "Avg HSR Dist/G",   "value": f"{int(avg_hsr_dist)} m", "sub": "GradientSports tracking"},
    ]
)

# ── Stat selector ────────────────────────────────────────────────────────────
STAT_OPTIONS = {
    # Physical (tracking)
    "Rel. HSR Runs / Game":        ("rel_hsr_runs_per_game",      "Relative HSR Runs",   "tracking"),
    "Rel. HSR Distance / Game (m)":("rel_hsr_dist_m_per_game",    "Rel. HSR Distance (m)","tracking"),
    "Abs. HSR Runs / Game":        ("abs_hsr_runs_per_game",      "Absolute HSR Runs",   "tracking"),
    "Abs. HSR Distance / Game (m)":("abs_hsr_dist_m_per_game",    "Abs. HSR Distance (m)","tracking"),
    "Δ Rel vs Abs HSR Runs":       ("delta_hsr_runs_per_game",    "Δ Rel vs Abs HSR",    "tracking"),
    "Δ Rel vs Abs Distance (m)":   ("delta_hsr_dist_m_per_game",  "Δ Rel vs Abs Dist.",  "tracking"),
    "Avg Max Speed (km/h)":        ("avg_max_speed_kmh",          "Avg Max Speed",       "tracking"),
    # Tactical (event)
    "Goals / Game":                ("goals_per_game",             "Goals / Game",        "event"),
    "xG / Game":                   ("xg_per_game",                "xG / Game",           "event"),
    "Shots / Game":                ("shots_per_game",             "Shots / Game",        "event"),
    "Shots on Target / Game":      ("shots_on_target_per_game",   "Shots on Target",     "event"),
    "Possession %":                ("avg_possession_pct",         "Possession %",        "event"),
    "Pass Completion %":           ("avg_pass_completion_pct",    "Pass Completion %",   "event"),
    "Passes / Game":               ("passes_per_game",            "Passes / Game",       "event"),
    "Crosses / Game":              ("crosses_per_game",           "Crosses / Game",      "event"),
    "Through Balls / Game":        ("through_balls_per_game",     "Through Balls",       "event"),
    "Pressures / Game":            ("pressures_per_game",         "Pressures / Game",    "event"),
    "PPDA":                        ("avg_ppda",                   "PPDA",                "event"),
    "Interceptions / Game":        ("interceptions_per_game",     "Interceptions",       "event"),
    "Dribbles / Game":             ("dribbles_per_game",          "Dribbles / Game",     "event"),
}

col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    selected_stat = st.selectbox(
        "Sort leaderboard by",
        options=list(STAT_OPTIONS.keys()),
        index=0,
    )
with col2:
    top_n = st.selectbox("Show top", [10, 16, 32], index=0)
with col3:
    ascending = st.checkbox("Ascending", value=False)

stat_col, stat_label, stat_type = STAT_OPTIONS[selected_stat]

# ── Filter & sort ────────────────────────────────────────────────────────────
if stat_col not in lb.columns:
    st.warning(f"Column `{stat_col}` not found in leaderboard data.")
    st.stop()

lb_sorted = lb.dropna(subset=[stat_col]) \
              .sort_values(stat_col, ascending=ascending) \
              .head(top_n) \
              .reset_index(drop=True)

lb_sorted["rank"] = lb_sorted.index + 1

# ── Bar chart ─────────────────────────────────────────────────────────────────
st.markdown(f'<p class="section-title">Top {top_n} Teams · {selected_stat}</p>', unsafe_allow_html=True)

# Add flag URLs for chart hover
lb_sorted["flag_url"] = lb_sorted["team_name"].apply(lambda t: get_flag_url(t, size=40))

fig = px.bar(
    lb_sorted,
    x=stat_col,
    y="team_name",
    orientation="h",
    color_discrete_sequence=[ACCENT],
    text=stat_col,
    hover_data={"team_name": True, stat_col: ":.2f", "games_played": True},
)
fig.update_traces(
    texttemplate="%{x:.1f}",
    textposition="outside",
    marker_color=ACCENT,
)
fig.update_layout(
    height=max(300, top_n * 36),
    margin=dict(l=0, r=60, t=10, b=10),
    paper_bgcolor="white",
    plot_bgcolor="white",
    xaxis=dict(showgrid=True, gridcolor="#f3f4f6", title=""),
    yaxis=dict(
        title="",
        categoryorder="total ascending" if not ascending else "total descending",
        tickfont=dict(size=12),
    ),
    showlegend=False,
    font=dict(family="Inter, sans-serif", size=12),
)
st.plotly_chart(fig, use_container_width=True)

# ── Leaderboard table ─────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Full Rankings Table</p>', unsafe_allow_html=True)

# Build display dataframe
display_cols = [
    "rank", "team_name",
    "games_played",
    "rel_hsr_runs_per_game", "abs_hsr_runs_per_game", "delta_hsr_runs_per_game",
    "goals_per_game", "xg_per_game",
    "avg_possession_pct", "avg_pass_completion_pct",
    "pressures_per_game", "avg_ppda",
]
display_cols = [c for c in display_cols if c in lb_sorted.columns]
display_df = lb_sorted[display_cols].copy()

# Add flag HTML to team name
display_df["team_name"] = display_df["team_name"].apply(
    lambda t: f'<img src="{get_flag_url(t, 40)}" width="20" style="vertical-align:middle;border-radius:2px;margin-right:6px;">{t}'
)

# Rename for display
display_df = display_df.rename(columns={
    "rank":                    "#",
    "team_name":               "Team",
    "games_played":            "GP",
    "rel_hsr_runs_per_game":   "Rel. HSR/G",
    "abs_hsr_runs_per_game":   "Abs. HSR/G",
    "delta_hsr_runs_per_game": "Δ HSR",
    "goals_per_game":          "Goals/G",
    "xg_per_game":             "xG/G",
    "avg_possession_pct":      "Poss %",
    "avg_pass_completion_pct": "Pass %",
    "pressures_per_game":      "Press/G",
    "avg_ppda":                "PPDA",
})

# Render as HTML table with flags
table_html = display_df.to_html(
    escape=False,
    index=False,
    classes="gs-data-table",
    border=0,
)

st.markdown(f"""
<style>
.gs-data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    font-family: Inter, sans-serif;
}}
.gs-data-table th {{
    background: #f9fafb;
    color: #6b7280;
    font-weight: 500;
    padding: 8px 10px;
    text-align: left;
    border-bottom: 1px solid #e5e7eb;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    white-space: nowrap;
}}
.gs-data-table td {{
    padding: 8px 10px;
    border-bottom: 0.5px solid #f3f4f6;
    color: #111;
    white-space: nowrap;
}}
.gs-data-table tr:hover td {{ background: #f9fafb; }}
.gs-data-table tr:last-child td {{ border-bottom: none; }}
</style>
{table_html}
""", unsafe_allow_html=True)

source_note(
    tracking=stat_type == "tracking" or True,
    event=stat_type == "event" or True,
)

# ── Head to head scatter ───────────────────────────────────────────────────────
st.markdown('<p class="section-title">Rel. vs Abs. HSR — Your Metric vs Industry Standard</p>',
            unsafe_allow_html=True)
st.caption("Teams above the diagonal line are underrated by the industry 20 km/h threshold — your relative metric sees them working harder than the standard measure suggests.")

if "rel_hsr_runs_per_game" in lb.columns and "abs_hsr_runs_per_game" in lb.columns:
    scatter_df = lb.dropna(subset=["rel_hsr_runs_per_game", "abs_hsr_runs_per_game"]).copy()
    scatter_df["delta"] = scatter_df["rel_hsr_runs_per_game"] - scatter_df["abs_hsr_runs_per_game"]

    fig2 = px.scatter(
        scatter_df,
        x="abs_hsr_runs_per_game",
        y="rel_hsr_runs_per_game",
        text="team_name",
        color="delta",
        color_continuous_scale=["#dc2626", "#f3f4f6", ACCENT],
        color_continuous_midpoint=0,
        hover_data={"team_name": True, "delta": ":.1f"},
        labels={
            "abs_hsr_runs_per_game": "Absolute HSR Runs/Game (20 km/h threshold)",
            "rel_hsr_runs_per_game": "Relative HSR Runs/Game (≥80% vMax)",
            "delta": "Δ Rel vs Abs",
        }
    )

    # Diagonal reference line
    max_val = max(scatter_df["rel_hsr_runs_per_game"].max(),
                  scatter_df["abs_hsr_runs_per_game"].max()) * 1.05
    fig2.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val],
        mode="lines",
        line=dict(color="#d1d5db", width=1, dash="dash"),
        showlegend=False,
        hoverinfo="skip",
    ))

    fig2.update_traces(
        textposition="top center",
        marker=dict(size=10),
        selector=dict(mode="markers+text"),
    )
    fig2.update_layout(
        height=460,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=0, r=0, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
        yaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
        coloraxis_showscale=False,
        font=dict(family="Inter, sans-serif", size=11),
    )
    st.plotly_chart(fig2, use_container_width=True)

source_note()
