"""Central configuration. Every threshold/decision used by the analysis must live here (and in docs/)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
EXTERNAL = ROOT / "data" / "external"
OUT = ROOT / "outputs"

# Expected shape of the original data pack, as recorded in the handoff (docs/original/). Used only to verify files.
EXPECTED_FILES = {
    "ball_by_ball.csv": {"rows": 200_999, "cols": 33},
    "matches.csv": {"rows": 883, "cols": 22},
    "competitions.csv": {"rows": 141, "cols": 4},
    "teams.csv": {"rows": 353, "cols": 3},
    "playing_eleven.csv": {"rows": 28_381, "cols": 9},
    "competition_team_player_mapping.csv": {"rows": 6_413, "cols": 6},
}

RANDOM_SEED = 2026  # fixed for every bootstrap / CV split; record any change in PROJECT_LOG.md

# --- Scope decisions: recorded in docs/decisions.md ---------------------------------------------
PRIMARY_COMPETITION_FORMATS = ("T20", "T20I")
SENSITIVITY_ONLY_COMPETITIONS = (
    "Men's T20 Emerging Teams Asia Cup 2024",
    "Asia Cup Rising Stars 2025",
)
PLS_MEANING = "Partial Least Squares"  # working interpretation; do not activate until confirmed
PLS_STATUS = "deferred_pending_confirmation"  # D-002
SUBMITTED_LENS = "A"  # D-003: transparent pressure-versus-baseline ranking

PRESSURE_BANDS = None          # Step 5
MIN_PRESSURE_BALLS = None      # Step 8 (set after inspecting distributions)
MIN_PRESSURE_MATCHES = None    # Step 8
