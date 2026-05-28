import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="wc-analytics · WC22 → WC26",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS — Athletic theme (matches HSR dashboard)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
    color: #1a1a1a;
}
.stApp { background-color: #f7f7f5; }

section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e5e3;
}
section[data-testid="stSidebar"] * { color: #1a1a1a !important; }

h1 {
    font-family: 'Source Serif 4', Georgia, serif;
    font-weight: 600; font-size: 28px; color: #111111;
    letter-spacing: -0.01em; line-height: 1.2;
}
h2, h3, h4 {
    font-family: 'Inter', sans-serif;
    font-weight: 600; color: #111111; letter-spacing: -0.01em;
}
h3 { font-size: 16px; }
h4 { font-size: 14px; font-weight: 500; color: #444; }

[data-testid="metric-container"] {
    background-color: #ffffff;
    border: 1px solid #e5e5e3;
    border-radius: 4px;
    padding: 16px 20px;
    box-shadow: none;
}
[data-testid="metric-container"] label {
    font-size: 11px; font-weight: 500; color: #888 !important;
    text-transform: uppercase; letter-spacing: 0.06em;
    font-family: 'Inter', sans-serif;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 26px; font-weight: 600; color: #111 !important;
    font-family: 'Source Serif 4', serif;
}

.stTabs [data-baseweb="tab-list"] {
    background-color: transparent;
    border-bottom: 2px solid #e5e5e3;
    gap: 0; padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent; color: #888;
    font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500;
    border-radius: 0; border-bottom: 2px solid transparent;
    margin-bottom: -2px; padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background-color: transparent !important;
    color: #111 !important;
    border-bottom: 2px solid #111 !important;
}

hr { border-color: #e5e5e3; }

[data-testid="stDataFrame"] {
    border: 1px solid #e5e5e3;
    border-radius: 4px;
    background: #fff;
}

[data-testid="stSlider"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stSelectbox"] label {
    font-size: 12px; font-weight: 500; color: #444 !important;
    text-transform: uppercase; letter-spacing: 0.05em;
}

.eyebrow {
    font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 600;
    color: #888; text-transform: uppercase; letter-spacing: 0.08em;
}
.kicker {
    font-family: 'Source Serif 4', serif;
    font-size: 13px; font-style: italic; color: #555;
}
.threshold-badge {
    display: inline-block; background: #111; color: #fff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px; padding: 3px 10px; border-radius: 3px; letter-spacing: 0.02em;
}
.gained-badge { display:inline-block; background:#e8f5e9; color:#2e7d32;
    font-size:11px; font-weight:600; padding:2px 8px; border-radius:3px; font-family:'Inter',sans-serif; }
.lost-badge { display:inline-block; background:#fce4e4; color:#c62828;
    font-size:11px; font-weight:600; padding:2px 8px; border-radius:3px; font-family:'Inter',sans-serif; }
.unch-badge { display:inline-block; background:#f5f5f5; color:#666;
    font-size:11px; font-weight:600; padding:2px 8px; border-radius:3px; font-family:'Inter',sans-serif; }
.caption { font-family:'Inter',sans-serif; font-size:12px; color:#888; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Flag helper
# ─────────────────────────────────────────────
TEAM_TO_ISO = {
    "United States":"us","Canada":"ca","Mexico":"mx","England":"gb-eng","France":"fr",
    "Germany":"de","Spain":"es","Portugal":"pt","Netherlands":"nl","Belgium":"be",
    "Switzerland":"ch","Croatia":"hr","Norway":"no","Scotland":"gb-sct","Austria":"at",
    "Bosnia and Herzegovina":"ba","Sweden":"se","Turkiye":"tr","Czechia":"cz",
    "Argentina":"ar","Brazil":"br","Colombia":"co","Ecuador":"ec","Paraguay":"py",
    "Uruguay":"uy","Japan":"jp","South Korea":"kr","Australia":"au","Iran":"ir",
    "Saudi Arabia":"sa","Qatar":"qa","Jordan":"jo","Uzbekistan":"uz","Morocco":"ma",
    "Senegal":"sn","Ghana":"gh","Tunisia":"tn","Algeria":"dz","Egypt":"eg",
    "Ivory Coast":"ci","South Africa":"za","Cape Verde":"cv","DR Congo":"cd",
    "Panama":"pa","Curacao":"cw","Haiti":"ht","New Zealand":"nz","Iraq":"iq",
    "Wales":"gb-wls","Poland":"pl","Denmark":"dk","Cameroon":"cm","Serbia":"rs",
}

def flag_url(team, size=40):
    iso = TEAM_TO_ISO.get(team, "").lower()
    return f"https://flagcdn.com/w{size}/{iso}.png" if iso else ""

def flag_img(team, size=20):
    url = flag_url(team)
    return f'<img src="{url}" width="{size}" style="vertical-align:middle;border-radius:2px;margin-right:6px;">' if url else ""

# ─────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@st.cache_data
def load_data():
    def _read(name):
        path = os.path.join(DATA_DIR, name)
        return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
    return {
        "leaderboard":      _read("team_leaderboard.csv"),
        "team_match":       _read("team_match_log.csv"),
        "match_meta":       _read("match_metadata.csv"),
        "player_summary":   _read("player_summary.csv"),
        "player_match":     _read("player_match_log.csv"),
        "predicted_team":   _read("predicted_team_stats.csv"),
        "predicted_player": _read("predicted_player_stats.csv"),
        "coverage":         _read("data_coverage.csv"),
    }

try:
    D = load_data()
    data_loaded = not D["leaderboard"].empty
except Exception:
    data_loaded = False
    D = {}

# ─────────────────────────────────────────────
# Plotly theme
# ─────────────────────────────────────────────
PLOT_BG="#ffffff"; PAPER_BG="#f7f7f5"; GRID="#eeeeec"; TEXT="#666666"
ACCENT="#1a6b3c"; BLUE="#1a4b8c"; RED="#c0392b"; AMBER="#b7791f"; GREEN="#1a6b3c"

def base_layout(title="", height=400, xaxis=None, yaxis=None):
    default_axis = dict(gridcolor=GRID, showline=False, zeroline=False)
    x = {**default_axis, **(xaxis or {})}
    y = {**default_axis, **(yaxis or {})}
    return dict(
        title=dict(text=title, font=dict(family="Inter", size=13, color="#111")),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(family="Inter", color=TEXT, size=11),
        height=height, margin=dict(l=40, r=20, t=40, b=40),
        xaxis=x, yaxis=y,
    )

def fmt(v, d=1, suffix=""):
    try:
        if pd.isna(v): return "—"
        return f"{v:.{d}f}{suffix}"
    except (TypeError, ValueError):
        return "—"

def delta_str(v):
    try:
        if pd.isna(v): return "—"
        return f"{'+' if v >= 0 else ''}{v:.1f}"
    except (TypeError, ValueError):
        return "—"

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="eyebrow" style="margin-bottom:2px;">wc-analytics</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Inter;font-size:12px;color:#666;margin:0 0 16px 0;">WC22 → WC26 Evolution</p>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### About")
    st.markdown(
        '<p style="font-family:Inter;font-size:12px;color:#666;line-height:1.6;">'
        'Comparing national team performance between the 2022 and 2026 World Cups, '
        'built on GradientSports broadcast tracking data and StatsBomb open event data.</p>',
        unsafe_allow_html=True
    )
    st.divider()
    st.markdown(
        '<p style="font-family:Inter;font-size:11px;color:#888;line-height:1.5;">'
        '<strong>Relative HSR</strong> — a run where a player reaches &ge;80% of their '
        'personal v-max for &ge;1 second.<br><br>'
        '<strong>Industry standard</strong> — flat 20 km/h absolute threshold.</p>',
        unsafe_allow_html=True
    )
    st.divider()
    st.markdown('<p class="eyebrow">Data Sources</p>', unsafe_allow_html=True)
    st.caption("GradientSports tracking · StatsBomb open data")

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown('<p class="eyebrow" style="margin-bottom:4px;">FIFA World Cup 2022 → 2026 · Team & Player Evolution</p>', unsafe_allow_html=True)
st.markdown('<h1 style="margin:0 0 4px 0;">wc-analytics</h1>', unsafe_allow_html=True)
st.markdown(
    "<p class='kicker'>How national teams have evolved between World Cups — physical output via "
    "<span class='threshold-badge'>GradientSports</span> tracking and tactical profile via StatsBomb events.</p>",
    unsafe_allow_html=True
)
st.divider()

if not data_loaded:
    st.error(
        "⚠️ Data files not found. Place the 8 Gold CSVs in the `app/data/` folder: "
        "team_leaderboard.csv, team_match_log.csv, match_metadata.csv, player_summary.csv, "
        "player_match_log.csv, predicted_team_stats.csv, predicted_player_stats.csv, data_coverage.csv"
    )
    st.stop()

lb = D["leaderboard"]
team_match = D["team_match"]
players = D["player_summary"]
player_match = D["player_match"]
predicted = D["predicted_team"]
coverage = D["coverage"]

# ─────────────────────────────────────────────
# Tournament KPIs
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
total_goals  = int(lb["total_goals"].sum())          if "total_goals" in lb.columns else 0
avg_xg       = lb["xg_per_game"].mean()              if "xg_per_game" in lb.columns else 0
avg_hsr      = lb["rel_hsr_runs_per_game"].mean()    if "rel_hsr_runs_per_game" in lb.columns else 0
avg_hsr_dist = lb["rel_hsr_dist_m_per_game"].mean()  if "rel_hsr_dist_m_per_game" in lb.columns else 0
n_teams      = lb["team_name"].nunique()             if "team_name" in lb.columns else 0

k1.metric("Teams", f"{n_teams}")
k2.metric("Total goals", f"{total_goals}")
k3.metric("Avg xG / game", f"{avg_xg:.2f}")
k4.metric("Avg Rel HSR / game", f"{avg_hsr:.1f}")
k5.metric("Avg HSR dist / game", f"{avg_hsr_dist:.0f} m")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Tabs — single-file architecture (matches HSR)
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Leaderboard",
    "Team Deep Dive",
    "Player Profile",
    "WC26 Predicted",
])

# ══════════════════════════════════════════════
# TAB 1 — Leaderboard
# ══════════════════════════════════════════════
with tab1:
    st.markdown("### Team rankings")

    STAT_OPTIONS = {
        "Rel. HSR Runs / Game":         ("rel_hsr_runs_per_game",     "tracking"),
        "Rel. HSR Distance / Game (m)": ("rel_hsr_dist_m_per_game",   "tracking"),
        "Abs. HSR Runs / Game":         ("abs_hsr_runs_per_game",     "tracking"),
        "Δ Rel vs Abs HSR Runs":        ("delta_hsr_runs_per_game",   "tracking"),
        "Goals / Game":                 ("goals_per_game",            "event"),
        "xG / Game":                    ("xg_per_game",               "event"),
        "Shots / Game":                 ("shots_per_game",            "event"),
        "Possession %":                 ("avg_possession_pct",        "event"),
        "Pass Completion %":            ("avg_pass_completion_pct",   "event"),
        "Crosses / Game":               ("crosses_per_game",          "event"),
        "Pressures / Game":             ("pressures_per_game",        "event"),
        "PPDA":                         ("avg_ppda",                  "event"),
        "Interceptions / Game":         ("interceptions_per_game",    "event"),
    }

    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        sel_stat = st.selectbox("Sort by", list(STAT_OPTIONS.keys()), key="lb_stat")
    with c2:
        top_n = st.selectbox("Show top", [10, 16, 32], index=0, key="lb_n")
    with c3:
        asc = st.checkbox("Ascending", value=(sel_stat == "PPDA"), key="lb_asc")

    stat_col, stat_type = STAT_OPTIONS[sel_stat]
    color = GREEN if stat_type == "tracking" else BLUE

    if stat_col in lb.columns:
        lb_sorted = lb.dropna(subset=[stat_col]).sort_values(stat_col, ascending=asc).head(top_n).reset_index(drop=True)

        fig = go.Figure(go.Bar(
            x=lb_sorted[stat_col],
            y=lb_sorted["team_name"],
            orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            text=lb_sorted[stat_col].round(1),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>" + sel_stat + ": %{x:.2f}<extra></extra>",
        ))
        fig.update_layout(**base_layout(
            f"Top {top_n} · {sel_stat}",
            height=max(400, top_n * 26),
            yaxis=dict(autorange="reversed" if not asc else True, tickfont=dict(size=11)),
            xaxis=dict(title=sel_stat),
        ))
        st.plotly_chart(fig, use_container_width=True)

    # Full table
    st.divider()
    st.markdown("#### Full rankings table")
    tbl_cols = ["team_name", "games_played", "rel_hsr_runs_per_game", "abs_hsr_runs_per_game",
                "delta_hsr_runs_per_game", "goals_per_game", "xg_per_game",
                "avg_possession_pct", "avg_pass_completion_pct", "pressures_per_game", "avg_ppda"]
    tbl_cols = [c for c in tbl_cols if c in lb.columns]
    tbl = lb[tbl_cols].sort_values(stat_col if stat_col in tbl_cols else tbl_cols[1], ascending=False).reset_index(drop=True)
    st.dataframe(
        tbl.rename(columns={
            "team_name":"Team","games_played":"GP",
            "rel_hsr_runs_per_game":"Rel HSR/G","abs_hsr_runs_per_game":"Abs HSR/G",
            "delta_hsr_runs_per_game":"Δ HSR","goals_per_game":"Goals/G","xg_per_game":"xG/G",
            "avg_possession_pct":"Poss %","avg_pass_completion_pct":"Pass %",
            "pressures_per_game":"Press/G","avg_ppda":"PPDA",
        }),
        use_container_width=True, height=400,
    )

    # Rel vs Abs scatter
    st.divider()
    st.markdown("#### Your metric vs industry standard")
    st.markdown('<p class="caption">Teams above the diagonal are underrated by the flat 20 km/h threshold.</p>', unsafe_allow_html=True)
    if "rel_hsr_runs_per_game" in lb.columns and "abs_hsr_runs_per_game" in lb.columns:
        sc = lb.dropna(subset=["rel_hsr_runs_per_game", "abs_hsr_runs_per_game"]).copy()
        sc["delta"] = sc["rel_hsr_runs_per_game"] - sc["abs_hsr_runs_per_game"]
        fig2 = px.scatter(
            sc, x="abs_hsr_runs_per_game", y="rel_hsr_runs_per_game",
            text="team_name", color="delta",
            color_continuous_scale=[[0, RED], [0.5, "#f3f4f6"], [1, GREEN]],
            color_continuous_midpoint=0,
            labels={"abs_hsr_runs_per_game":"Absolute HSR Runs/Game (20 km/h)",
                    "rel_hsr_runs_per_game":"Relative HSR Runs/Game (≥80% vMax)"},
        )
        mx = max(sc["rel_hsr_runs_per_game"].max(), sc["abs_hsr_runs_per_game"].max()) * 1.05
        fig2.add_trace(go.Scatter(x=[0, mx], y=[0, mx], mode="lines",
                                  line=dict(color="#ccc", width=1, dash="dash"),
                                  showlegend=False, hoverinfo="skip"))
        fig2.update_traces(textposition="top center", marker=dict(size=9),
                           selector=dict(mode="markers+text"))
        fig2.update_layout(**base_layout(height=480), coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — Team Deep Dive
# ══════════════════════════════════════════════
with tab2:
    all_teams = sorted(lb["team_name"].dropna().unique().tolist())
    c1, c2 = st.columns([2, 2])
    with c1:
        team_a = st.selectbox("Select team", all_teams,
                              index=all_teams.index("France") if "France" in all_teams else 0,
                              key="team_a")
    with c2:
        cmp_on = st.checkbox("Compare with another team", key="cmp")
        team_b = None
        if cmp_on:
            rem = [t for t in all_teams if t != team_a]
            team_b = st.selectbox("Compare with", rem,
                                  index=rem.index("Argentina") if "Argentina" in rem else 0, key="team_b")

    td = lb[lb["team_name"] == team_a].iloc[0] if len(lb[lb["team_name"] == team_a]) > 0 else None

    st.markdown(f"## {flag_img(team_a, 28)}{team_a}", unsafe_allow_html=True)
    if td is not None:
        rec = f"{int(td.get('wins',0))}W {int(td.get('draws',0))}D {int(td.get('losses',0))}L"
        st.markdown(f'<p class="kicker">FIFA World Cup 2022 · {rec} · {int(td.get("games_played",0))} games</p>', unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Goals / Game", fmt(td.get("goals_per_game")))
        m2.metric("xG / Game", fmt(td.get("xg_per_game")))
        m3.metric("Rel HSR / Game", fmt(td.get("rel_hsr_runs_per_game")))
        m4.metric("Δ Rel vs Abs", delta_str(td.get("delta_hsr_runs_per_game")))

    st.divider()
    sub1, sub2, sub3, sub4 = st.tabs(["Overview", "Physical", "Tactical", "WC26 Predicted"])

    with sub1:
        if td is not None:
            o1, o2, o3 = st.columns(3)
            with o1:
                st.metric("Possession %", fmt(td.get("avg_possession_pct"), suffix="%"))
                st.metric("Pass Completion", fmt(td.get("avg_pass_completion_pct"), suffix="%"))
                st.metric("Passes / Game", fmt(td.get("passes_per_game"), 0))
            with o2:
                st.metric("Shots / Game", fmt(td.get("shots_per_game")))
                st.metric("Shots on Target", fmt(td.get("shots_on_target_per_game")))
                st.metric("Crosses / Game", fmt(td.get("crosses_per_game")))
            with o3:
                st.metric("Pressures / Game", fmt(td.get("pressures_per_game"), 0))
                st.metric("PPDA", fmt(td.get("avg_ppda")))
                st.metric("Interceptions / Game", fmt(td.get("interceptions_per_game")))

            if cmp_on and team_b:
                tb = lb[lb["team_name"] == team_b]
                if len(tb) > 0:
                    tb = tb.iloc[0]
                    st.markdown(f"#### {team_a} vs {team_b}")
                    stats = ["goals_per_game","xg_per_game","avg_possession_pct",
                             "rel_hsr_runs_per_game","pressures_per_game","avg_ppda"]
                    labels = ["Goals/G","xG/G","Poss %","Rel HSR/G","Press/G","PPDA"]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name=team_a, x=labels,
                                         y=[float(td.get(c,0) or 0) for c in stats], marker_color=GREEN))
                    fig.add_trace(go.Bar(name=team_b, x=labels,
                                         y=[float(tb.get(c,0) or 0) for c in stats], marker_color=BLUE))
                    fig.update_layout(**base_layout(height=360), barmode="group",
                                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
                    st.plotly_chart(fig, use_container_width=True)

    with sub2:
        st.markdown('<p class="caption">Physical stats from GradientSports broadcast tracking (25Hz)</p>', unsafe_allow_html=True)
        tm = team_match[team_match["team_name"] == team_a].copy() if "team_name" in team_match.columns else pd.DataFrame()
        if td is not None:
            p1, p2 = st.columns(2)
            p1.metric("Avg Rel HSR Runs/Game", fmt(td.get("rel_hsr_runs_per_game")))
            p1.metric("Avg Rel HSR Dist/Game", fmt(td.get("rel_hsr_dist_m_per_game"), suffix=" m"))
            p2.metric("Avg Abs HSR Runs/Game", fmt(td.get("abs_hsr_runs_per_game")))
            p2.metric("Δ Rel vs Abs Runs/Game", delta_str(td.get("delta_hsr_runs_per_game")))
        if not tm.empty and "rel_hsr_runs" in tm.columns and "match_date" in tm.columns:
            tm = tm.sort_values("match_date")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=tm["match_date"].astype(str), y=tm["rel_hsr_runs"],
                                 name="Rel. HSR", marker_color=GREEN))
            if "abs_hsr_runs" in tm.columns:
                fig.add_trace(go.Scatter(x=tm["match_date"].astype(str), y=tm["abs_hsr_runs"],
                                         mode="lines+markers", name="Abs. HSR (20 km/h)",
                                         line=dict(color="#aaa", width=1.5, dash="dot")))
            fig.update_layout(**base_layout("Rel. HSR Runs per match", height=320),
                              legend=dict(orientation="h", yanchor="bottom", y=1.02))
            st.plotly_chart(fig, use_container_width=True)

    with sub3:
        st.markdown('<p class="caption">Tactical stats from StatsBomb open data</p>', unsafe_allow_html=True)
        tm = team_match[team_match["team_name"] == team_a].copy() if "team_name" in team_match.columns else pd.DataFrame()
        if not tm.empty and "xg" in tm.columns and "match_date" in tm.columns:
            tm = tm.sort_values("match_date")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=tm["match_date"].astype(str), y=tm["xg"], name="xG", marker_color="#dbeafe"))
            if "goals" in tm.columns:
                fig.add_trace(go.Scatter(x=tm["match_date"].astype(str), y=tm["goals"],
                                         mode="lines+markers", name="Goals",
                                         line=dict(color=GREEN, width=2), marker=dict(size=8)))
            fig.update_layout(**base_layout("xG vs Goals per match", height=320),
                              legend=dict(orientation="h", yanchor="bottom", y=1.02))
            st.plotly_chart(fig, use_container_width=True)

    with sub4:
        st.markdown('<p class="caption">Predicted WC26 · avg of last 7 competitive games · StatsBomb</p>', unsafe_allow_html=True)
        cov = coverage[coverage["team_name"] == team_a] if len(coverage) > 0 else pd.DataFrame()
        has = len(cov) > 0 and str(cov.iloc[0].get("has_predicted_data","no")).lower() == "yes"
        if not has:
            st.info(f"**{team_a}** did not appear in EURO 2024, Copa América 2024, or AFCON 2023 — no predicted data. WC26 live stats will populate as games are played.", icon="📭")
        else:
            tcol = "team" if "team" in predicted.columns else "team_name"
            pr = predicted[predicted[tcol] == team_a]
            if not pr.empty:
                pr = pr.iloc[0]
                games = int(pr.get("games_in_sample", 0))
                st.markdown(f"**Based on last {games} competitive games** · {pr.get('competitions_used','')}")
                q1, q2, q3 = st.columns(3)
                q1.metric("Pred. Goals/G", fmt(pr.get("pred_goals_per_game")))
                q1.metric("Pred. xG/G", fmt(pr.get("pred_xg_per_game")))
                q2.metric("Pred. Possession %", fmt(pr.get("pred_possession_pct"), suffix="%"))
                q2.metric("Pred. Pass Comp %", fmt(pr.get("pred_pass_completion_pct"), suffix="%"))
                q3.metric("Pred. Pressures/G", fmt(pr.get("pred_pressures_per_game"), 0))
                q3.metric("Pred. PPDA", fmt(pr.get("pred_ppda")))
                if td is not None:
                    st.markdown("#### WC22 vs Predicted WC26")
                    cm = [("Goals/G","goals_per_game","pred_goals_per_game"),
                          ("xG/G","xg_per_game","pred_xg_per_game"),
                          ("Poss %","avg_possession_pct","pred_possession_pct"),
                          ("Press/G","pressures_per_game","pred_pressures_per_game"),
                          ("PPDA","avg_ppda","pred_ppda")]
                    labels = [m[0] for m in cm]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name="WC22", x=labels,
                                         y=[float(td.get(m[1],0) or 0) for m in cm], marker_color="#dbeafe"))
                    fig.add_trace(go.Bar(name="Predicted WC26", x=labels,
                                         y=[float(pr.get(m[2],0) or 0) for m in cm], marker_color=GREEN))
                    fig.update_layout(**base_layout(height=320), barmode="group",
                                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
                    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — Player Profile
# ══════════════════════════════════════════════
with tab3:
    c1, c2, c3 = st.columns(3)
    with c1:
        pteams = sorted(players["team_name"].dropna().unique().tolist()) if "team_name" in players.columns else []
        sel_team = st.selectbox("Filter by team", ["All teams"] + pteams, key="p_team")
    with c2:
        pposs = sorted(players["position"].dropna().unique().tolist()) if "position" in players.columns else []
        sel_pos = st.selectbox("Filter by position", ["All positions"] + pposs, key="p_pos")

    fp = players.copy()
    if sel_team != "All teams":
        fp = fp[fp["team_name"] == sel_team]
    if sel_pos != "All positions":
        fp = fp[fp["position"] == sel_pos]

    with c3:
        popts = sorted(fp["player_name"].dropna().unique().tolist()) if "player_name" in fp.columns else []
        if not popts:
            st.warning("No players for selected filters.")
            st.stop()
        sel_player = st.selectbox("Select player", popts, key="p_player")

    p = fp[fp["player_name"] == sel_player]
    if not p.empty:
        p = p.iloc[0]
        tn = str(p.get("team_name",""))
        st.markdown(f"## {flag_img(tn, 28)}{sel_player}", unsafe_allow_html=True)
        st.markdown(f'<p class="kicker">{tn} · {p.get("position","")} · WC22 · {int(p.get("games_played",0))} games</p>', unsafe_allow_html=True)

        sb_avail = str(p.get("sb_data_available","False")).lower() == "true"
        if not sb_avail:
            st.info("Technical stats not available — no StatsBomb match found. Physical tracking stats shown below.", icon="📭")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Personal vMax", fmt(p.get("personal_vmax_kmh"), suffix=" km/h"))
        m2.metric("Rel HSR/Game", fmt(p.get("avg_rel_hsr_runs_per_game")))
        m3.metric("xG / Game", fmt(p.get("xg_per_game")))
        m4.metric("Δ Rel vs Abs", delta_str(p.get("avg_delta_hsr_runs_per_game")))

        st.divider()
        pt1, pt2 = st.tabs(["Physical Profile", "Technical Profile"])
        with pt1:
            x1, x2, x3 = st.columns(3)
            x1.metric("Personal vMax", fmt(p.get("personal_vmax_kmh"), suffix=" km/h"))
            x1.metric("Tournament Max Speed", fmt(p.get("tournament_max_speed_kmh"), suffix=" km/h"))
            x2.metric("Rel HSR Runs/Game", fmt(p.get("avg_rel_hsr_runs_per_game")))
            x2.metric("Rel HSR Dist/Game", fmt(p.get("avg_rel_hsr_dist_m_per_game"), suffix=" m"))
            x3.metric("Abs HSR Runs/Game", fmt(p.get("avg_abs_hsr_runs_per_game")))
            x3.metric("Avg Distance/Game", fmt(p.get("avg_distance_m_per_game"), suffix=" m"))

            pm = player_match[player_match["player_name"] == sel_player] if "player_name" in player_match.columns else pd.DataFrame()
            if not pm.empty and "match_date" in pm.columns and "rel_hsr_runs" in pm.columns:
                pm = pm.sort_values("match_date")
                fig = go.Figure()
                fig.add_trace(go.Bar(x=pm["match_date"].astype(str), y=pm["rel_hsr_runs"],
                                     name="Rel. HSR", marker_color=GREEN))
                if "abs_hsr_runs" in pm.columns:
                    fig.add_trace(go.Scatter(x=pm["match_date"].astype(str), y=pm["abs_hsr_runs"],
                                             mode="lines+markers", name="Abs. HSR",
                                             line=dict(color="#aaa", width=1.5, dash="dot")))
                fig.update_layout(**base_layout("Rel. HSR Runs per match", height=300),
                                  legend=dict(orientation="h", yanchor="bottom", y=1.02))
                st.plotly_chart(fig, use_container_width=True)

            pos = str(p.get("position",""))
            if pos and "avg_rel_hsr_runs_per_game" in players.columns:
                peers = players[players["position"] == pos].copy()
                peers["hl"] = peers["player_name"] == sel_player
                fig2 = px.histogram(peers, x="avg_rel_hsr_runs_per_game", color="hl",
                                    color_discrete_map={True: GREEN, False: "#e5e5e3"}, nbins=20,
                                    labels={"avg_rel_hsr_runs_per_game": f"Rel HSR Runs/Game ({pos})"})
                pv = float(p.get("avg_rel_hsr_runs_per_game") or 0)
                if pv > 0:
                    fig2.add_vline(x=pv, line_dash="dash", line_color=GREEN)
                fig2.update_layout(**base_layout("Position peer comparison", height=240), showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        with pt2:
            if not sb_avail:
                st.info("No StatsBomb data available for this player.", icon="📭")
            else:
                y1, y2, y3 = st.columns(3)
                y1.metric("Goals", str(int(p.get("total_goals",0))))
                y1.metric("Goals / Game", fmt(p.get("goals_per_game")))
                y1.metric("xG / Game", fmt(p.get("xg_per_game")))
                y2.metric("Total Passes", str(int(p.get("total_passes",0))))
                y2.metric("Passes / Game", fmt(p.get("passes_per_game"), 0))
                y2.metric("Pass Comp %", fmt(p.get("avg_pass_completion_pct"), suffix="%"))
                y3.metric("Pressures/Game", fmt(p.get("pressures_per_game"), 0))
                y3.metric("Dribbles/Game", fmt(p.get("dribbles_per_game")))
                y3.metric("Interceptions/G", fmt(p.get("interceptions_per_game")))

                pm = player_match[player_match["player_name"] == sel_player] if "player_name" in player_match.columns else pd.DataFrame()
                if not pm.empty and "xg" in pm.columns and "match_date" in pm.columns:
                    pm = pm.sort_values("match_date")
                    fig = px.bar(pm, x="match_date", y="xg", color_discrete_sequence=[BLUE])
                    fig.update_layout(**base_layout("xG per match", height=240))
                    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — WC26 Predicted
# ══════════════════════════════════════════════
with tab4:
    st.markdown("### WC26 predicted performance")
    st.markdown('<p class="caption">Based on last 7 competitive games (excl. friendlies) · StatsBomb open data</p>', unsafe_allow_html=True)

    tw = coverage[coverage["has_predicted_data"] == "yes"]["team_name"].tolist() if len(coverage) > 0 else []
    two = coverage[coverage["has_predicted_data"] == "no"]["team_name"].tolist() if len(coverage) > 0 else []

    k1, k2, k3 = st.columns(3)
    k1.metric("Teams with data", len(tw))
    k2.metric("Teams without data", len(two))
    k3.metric("Good quality", len(predicted[predicted["data_quality"] == "good"]) if len(predicted) > 0 else 0)

    st.divider()
    if len(predicted) > 0:
        PRED = {
            "Pred. Goals / Game":"pred_goals_per_game","Pred. xG / Game":"pred_xg_per_game",
            "Pred. Shots / Game":"pred_shots_per_game","Pred. Possession %":"pred_possession_pct",
            "Pred. Passes / Game":"pred_passes_per_game","Pred. Pressures / Game":"pred_pressures_per_game",
            "Pred. PPDA":"pred_ppda","Pred. Crosses / Game":"pred_crosses_per_game",
        }
        c1, c2 = st.columns([3, 1])
        with c1:
            ps = st.selectbox("Sort by", list(PRED.keys()), key="pred_stat")
        with c2:
            pn = st.selectbox("Show top", [10, 20, 32], index=0, key="pred_n")
        scol = PRED[ps]
        tcol = "team" if "team" in predicted.columns else "team_name"
        if scol in predicted.columns:
            psd = predicted.dropna(subset=[scol]).sort_values(scol, ascending=(ps == "Pred. PPDA")).head(pn).reset_index(drop=True)
            fig = go.Figure(go.Bar(
                x=psd[scol], y=psd[tcol], orientation="h",
                marker=dict(color=BLUE, line=dict(width=0)),
                text=psd[scol].round(2), textposition="outside",
            ))
            fig.update_layout(**base_layout(f"Predicted · {ps}", height=max(400, pn*26),
                                            yaxis=dict(autorange="reversed")))
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("#### Data coverage")
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("**Teams with predicted data**")
        for t in sorted(tw):
            cov = coverage[coverage["team_name"] == t]
            q = cov.iloc[0].get("data_quality","") if len(cov) > 0 else ""
            badge = '<span class="gained-badge">good</span>' if q == "good" else '<span class="lost-badge">limited</span>'
            st.markdown(f'{flag_img(t,16)}{t} {badge}', unsafe_allow_html=True)
    with cc2:
        st.markdown("**Teams without predicted data**")
        for t in sorted(two):
            st.markdown(f'{flag_img(t,16)}{t} <span class="unch-badge">no data</span>', unsafe_allow_html=True)
