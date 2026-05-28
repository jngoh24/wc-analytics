# wc-analytics

**FIFA World Cup 2022 → 2026 Team & Player Evolution Dashboard**

A Streamlit dashboard exploring how national teams have evolved between WC22 and WC26, built on GradientSports broadcast tracking data and StatsBomb open event data.

## Live Dashboard

[wc-analytics.streamlit.app](https://wc-analytics.streamlit.app) *(link to be updated on deployment)*

## Features

### Page 1 · Leaderboard
- Top 10/16/32 teams sortable by any stat
- Filterable across 20+ metrics: physical (tracking) and tactical (events)
- Your **Relative HSR metric** front and centre: ≥80% personal vMax, ≥1 second — vs the industry flat 20 km/h threshold
- Δ Rel vs Abs scatter — which teams are underrated by the standard metric?

### Page 2 · Team Deep Dive
- Physical tab: match-by-match HSR, distance, speed trends
- Tactical tab: xG, possession, pressures, PPDA per match
- Head-to-head comparison with any other WC22 team
- WC26 Predicted tab: projected stats from last 7 competitive games

### Page 3 · Player Profile
- Personal vMax, relative HSR, absolute HSR per player
- Technical stats: xG, passes, pressures, dribbles
- Position peer comparison histogram
- StatsBomb availability flag (47 players unmatched across ID systems)

### Page 4 · WC26 Predicted
- Predicted leaderboard for 32/48 WC26 teams
- Based on last 7 competitive games from EURO 2024, Copa América 2024, AFCON 2023
- Coverage transparency — which teams have data, quality rating, source competitions

## Data Sources

| Source | Data type | Coverage |
|--------|-----------|----------|
| GradientSports | Broadcast tracking (25Hz, x/y/z) | WC22 · 64 games |
| StatsBomb open data | Event data (passes, shots, pressures) | WC22 · EURO24 · Copa24 · AFCON23 |

## Architecture

```
Databricks (Azure) pipeline
  Bronze → Silver → Gold (Delta Lake)
    ↓ CSV export (8 files)
Streamlit Community Cloud
  app.py + pages/
```

### Pipeline notebooks (Databricks)
| Notebook | Description |
|----------|-------------|
| `01_bronze_tracking` | GradientSports → tracking_bronze (82M rows) |
| `02_bronze_statsbomb` | StatsBomb open data → events/matches/lineups bronze |
| `03_silver_tracking` | Speed, vMax (p99.9), relative + absolute HSR flags |
| `04_silver_statsbomb` | xG, PPDA, possession, tactical stats per team/player |
| `05_gold_team` | HSR run extraction, team leaderboard + match log CSVs |
| `06_gold_player` | Player summary + match log CSVs |
| `07_gold_predicted` | Predicted WC26 stats from recent tournaments |

### Key technical decisions
- **Relative HSR**: personal vMax computed at p99.9 of non-null speed frames, after capping at 45 km/h and nulling frame-gap teleport artefacts
- **GK exclusion**: GKs flagged `low_confidence=True` in vMax silver — excluded from relative HSR calculations due to occlusion artefacts
- **Player ID crosswalk**: GradientSports and StatsBomb use different player ID systems. Name matching (exact + accent normalisation + nickname + fuzzy) achieves 92.5% coverage (579/626 players)
- **Team ID crosswalk**: GradientSports and StatsBomb use different team ID systems — bridged via team name

## Data Limitations

- Relative HSR (physical) only available for WC22 — no tracking data for WC26 or recent qualifiers
- 16/48 WC26 teams have no predicted stats (AFC teams + some CONCACAF/UEFA not in covered tournaments)
- 47/626 WC22 players have no StatsBomb technical stats (name matching failure — mainly Arabic transliteration differences)

## Local Development

```bash
git clone https://github.com/jngoh24/wc-analytics
cd wc-analytics
pip install -r requirements.txt

# Add Gold CSVs to data/ folder (download from DBFS via Azure Storage Explorer)
# data/team_leaderboard.csv
# data/team_match_log.csv
# data/match_metadata.csv
# data/player_summary.csv
# data/player_match_log.csv
# data/predicted_team_stats.csv
# data/predicted_player_stats.csv
# data/data_coverage.csv

streamlit run app.py
```

## Deployment

Deployed on Streamlit Community Cloud. Connected to this GitHub repo — pushes to `main` auto-deploy.

CSVs committed to `data/` folder (files are small enough for GitHub — largest is ~15MB).

## Related Projects

- [HSR · Effort, Not Speed](https://github.com/jngoh24/hsr) — the original relative HSR metric project (WC22 player-level)
- [SwishScore](https://github.com/jngoh24/swishscore_nba) — NBA shot quality model (xG equivalent for basketball)
