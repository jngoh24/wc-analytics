"""
wc-analytics · Page 4: WC26 Predicted
Predicted WC26 team performance based on last 7 competitive games.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.theme import render_header, hero, source_note, ACCENT
from utils.data_loader import load_predicted_team_stats, load_data_coverage, fmt
from utils.flags import get_flag_url

st.set_page_config(
    page_title="wc-analytics · WC26 Predicted",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_header(active="Predicted")

# ── Load data ────────────────────────────────────────────────────────────────
predicted = load_predicted_team_stats()
coverage  = load_data_coverage()

teams_with_data    = coverage[coverage["has_predicted_data"] == "yes"]["team_name"].tolist() if len(coverage) > 0 else []
teams_without_data = coverage[coverage["has_predicted_data"] == "no"]["team_name"].tolist()  if len(coverage) > 0 else []

hero(
    title="WC26 Predicted Team Performance",
    subtitle=f"Based on last 7 competitive games (excl. friendlies) · StatsBomb open data · {len(teams_with_data)}/48 teams covered",
    kpis=[
        {"label": "Teams with data",    "value": len(teams_with_data),    "sub": "EURO24 · Copa24 · AFCON23"},
        {"label": "Teams without data", "value": len(teams_without_data), "sub": "AFC + some CONCACAF/UEFA", "negative": True},
        {"label": "Good quality",       "value": len(predicted[predicted["data_quality"] == "good"])  if len(predicted) > 0 else 0, "sub": "≥5 games in sample"},
        {"label": "Limited quality",    "value": len(predicted[predicted["data_quality"] == "limited"]) if len(predicted) > 0 else 0, "sub": "3-4 games in sample", "negative": True},
    ]
)

# ── Data coverage map ─────────────────────────────────────────────────────────
st.markdown('<p class="section-title">Data Coverage</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Teams with predicted data**")
    for team in sorted(teams_with_data):
        flag_url = get_flag_url(team, size=40)
        flag_html = f'<img src="{flag_url}" width="18" style="vertical-align:middle;border-radius:2px;margin-right:6px;">' if flag_url else ""
        q = coverage[coverage["team_name"] == team]["data_quality"].values[0] if len(coverage[coverage["team_name"] == team]) > 0 else ""
        badge = f'<span class="badge-tracking">good</span>' if q == "good" else f'<span class="badge-event">limited</span>'
        st.markdown(f'{flag_html}{team} {badge}', unsafe_allow_html=True)

with col2:
    st.markdown("**Teams without predicted data**")
    for team in sorted(teams_without_data):
        flag_url = get_flag_url(team, size=40)
        flag_html = f'<img src="{flag_url}" width="18" style="vertical-align:middle;border-radius:2px;margin-right:6px;">' if flag_url else ""
        st.markdown(f'{flag_html}{team} <span class="badge-none">no data</span>', unsafe_allow_html=True)

# ── Predicted leaderboard ─────────────────────────────────────────────────────
if len(predicted) == 0:
    st.warning("No predicted stats available.")
    st.stop()

st.markdown('<p class="section-title">Predicted Leaderboard</p>', unsafe_allow_html=True)

PRED_STATS = {
    "Pred. Goals / Game":      "pred_goals_per_game",
    "Pred. xG / Game":         "pred_xg_per_game",
    "Pred. Shots / Game":      "pred_shots_per_game",
    "Pred. Possession %":      "pred_possession_pct",
    "Pred. Pass Completion %": "pred_pass_completion_pct",
    "Pred. Passes / Game":     "pred_passes_per_game",
    "Pred. Pressures / Game":  "pred_pressures_per_game",
    "Pred. PPDA":              "pred_ppda",
    "Pred. Crosses / Game":    "pred_crosses_per_game",
}

col1, col2 = st.columns([3, 1])
with col1:
    pred_stat = st.selectbox("Sort predicted leaderboard by", list(PRED_STATS.keys()))
with col2:
    pred_n = st.selectbox("Show top", [10, 20, 32], index=0)

stat_col = PRED_STATS[pred_stat]

if stat_col in predicted.columns:
    pred_sorted = predicted.dropna(subset=[stat_col]) \
                           .sort_values(stat_col, ascending=(pred_stat == "Pred. PPDA")) \
                           .head(pred_n) \
                           .reset_index(drop=True)

    # Team name column in predicted may be "team" or "team_name"
    team_col = "team" if "team" in pred_sorted.columns else "team_name"

    fig = px.bar(
        pred_sorted,
        x=stat_col,
        y=team_col,
        orientation="h",
        color_discrete_sequence=[ACCENT],
        text=stat_col,
    )
    fig.update_traces(texttemplate="%{x:.2f}", textposition="outside")
    fig.update_layout(
        height=max(300, pred_n * 34),
        margin=dict(l=0, r=60, t=10, b=10),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#f3f4f6", title=""),
        yaxis=dict(title="", categoryorder="total ascending"),
        showlegend=False,
        font=dict(family="Inter, sans-serif", size=12),
    )
    st.plotly_chart(fig, width="stretch")

    # Full table
    st.markdown('<p class="section-title">Full Predicted Stats Table</p>', unsafe_allow_html=True)

    display_cols = [team_col, "games_in_sample", "data_quality", "competitions_used"] + [
        c for c in PRED_STATS.values() if c in pred_sorted.columns
    ]
    display_df = pred_sorted[display_cols].copy()

    # Add flags to team name
    display_df[team_col] = display_df[team_col].apply(
        lambda t: f'<img src="{get_flag_url(str(t), 40)}" width="18" style="vertical-align:middle;border-radius:2px;margin-right:6px;">{t}'
    )

    display_df = display_df.rename(columns={
        team_col:             "Team",
        "games_in_sample":    "Games",
        "data_quality":       "Quality",
        "competitions_used":  "Competitions",
        "pred_goals_per_game":          "Goals/G",
        "pred_xg_per_game":             "xG/G",
        "pred_shots_per_game":          "Shots/G",
        "pred_possession_pct":          "Poss %",
        "pred_pass_completion_pct":     "Pass %",
        "pred_passes_per_game":         "Passes/G",
        "pred_pressures_per_game":      "Press/G",
        "pred_ppda":                    "PPDA",
        "pred_crosses_per_game":        "Cross/G",
    })

    table_html = display_df.to_html(escape=False, index=False, classes="gs-data-table", border=0)
    st.markdown(f"""
    <style>
    .gs-data-table {{
        width: 100%; border-collapse: collapse;
        font-size: 13px; font-family: Inter, sans-serif;
    }}
    .gs-data-table th {{
        background: #f9fafb; color: #6b7280; font-weight: 500;
        padding: 8px 10px; text-align: left;
        border-bottom: 1px solid #e5e7eb;
        font-size: 11px; text-transform: uppercase; letter-spacing: 0.4px;
        white-space: nowrap;
    }}
    .gs-data-table td {{
        padding: 8px 10px; border-bottom: 0.5px solid #f3f4f6;
        color: #111; white-space: nowrap;
    }}
    .gs-data-table tr:hover td {{ background: #f9fafb; }}
    .gs-data-table tr:last-child td {{ border-bottom: none; }}
    </style>
    {table_html}
    """, unsafe_allow_html=True)

source_note(tracking=False, event=True)

st.markdown(f"""
<p class="gs-source">
⚠️ Teams without predicted data: {", ".join(teams_without_data)}<br>
These teams did not appear in EURO 2024, Copa América 2024, or AFCON 2023.
WC26 live stats will populate as games are played.
</p>
""", unsafe_allow_html=True)
