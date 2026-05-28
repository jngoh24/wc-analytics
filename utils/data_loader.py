"""
Data loader for wc-analytics dashboard.
Reads Gold CSVs exported from Databricks pipeline.
All CSVs live in the data/ folder alongside this app.
"""

import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data
def load_team_leaderboard() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "team_leaderboard.csv")
    return df


@st.cache_data
def load_team_match_log() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "team_match_log.csv")
    if "match_date" in df.columns:
        df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
    return df


@st.cache_data
def load_match_metadata() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "match_metadata.csv")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


@st.cache_data
def load_player_summary() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "player_summary.csv")
    return df


@st.cache_data
def load_player_match_log() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "player_match_log.csv")
    if "match_date" in df.columns:
        df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
    return df


@st.cache_data
def load_predicted_team_stats() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "predicted_team_stats.csv")
    return df


@st.cache_data
def load_predicted_player_stats() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "predicted_player_stats.csv")
    return df


@st.cache_data
def load_data_coverage() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "data_coverage.csv")
    return df


def fmt(val, decimals: int = 1, suffix: str = "") -> str:
    """Format a numeric value for display, handling NaN gracefully."""
    try:
        if pd.isna(val):
            return "—"
        return f"{val:.{decimals}f}{suffix}"
    except (TypeError, ValueError):
        return "—"


def delta_str(val) -> str:
    """Format a delta value with +/- sign."""
    try:
        if pd.isna(val):
            return "—"
        sign = "+" if val >= 0 else ""
        return f"{sign}{val:.1f}"
    except (TypeError, ValueError):
        return "—"


def delta_color(val) -> str:
    """Return CSS class for delta coloring."""
    try:
        if pd.isna(val):
            return ""
        return "delta-pos" if val >= 0 else "delta-neg"
    except (TypeError, ValueError):
        return ""
