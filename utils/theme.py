"""
GradientSports-inspired hybrid theme for the wc-analytics Streamlit dashboard.
Dark header/nav + light body for data readability.
"""

ACCENT       = "#4ade9a"
ACCENT_DARK  = "#16a34a"
DARK_BG      = "#0d0d0d"
DARK_CARD    = "#1a1a1a"
DARK_BORDER  = "#2a2a2a"
DARK_TEXT    = "#ffffff"
DARK_MUTED   = "#888888"
POSITIVE     = "#16a34a"
NEGATIVE     = "#dc2626"

CSS = f"""
<style>
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 0 !important; max-width: 1200px; }}
[data-testid="stSidebar"] {{ background: {DARK_BG}; }}
[data-testid="stSidebar"] * {{ color: #ccc !important; }}
[data-testid="stSidebarNav"] {{ display: none; }}

.gs-header {{
    background: {DARK_BG};
    padding: 14px 28px;
    display: flex;
    align-items: center;
    gap: 28px;
    margin: -1rem -1rem 0 -1rem;
    border-bottom: 0.5px solid {DARK_BORDER};
}}
.gs-logo {{
    font-size: 15px;
    font-weight: 600;
    color: {ACCENT};
    letter-spacing: -0.3px;
    margin-right: auto;
}}
.gs-nav-item {{
    font-size: 13px;
    color: {DARK_MUTED};
    text-decoration: none;
    padding-bottom: 2px;
}}
.gs-nav-active {{
    font-size: 13px;
    color: white;
    text-decoration: none;
    border-bottom: 1.5px solid {ACCENT};
    padding-bottom: 2px;
}}
.gs-hero {{
    background: #111;
    padding: 20px 28px 24px;
    margin: 0 -1rem 1.5rem -1rem;
    border-bottom: 0.5px solid {DARK_BORDER};
}}
.gs-hero-title {{
    font-size: 20px;
    font-weight: 600;
    color: {DARK_TEXT};
    margin: 0 0 4px;
}}
.gs-hero-sub {{
    font-size: 12px;
    color: {DARK_MUTED};
    margin: 0 0 16px;
}}
.gs-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}}
.gs-kpi {{
    background: {DARK_CARD};
    border-radius: 8px;
    padding: 12px 14px;
    border: 0.5px solid {DARK_BORDER};
}}
.gs-kpi-label {{
    font-size: 10px;
    color: #555;
    margin: 0 0 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.gs-kpi-value {{
    font-size: 22px;
    font-weight: 600;
    color: {DARK_TEXT};
    margin: 0;
}}
.gs-kpi-sub {{ font-size: 11px; color: {ACCENT}; margin-top: 2px; }}
.gs-kpi-sub-neg {{ font-size: 11px; color: #f87171; margin-top: 2px; }}
.gs-source {{ font-size: 11px; color: #9ca3af; margin-top: 8px; }}
.gs-source span {{ color: {ACCENT}; }}
.delta-pos {{ color: {POSITIVE}; font-weight: 500; }}
.delta-neg {{ color: {NEGATIVE}; font-weight: 500; }}
.section-title {{
    font-size: 15px;
    font-weight: 600;
    color: #111;
    margin: 1.5rem 0 0.75rem;
    padding-bottom: 6px;
    border-bottom: 2px solid {ACCENT};
    display: inline-block;
}}
.badge-tracking {{
    background: #f0fdf4; color: #15803d;
    border: 0.5px solid #bbf7d0;
    padding: 2px 8px; border-radius: 4px; font-size: 11px;
}}
.badge-event {{
    background: #eff6ff; color: #1d4ed8;
    border: 0.5px solid #bfdbfe;
    padding: 2px 8px; border-radius: 4px; font-size: 11px;
}}
.badge-none {{
    background: #f9fafb; color: #9ca3af;
    border: 0.5px solid #e5e7eb;
    padding: 2px 8px; border-radius: 4px; font-size: 11px;
}}
</style>
"""


def render_header(active: str = "Leaderboard"):
    import streamlit as st
    pages = [
        ("", "Leaderboard"),
        ("Team_Deep_Dive", "Team"),
        ("Player_Profile", "Player"),
        ("WC26_Predicted", "Predicted"),
    ]
    nav_links = "".join(
        f'<span class="{"gs-nav-active" if label == active else "gs-nav-item"}">{label}</span>'
        for _, label in pages
    )
    st.markdown(f"""
    {CSS}
    <div class="gs-header">
        <span class="gs-logo">● wc-analytics</span>
        {nav_links}
    </div>
    """, unsafe_allow_html=True)


def hero(title: str, subtitle: str, kpis: list):
    import streamlit as st
    kpi_html = "".join(f"""
        <div class="gs-kpi">
            <p class="gs-kpi-label">{k['label']}</p>
            <p class="gs-kpi-value">{k['value']}</p>
            <p class="{'gs-kpi-sub-neg' if k.get('negative') else 'gs-kpi-sub'}">{k.get('sub', '')}</p>
        </div>
    """ for k in kpis)
    st.markdown(f"""
    <div class="gs-hero">
        <p class="gs-hero-title">{title}</p>
        <p class="gs-hero-sub">{subtitle}</p>
        <div class="gs-kpi-grid">{kpi_html}</div>
    </div>
    """, unsafe_allow_html=True)


def source_note(tracking: bool = True, event: bool = True):
    import streamlit as st
    parts = []
    if tracking:
        parts.append("Tracking data via <span>GradientSports</span>")
    if event:
        parts.append("Events via <span>StatsBomb</span> open data")
    st.markdown(
        f'<p class="gs-source">{"  ·  ".join(parts)}</p>',
        unsafe_allow_html=True
    )
