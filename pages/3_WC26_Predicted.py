"""
wc-analytics · Page 4: WC26 Predicted
Predicted WC26 team performance based on last 7 competitive games.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.theme import inject_css, page_header, kpi_row, source_note, plotly_base, GREEN, BLUE
from utils.data_loader import load_predicted_team_stats, load_data_coverage, fmt
from utils.flags import get_flag_url

st.set_page_config(
    page_title="wc-analytics · WC26 Predicted",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

with st.sidebar:
    st.markdown("## ⚽ wc-analytics")
    st.markdown("---")
    st.page_link("app.py",                        label="🏆 Leaderboard")
    st.page_link("pages/1_Team_Deep_Dive.py",     label="🔍 Team Deep Dive")
    st.page_link("pages/2_Player_Profile.py",     label="👤 Player Profile")
    st.page_link("pages/3_WC26_Predicted.py",     label="🔮 WC26 Predicted")
    st.markdown("---")
    st.caption("GradientSports tracking · StatsBomb open data")

# ── Load data ─────────────────────────────────────────────────────────────────
predicted = load_predicted_team_stats()
coverage  = load_data_coverage()

teams_with    = coverage[coverage["has_predicted_data"] == "yes"]["team_name"].tolist() if len(coverage) > 0 else []
teams_without = coverage[coverage["has_predicted_data"] == "no"]["team_name"].tolist()  if len(coverage) > 0 else []

page_header(
    "WC26 Predicted Team Performance",
    "Based on last 7 competitive games (excl. friendlies) · StatsBomb open data"
)

kpi_row([
    {"label": "Teams with data",    "value": len(teams_with),    "delta": "EURO24 · Copa24 · AFCON23"},
    {"label": "Teams without data", "value": len(teams_without), "delta": "AFC + some CONCACAF/UEFA"},
    {"label": "Good quality",       "value": len(predicted[predicted["data_quality"] == "good"])    if len(predicted) > 0 else 0, "delta": "≥5 games in sample"},
    {"label": "Limited quality",    "value": len(predicted[predicted["data_quality"] == "limited"]) if len(predicted) > 0 else 0, "delta": "3-4 games in sample"},
])

st.markdown("---")

# ── Coverage ──────────────────────────────────────────────────────────────────
st.markdown("### Data Coverage")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Teams with predicted data**")
    for team in sorted(teams_with):
        flag_url  = get_flag_url(team, size=40)
        flag_html = f'<img src="{flag_url}" width="16" style="vertical-align:middle;border-radius:2px;margin-right:6px;">' if flag_url else ""
        cov_row   = coverage[coverage["team_name"] == team]
        q = cov_row.iloc[0].get("data_quality", "") if len(cov_row) > 0 else ""
        badge = '<span class="gained-badge">good</span>' if q == "good" else '<span class="lost-badge">limited</span>'
        st.markdown(f'{flag_html}{team} {badge}', unsafe_allow_html=True)

with col2:
    st.markdown("**Teams without predicted data**")
    for team in sorted(teams_without):
        flag_url  = get_flag_url(team, size=40)
        flag_html = f'<img src="{flag_url}" width="16" style="vertical-align:middle;border-radius:2px;margin-right:6px;">' if flag_url else ""
        st.markdown(f'{flag_html}{team}', unsafe_allow_html=True)

st.markdown("---")

# ── Predicted leaderboard ─────────────────────────────────────────────────────
if len(predicted) == 0:
    st.warning("No predicted stats available.")
    st.stop()

st.markdown("### Predicted Leaderboard")

PRED_STATS = {
    "Pred. Goals / Game":       "pred_goals_per_game",
    "Pred. xG / Game":          "pred_xg_per_game",
    "Pred. Shots / Game":       "pred_shots_per_game",
    "Pred. Possession %":       "pred_possession_pct",
    "Pred. Pass Completion %":  "pred_pass_completion_pct",
    "Pred. Passes / Game":      "pred_passes_per_game",
    "Pred. Pressures / Game":   "pred_pressures_per_game",
    "Pred. PPDA":               "pred_ppda",
    "Pred. Crosses / Game":     "pred_crosses_per_game",
}

col1, col2 = st.columns([3, 1])
with col1:
    pred_stat = st.selectbox("Sort by", list(PRED_STATS.keys()))
with col2:
    pred_n = st.selectbox("Show top", [10, 20, 32], index=0)

stat_col  = PRED_STATS[pred_stat]
team_col  = "team" if "team" in predicted.columns else "team_name"
ascending = pred_stat == "Pred. PPDA"

if stat_col in predicted.columns:
    pred_sorted = (
        predicted.dropna(subset=[stat_col])
        .sort_values(stat_col, ascending=ascending)
        .head(pred_n)
        .reset_index(drop=True)
    )

    fig = px.bar(
        pred_sorted, x=stat_col, y=team_col,
        orientation="h",
        color_discrete_sequence=[BLUE],
        text=stat_col,
    )
    fig.update_traces(texttemplate="%{x:.2f}", textposition="outside")
    fig.update_layout(
        **plotly_base(height=max(300, pred_n * 34)),
        xaxis=dict(showgrid=True, gridcolor="#eeeeec", title=""),
        yaxis=dict(title="", categoryorder="total ascending"),
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")

    # Table
    st.markdown("### Full Predicted Stats Table")
    display_cols = [team_col, "games_in_sample", "data_quality", "competitions_used"] + [
        c for c in PRED_STATS.values() if c in pred_sorted.columns
    ]
    display_df = pred_sorted[[c for c in display_cols if c in pred_sorted.columns]].copy()
    display_df[team_col] = display_df[team_col].apply(
        lambda t: f'<img src="{get_flag_url(str(t), 40)}" width="16" style="vertical-align:middle;border-radius:2px;margin-right:6px;">{t}'
    )
    display_df = display_df.rename(columns={
        team_col:                    "Team",
        "games_in_sample":           "Games",
        "data_quality":              "Quality",
        "competitions_used":         "Competitions",
        "pred_goals_per_game":       "Goals/G",
        "pred_xg_per_game":          "xG/G",
        "pred_shots_per_game":       "Shots/G",
        "pred_possession_pct":       "Poss %",
        "pred_pass_completion_pct":  "Pass %",
        "pred_passes_per_game":      "Passes/G",
        "pred_pressures_per_game":   "Press/G",
        "pred_ppda":                 "PPDA",
        "pred_crosses_per_game":     "Cross/G",
    })
    table_html = display_df.to_html(escape=False, index=False, classes="gs-data-table", border=0)
    st.markdown(f"""
    <style>
    .gs-data-table {{
        width:100%;border-collapse:collapse;font-size:13px;
        font-family:Inter,sans-serif;background:#fff;
    }}
    .gs-data-table th {{
        background:#f9fafb;color:#888;font-weight:500;
        padding:8px 12px;text-align:left;border-bottom:1px solid #e5e5e3;
        font-size:11px;text-transform:uppercase;letter-spacing:0.05em;white-space:nowrap;
    }}
    .gs-data-table td {{
        padding:8px 12px;border-bottom:0.5px solid #f3f4f6;color:#111;white-space:nowrap;
    }}
    .gs-data-table tr:hover td {{ background:#fafaf9; }}
    .gs-data-table tr:last-child td {{ border-bottom:none; }}
    </style>
    {table_html}
    """, unsafe_allow_html=True)

source_note(tracking=False, event=True)
st.caption(f"Teams without predicted data: {', '.join(teams_without)}")
