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

# --- Open decisions: leave as None until recorded in docs/decisions.md -------------------------
COMPETITION_SCOPE = None       # D-001
PRESSURE_BANDS = None          # Step 5
MIN_PRESSURE_BALLS = None      # Step 8 (set after inspecting distributions)
MIN_PRESSURE_MATCHES = None    # Step 8
SUBMITTED_LENS = None          # D-003: "A" | "B" | "consensus"
