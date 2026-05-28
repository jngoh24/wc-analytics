"""
Athletic-inspired theme for wc-analytics — matches the HSR dashboard exactly.
Source Serif 4 + Inter + JetBrains Mono · #f7f7f5 background · white cards
"""

# Plot theme constants
PLOT_BG    = "#ffffff"
PAPER_BG   = "#f7f7f5"
GRID_COLOR = "#eeeeec"
TEXT_COLOR = "#666666"
ACCENT     = "#1a6b3c"
BLUE       = "#1a4b8c"
RED        = "#c0392b"
AMBER      = "#b7791f"
GREEN      = "#1a6b3c"
POSITIVE   = "#1a6b3c"
NEGATIVE   = "#c0392b"

PLOT_LAYOUT = dict(
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PLOT_BG,
    font=dict(family="Inter, sans-serif", size=12, color=TEXT_COLOR),
    margin=dict(l=0, r=0, t=10, b=10),
    xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
    yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
    color: #1a1a1a;
}
.stApp { background-color: #f7f7f5; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e5e3;
}
section[data-testid="stSidebar"] * { color: #1a1a1a !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 1200px; }

/* ── Headers ── */
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

/* ── Metric cards ── */
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

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent;
    border-bottom: 2px solid #e5e5e3;
    gap: 0; padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent; color: #888;
    font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500;
    padding: 8px 20px; border-radius: 0;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}
.stTabs [aria-selected="true"] {
    background-color: transparent !important;
    color: #111 !important;
    border-bottom: 2px solid #111 !important;
}

/* ── Selectbox / inputs ── */
[data-baseweb="select"] { border-radius: 4px !important; }
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label {
    font-size: 12px; font-weight: 500; color: #444 !important;
    text-transform: uppercase; letter-spacing: 0.05em;
}

/* ── Buttons ── */
.stButton > button {
    background-color: #111; color: #fff;
    border: none; border-radius: 4px;
    font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500;
    padding: 8px 20px;
}
.stButton > button:hover { background-color: #333; }

/* ── Utility classes ── */
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
    font-size: 13px; padding: 3px 10px;
    border-radius: 3px; letter-spacing: 0.02em;
}
.gained-badge {
    display: inline-block; background: #e8f5e9; color: #2e7d32;
    font-size: 11px; font-weight: 600; padding: 2px 8px;
    border-radius: 3px; font-family: 'Inter', sans-serif;
}
.lost-badge {
    display: inline-block; background: #fce4e4; color: #c62828;
    font-size: 11px; font-weight: 600; padding: 2px 8px;
    border-radius: 3px; font-family: 'Inter', sans-serif;
}
.section-divider {
    border: none; border-top: 1px solid #e5e5e3; margin: 1.5rem 0;
}
.data-source {
    font-family: 'Inter', sans-serif; font-size: 11px; color: #aaa;
    margin-top: 8px;
}
</style>
"""


def inject_css():
    """Inject the Athletic theme CSS. Call at top of every page."""
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Render an Athletic-style page header with Source Serif 4."""
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f'<p class="kicker">{subtitle}</p>', unsafe_allow_html=True)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


def kpi_row(kpis: list):
    """
    Render a row of KPI metrics using st.metric (styled by CSS above).
    kpis: list of dicts with keys: label, value, delta (optional)
    """
    import streamlit as st
    cols = st.columns(len(kpis))
    for col, k in zip(cols, kpis):
        with col:
            st.metric(
                label=k["label"],
                value=k["value"],
                delta=k.get("delta"),
            )


def source_note(tracking: bool = True, event: bool = True):
    """Render data source attribution."""
    import streamlit as st
    parts = []
    if tracking:
        parts.append("GradientSports tracking data")
    if event:
        parts.append("StatsBomb open data")
    st.markdown(
        f'<p class="data-source">Data: {"  ·  ".join(parts)}</p>',
        unsafe_allow_html=True
    )


def plotly_base(height: int = 400, **overrides) -> dict:
    """Return a base Plotly layout dict matching the Athletic theme."""
    layout = {**PLOT_LAYOUT, "height": height}
    layout.update(overrides)
    return layout
