"""
wc-analytics · Page 3: Player Profile
Individual player physical + technical stats from WC22.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import inject_css, kpi_row, source_note, plotly_base, GREEN, BLUE, RED
from utils.data_loader import load_player_summary, load_player_match_log, fmt, delta_str
from utils.flags import get_flag_url

st.set_page_config(
    page_title="wc-analytics · Player",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# with st.sidebar:
#     st.markdown("## ⚽ wc-analytics")
#     st.markdown("---")
#     st.page_link("app.py",                        label="🏆 Leaderboard")
#     st.page_link("pages/1_Team_Deep_Dive.py",     label="🔍 Team Deep Dive")
#     st.page_link("pages/2_Player_Profile.py",     label="👤 Player Profile")
#     st.page_link("pages/3_WC26_Predicted.py",     label="🔮 WC26 Predicted")
#     st.markdown("---")
#     st.caption("GradientSports tracking · StatsBomb open data")

# ── Load data ─────────────────────────────────────────────────────────────────
players   = load_player_summary()
match_log = load_player_match_log()

# ── Filters ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    all_teams = sorted(players["team_name"].dropna().unique().tolist()) if "team_name" in players.columns else []
    selected_team = st.selectbox("Filter by team", ["All teams"] + all_teams)
with col2:
    all_positions = sorted(players["position"].dropna().unique().tolist()) if "position" in players.columns else []
    selected_pos  = st.selectbox("Filter by position", ["All positions"] + all_positions)

filtered = players.copy()
if selected_team != "All teams":
    filtered = filtered[filtered["team_name"] == selected_team]
if selected_pos != "All positions":
    filtered = filtered[filtered["position"] == selected_pos]

exclude_gk = st.checkbox("Exclude GKs from HSR rankings", value=True)
if exclude_gk and "position" in filtered.columns:
    filtered_hsr = filtered[filtered["position"] != "GK"]
else:
    filtered_hsr = filtered

with col3:
    player_options = sorted(filtered["player_name"].dropna().unique().tolist()) if "player_name" in filtered.columns else []
    if not player_options:
        st.warning("No players found for selected filters.")
        st.stop()
    selected_player = st.selectbox("Select player", player_options)

# ── Player data ───────────────────────────────────────────────────────────────
p = filtered[filtered["player_name"] == selected_player]
if p.empty:
    st.warning("Player not found.")
    st.stop()
p = p.iloc[0]

team_name = str(p.get("team_name", ""))
flag_url  = get_flag_url(team_name, size=80)
flag_html = f'<img src="{flag_url}" width="28" style="vertical-align:middle;border-radius:3px;margin-right:8px;">' if flag_url else ""

st.markdown(f"# {flag_html}{selected_player}", unsafe_allow_html=True)
st.markdown(
    f'<p class="kicker">{team_name} · {p.get("position", "")} · WC22 · {int(p.get("games_played", 0))} games</p>',
    unsafe_allow_html=True
)
st.markdown("---")

sb_available = str(p.get("sb_data_available", "False")).lower() == "true"
if not sb_available:
    st.info(
        "Technical stats (xG, passes, pressures) not available — no StatsBomb match found. "
        "Physical tracking stats are shown below.",
        icon="📭"
    )

kpi_row([
    {"label": "Personal vMax",  "value": fmt(p.get("personal_vmax_kmh"), suffix=" km/h"),
     "delta": "p99.9 of tracked frames"},
    {"label": "Rel. HSR/Game",  "value": fmt(p.get("avg_rel_hsr_runs_per_game")),
     "delta": "≥80% vMax · ≥1 sec"},
    {"label": "xG / Game",      "value": fmt(p.get("xg_per_game")),
     "delta": f"Total: {fmt(p.get('total_xg'))}"},
    {"label": "Δ Rel vs Abs",   "value": delta_str(p.get("avg_delta_hsr_runs_per_game")),
     "delta": "Your metric vs 20 km/h"},
])

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Physical Profile", "Technical Profile"])

with tab1:
    st.caption("Physical stats from GradientSports broadcast tracking · GKs excluded from HSR")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Personal vMax",        fmt(p.get("personal_vmax_kmh"), suffix=" km/h"))
        st.metric("Tournament Max Speed", fmt(p.get("tournament_max_speed_kmh"), suffix=" km/h"))
    with col2:
        st.metric("Rel. HSR Runs/Game",   fmt(p.get("avg_rel_hsr_runs_per_game")))
        st.metric("Rel. HSR Dist/Game",   fmt(p.get("avg_rel_hsr_dist_m_per_game"), suffix=" m"))
    with col3:
        st.metric("Abs. HSR Runs/Game",   fmt(p.get("avg_abs_hsr_runs_per_game")))
        st.metric("Avg Distance/Game",    fmt(p.get("avg_distance_m_per_game"), suffix=" m"))

    p_matches = match_log[match_log["player_name"] == selected_player] if "player_name" in match_log.columns else pd.DataFrame()
    if not p_matches.empty and "match_date" in p_matches.columns:
        p_matches = p_matches.sort_values("match_date")
        st.markdown("#### Rel. HSR Runs per match")
        fig = go.Figure()
        if "rel_hsr_runs" in p_matches.columns:
            fig.add_trace(go.Bar(x=p_matches["match_date"].astype(str), y=p_matches["rel_hsr_runs"],
                                 name="Rel. HSR", marker_color=GREEN))
        if "abs_hsr_runs" in p_matches.columns:
            fig.add_trace(go.Scatter(x=p_matches["match_date"].astype(str), y=p_matches["abs_hsr_runs"],
                                     mode="lines+markers", name="Abs. HSR (20 km/h)",
                                     line=dict(color="#aaa", width=1.5, dash="dot")))
        fig.update_layout(**plotly_base(height=260),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, width="stretch")

    st.markdown("#### Position peer comparison")
    pos = str(p.get("position", ""))
    if pos and "position" in players.columns and "avg_rel_hsr_runs_per_game" in players.columns:
        pos_peers = players[players["position"] == pos].copy()
        pos_peers["highlight"] = pos_peers["player_name"] == selected_player
        fig2 = px.histogram(pos_peers, x="avg_rel_hsr_runs_per_game",
                            color="highlight",
                            color_discrete_map={True: GREEN, False: "#e5e5e3"},
                            nbins=20,
                            labels={"avg_rel_hsr_runs_per_game": f"Rel. HSR Runs/Game ({pos})"})
        player_val = float(p.get("avg_rel_hsr_runs_per_game") or 0)
        if player_val > 0:
            fig2.add_vline(x=player_val, line_dash="dash", line_color=GREEN,
                           annotation_text=selected_player, annotation_position="top right")
        fig2.update_layout(**plotly_base(height=220), showlegend=False,
                           yaxis=dict(showgrid=True, gridcolor="#eeeeec", title="Players"))
        st.plotly_chart(fig2, width="stretch")

    source_note(tracking=True, event=False)

with tab2:
    if not sb_available:
        st.info("No StatsBomb data available for this player.", icon="📭")
    else:
        st.caption("Technical stats from StatsBomb open data · WC22 events")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Goals",          str(int(p.get("total_goals", 0))))
            st.metric("Goals / Game",   fmt(p.get("goals_per_game")))
            st.metric("xG / Game",      fmt(p.get("xg_per_game")))
            st.metric("Shots / Game",   fmt(p.get("shots_per_game")))
        with col2:
            st.metric("Total Passes",   str(int(p.get("total_passes", 0))))
            st.metric("Passes / Game",  fmt(p.get("passes_per_game"), 0))
            st.metric("Pass Comp. %",   fmt(p.get("avg_pass_completion_pct"), suffix="%"))
            st.metric("Crosses / Game", fmt(p.get("crosses_per_game")))
        with col3:
            st.metric("Pressures/Game", fmt(p.get("pressures_per_game"), 0))
            st.metric("Dribbles/Game",  fmt(p.get("dribbles_per_game")))
            st.metric("Interceptions/G",fmt(p.get("interceptions_per_game")))

        p_matches = match_log[match_log["player_name"] == selected_player] if "player_name" in match_log.columns else pd.DataFrame()
        if not p_matches.empty and "xg" in p_matches.columns and "match_date" in p_matches.columns:
            p_matches = p_matches.sort_values("match_date")
            st.markdown("#### xG per match")
            fig = px.bar(p_matches, x="match_date", y="xg",
                         color_discrete_sequence=[BLUE],
                         labels={"match_date": "Match", "xg": "xG"})
            fig.update_layout(**plotly_base(height=220))
            st.plotly_chart(fig, width="stretch")

    source_note(tracking=True, event=sb_available)
