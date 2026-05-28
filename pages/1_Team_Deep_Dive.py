"""
wc-analytics · Page 2: Team Deep Dive
Per-team WC22 stats with physical + tactical breakdowns and match-by-match trends.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import inject_css, page_header, kpi_row, source_note, plotly_base, ACCENT, GREEN, RED, BLUE
from utils.data_loader import (
    load_team_leaderboard, load_team_match_log,
    load_predicted_team_stats, load_data_coverage, fmt, delta_str
)
from utils.flags import get_flag_url

st.set_page_config(
    page_title="wc-analytics · Team",
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
lb        = load_team_leaderboard()
match_log = load_team_match_log()
predicted = load_predicted_team_stats()
coverage  = load_data_coverage()

# ── Team selector ─────────────────────────────────────────────────────────────
all_teams = sorted(lb["team_name"].dropna().unique().tolist())

col1, col2 = st.columns([2, 2])
with col1:
    team_a = st.selectbox("Select team", all_teams,
                          index=all_teams.index("France") if "France" in all_teams else 0)
with col2:
    compare_on = st.checkbox("Compare with another team")
    team_b = None
    if compare_on:
        remaining = [t for t in all_teams if t != team_a]
        team_b = st.selectbox("Compare with", remaining,
                               index=remaining.index("Argentina") if "Argentina" in remaining else 0)

# ── Page header ───────────────────────────────────────────────────────────────
flag_url  = get_flag_url(team_a, size=80)
flag_html = f'<img src="{flag_url}" width="28" style="vertical-align:middle;border-radius:3px;margin-right:8px;">' if flag_url else ""
team_data = lb[lb["team_name"] == team_a].iloc[0] if len(lb[lb["team_name"] == team_a]) > 0 else None

st.markdown(f"# {flag_html}{team_a}", unsafe_allow_html=True)
if team_data is not None:
    record = f"{int(team_data.get('wins',0))}W {int(team_data.get('draws',0))}D {int(team_data.get('losses',0))}L"
    st.markdown(f'<p class="kicker">FIFA World Cup 2022 · {record} · {int(team_data.get("games_played",0))} games</p>',
                unsafe_allow_html=True)
st.markdown("---")

# KPIs
if team_data is not None:
    kpi_row([
        {"label": "Goals / Game",    "value": fmt(team_data.get("goals_per_game")),
         "delta": f"Total: {int(team_data.get('total_goals', 0))}"},
        {"label": "xG / Game",       "value": fmt(team_data.get("xg_per_game"))},
        {"label": "Rel. HSR / Game", "value": fmt(team_data.get("rel_hsr_runs_per_game")),
         "delta": "≥80% vMax · ≥1 sec"},
        {"label": "Δ Rel vs Abs",    "value": delta_str(team_data.get("delta_hsr_runs_per_game")),
         "delta": "Your metric vs 20 km/h"},
    ])

st.markdown("---")

# ── Sub-tabs ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Physical", "Tactical", "WC26 Predicted"])

# ── TAB 1: Overview ───────────────────────────────────────────────────────────
with tab1:
    if team_data is None:
        st.warning("No data found for this team.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Possession %",    fmt(team_data.get("avg_possession_pct"), suffix="%"))
            st.metric("Pass Completion", fmt(team_data.get("avg_pass_completion_pct"), suffix="%"))
            st.metric("Passes / Game",   fmt(team_data.get("passes_per_game"), 0))
        with col2:
            st.metric("Shots / Game",          fmt(team_data.get("shots_per_game")))
            st.metric("Shots on Target / Game",fmt(team_data.get("shots_on_target_per_game")))
            st.metric("Crosses / Game",        fmt(team_data.get("crosses_per_game")))
        with col3:
            st.metric("Pressures / Game", fmt(team_data.get("pressures_per_game"), 0))
            st.metric("PPDA",             fmt(team_data.get("avg_ppda")))
            st.metric("Interceptions/G",  fmt(team_data.get("interceptions_per_game")))

        if compare_on and team_b:
            st.markdown("---")
            st.markdown(f"#### {team_a} vs {team_b}")
            tb_data = lb[lb["team_name"] == team_b]
            if len(tb_data) > 0:
                tb = tb_data.iloc[0]
                comp_stats  = ["goals_per_game", "xg_per_game", "avg_possession_pct",
                                "rel_hsr_runs_per_game", "pressures_per_game", "avg_ppda"]
                comp_labels = ["Goals/G", "xG/G", "Possession %",
                                "Rel. HSR/G", "Pressures/G", "PPDA"]
                fig = go.Figure()
                fig.add_trace(go.Bar(name=team_a, x=comp_labels,
                                     y=[round(float(team_data.get(c, 0) or 0), 2) for c in comp_stats],
                                     marker_color=GREEN))
                fig.add_trace(go.Bar(name=team_b, x=comp_labels,
                                     y=[round(float(tb.get(c, 0) or 0), 2) for c in comp_stats],
                                     marker_color=BLUE))
                fig.update_layout(**plotly_base(height=340), barmode="group",
                                  legend=dict(orientation="h", yanchor="bottom", y=1.02))
                st.plotly_chart(fig, width="stretch")

    source_note(tracking=True, event=True)

# ── TAB 2: Physical ───────────────────────────────────────────────────────────
with tab2:
    st.caption("Physical stats from GradientSports broadcast tracking data (25Hz)")
    team_matches = match_log[match_log["team_name"] == team_a].copy() if "team_name" in match_log.columns else pd.DataFrame()

    if team_data is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Avg Rel. HSR Runs/Game", fmt(team_data.get("rel_hsr_runs_per_game")))
            st.metric("Avg Rel. HSR Dist/Game", fmt(team_data.get("rel_hsr_dist_m_per_game"), suffix=" m"))
        with col2:
            st.metric("Avg Abs. HSR Runs/Game", fmt(team_data.get("abs_hsr_runs_per_game")))
            st.metric("Δ Rel vs Abs Runs/Game", delta_str(team_data.get("delta_hsr_runs_per_game")))

    if not team_matches.empty and "rel_hsr_runs" in team_matches.columns:
        team_matches = team_matches.sort_values("match_date")
        st.markdown("#### Rel. HSR Runs per match")
        fig = px.bar(team_matches, x="match_date", y="rel_hsr_runs",
                     color_discrete_sequence=[GREEN],
                     labels={"match_date": "Match Date", "rel_hsr_runs": "Rel. HSR Runs"})
        if "abs_hsr_runs" in team_matches.columns:
            fig.add_trace(go.Scatter(
                x=team_matches["match_date"], y=team_matches["abs_hsr_runs"],
                mode="lines+markers", name="Abs. HSR (20 km/h)",
                line=dict(color="#aaa", width=1.5, dash="dot"),
            ))
        fig.update_layout(**plotly_base(height=300),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, width="stretch")

    source_note(tracking=True, event=False)

# ── TAB 3: Tactical ───────────────────────────────────────────────────────────
with tab3:
    st.caption("Tactical stats from StatsBomb open data (event-level)")
    team_matches_sb = match_log[match_log["team_name"] == team_a].copy() if "team_name" in match_log.columns else pd.DataFrame()

    if not team_matches_sb.empty and "xg" in team_matches_sb.columns:
        team_matches_sb = team_matches_sb.sort_values("match_date")
        st.markdown("#### xG per match vs goals scored")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=team_matches_sb["match_date"].astype(str),
                             y=team_matches_sb["xg"], name="xG",
                             marker_color="#dbeafe"))
        if "goals" in team_matches_sb.columns:
            fig.add_trace(go.Scatter(
                x=team_matches_sb["match_date"].astype(str),
                y=team_matches_sb["goals"],
                mode="lines+markers", name="Goals",
                line=dict(color=GREEN, width=2), marker=dict(size=8, color=GREEN),
            ))
        fig.update_layout(**plotly_base(height=300),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, width="stretch")

        col1, col2 = st.columns(2)
        with col1:
            if "possession_pct" in team_matches_sb.columns:
                st.markdown("#### Possession % per match")
                fig = px.line(team_matches_sb, x="match_date", y="possession_pct",
                              markers=True, color_discrete_sequence=[BLUE])
                fig.add_hline(y=50, line_dash="dot", line_color="#e5e5e3")
                fig.update_layout(**plotly_base(height=220))
                st.plotly_chart(fig, width="stretch")
        with col2:
            if "pressures" in team_matches_sb.columns:
                st.markdown("#### Pressures per match")
                fig = px.bar(team_matches_sb, x="match_date", y="pressures",
                             color_discrete_sequence=[BLUE])
                fig.update_layout(**plotly_base(height=220))
                st.plotly_chart(fig, width="stretch")

    source_note(tracking=False, event=True)

# ── TAB 4: WC26 Predicted ─────────────────────────────────────────────────────
with tab4:
    st.caption("Predicted WC26 stats · avg of last 7 competitive games · StatsBomb open data")

    team_cov = coverage[coverage["team_name"] == team_a] if len(coverage) > 0 else pd.DataFrame()
    has_data = len(team_cov) > 0 and str(team_cov.iloc[0].get("has_predicted_data", "no")).lower() == "yes"

    if not has_data:
        st.info(
            f"**{team_a}** did not appear in EURO 2024, Copa América 2024, or AFCON 2023 — "
            "no predicted data available. WC26 live stats will populate as games are played.",
            icon="📭"
        )
    else:
        team_col = "team" if "team" in predicted.columns else "team_name"
        pred_row = predicted[predicted[team_col] == team_a]
        if pred_row.empty:
            pred_row = predicted[predicted[team_col].str.lower() == team_a.lower()]

        if pred_row.empty:
            st.warning("Predicted stats not found for this team.")
        else:
            pred = pred_row.iloc[0]
            games   = int(pred.get("games_in_sample", 0))
            quality = pred.get("data_quality", "")
            comps   = pred.get("competitions_used", "")

            st.markdown(f"**Based on last {games} competitive games** · {comps}")
            if quality == "limited":
                st.warning(f"Only {games} games available — limited sample size.", icon="⚠️")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pred. Goals/Game",   fmt(pred.get("pred_goals_per_game")))
                st.metric("Pred. xG/Game",      fmt(pred.get("pred_xg_per_game")))
                st.metric("Pred. Shots/Game",   fmt(pred.get("pred_shots_per_game")))
            with col2:
                st.metric("Pred. Possession %", fmt(pred.get("pred_possession_pct"), suffix="%"))
                st.metric("Pred. Pass Comp. %", fmt(pred.get("pred_pass_completion_pct"), suffix="%"))
                st.metric("Pred. Passes/Game",  fmt(pred.get("pred_passes_per_game"), 0))
            with col3:
                st.metric("Pred. Pressures/G",  fmt(pred.get("pred_pressures_per_game"), 0))
                st.metric("Pred. PPDA",         fmt(pred.get("pred_ppda")))
                st.metric("Pred. Crosses/G",    fmt(pred.get("pred_crosses_per_game")))

            if team_data is not None:
                st.markdown("---")
                st.markdown("#### WC22 vs Predicted WC26")
                compare_metrics = [
                    ("Goals/G",    "goals_per_game",       "pred_goals_per_game"),
                    ("xG/G",       "xg_per_game",          "pred_xg_per_game"),
                    ("Poss %",     "avg_possession_pct",   "pred_possession_pct"),
                    ("Press/G",    "pressures_per_game",   "pred_pressures_per_game"),
                    ("PPDA",       "avg_ppda",             "pred_ppda"),
                ]
                labels    = [m[0] for m in compare_metrics]
                wc22_vals = [float(team_data.get(m[1], 0) or 0) for m in compare_metrics]
                pred_vals = [float(pred.get(m[2], 0) or 0) for m in compare_metrics]
                fig = go.Figure()
                fig.add_trace(go.Bar(name="WC22",           x=labels, y=wc22_vals, marker_color="#dbeafe"))
                fig.add_trace(go.Bar(name="Predicted WC26", x=labels, y=pred_vals, marker_color=GREEN))
                fig.update_layout(**plotly_base(height=300), barmode="group",
                                  legend=dict(orientation="h", yanchor="bottom", y=1.02))
                st.plotly_chart(fig, width="stretch")

    source_note(tracking=False, event=True)
