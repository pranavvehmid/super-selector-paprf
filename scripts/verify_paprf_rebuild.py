"""Recompute all ranking versions in a clean temporary tree from organiser CSVs."""

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parents[1]
RAW = ("ball_by_ball", "matches", "competitions", "teams", "playing_eleven", "competition_team_player_mapping")
STEPS = (
    "audit_data_quality", "validate_state_rules", "reconstruct_state", "validate_reconstructed_state",
    "apply_pressure_definition", "validate_pressure_definition", "build_player_metrics", "validate_player_metrics",
    "build_baselines", "validate_baselines", "build_reliability_scores", "freeze_rankings", "validate_rankings",
    "build_candidate_universe", "run_paprf_phase2", "audit_paprf_context", "build_paprf_v2", "build_paprf_v3",
    "build_paprf_v4", "validate_paprf_forward", "audit_paprf_split_reliability",
    "build_paprf_role_profiles", "validate_paprf_role_profiles", "build_paprf_unified_ranking",
    "build_paprf_discipline_rankings",
)
CHECKS = (
    "data/processed/metric_attribution_deliveries.csv",
    *(f"outputs/rankings/{prefix}_{role}_{version}.csv"
      for prefix, version in (("lens_a", "v1"), ("paprf", "v2"), ("paprf", "v3"), ("paprf", "v4"))
      for role in ("batters", "bowlers")),
    *(f"outputs/tables/paprf_v4_{name}.csv" for name in ("rank_ledger", "sensitivity", "temporal", "cells", "progression")),
    "work/paprf_v4_validation.json",
    "work/paprf_forward_validation.json", "work/paprf_split_reliability.json",
    "work/paprf_contextual_roles.json", "work/paprf_role_profile_validation.json",
    "work/paprf_unified_ranking.json", "work/paprf_contextual_discipline_v2.json",
    "outputs/rankings/paprf_contextual_role_top10_v1.csv",
    "outputs/rankings/paprf_unified_top10_v1.csv",
    "outputs/rankings/paprf_contextual_batters_top10_v2.csv",
    "outputs/rankings/paprf_contextual_bowlers_top10_v2.csv",
)


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def records(root, file):
    with (root / file).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_scalar_scores(root):
    """Recalculate every point score from cell numerators with scalar arithmetic."""
    groups = defaultdict(list)
    for cell in records(root, "outputs/tables/paprf_v4_cells.csv"):
        groups[cell["role"], cell["player_id"]].append(cell)
    saved = records(root, "outputs/tables/paprf_v4_rank_ledger.csv")
    for role in ("batter", "bowler"):
        expected = {}
        for (record_role, player), cells in groups.items():
            if record_role != role:
                continue
            numerators = [0.0, 0.0, 0.0]
            denominator = 0
            for row in cells:
                a, b = (int(row[f"{bucket}_balls"]) for bucket in ("ordinary", "pressure"))
                effective_n = a * b / (a + b)
                for j, metric in enumerate(("runs", "dots", "events")):
                    pressure = int(row[f"pressure_{metric}"]) / b
                    ordinary = int(row[f"ordinary_{metric}"]) / a
                    factor = 6 if j == 0 and role == "bowler" else 1
                    numerators[j] += factor * (pressure - ordinary) * effective_n / (effective_n + 12) * b
                denominator += b
            expected[player] = [value / denominator for value in numerators], denominator
        columns = list(zip(*(deltas for deltas, _ in expected.values())))
        scales = [(mean(c), stdev(c)) for c in columns]
        signs = (1, -1, -1) if role == "batter" else (-1, 1, 1)
        for row in (r for r in saved if r["role"] == role):
            values, n = expected[row["player_id"]]
            z = [max(-3.0, min(3.0, sign * (dp - mu) / sd)) if sd else 0.0
                 for dp, (mu, sd), sign in zip(values, scales, signs)]
            point = round(mean(z) * n / (n + 60), 6)
            if point != float(row["point_score"]) or n != int(row["pressure_balls"]):
                raise ValueError(f"Independent point-score mismatch for {role} {row['player_id']}")
        qualified = [r for r in saved if r["role"] == role and int(r["valid_draws"]) >= 475]
        ordered = sorted(qualified, key=lambda r: (-float(r["p10"]), int(r["player_id"])))
        top = records(root, f"outputs/rankings/paprf_{role}s_v4.csv")
        if [r["player_id"] for r in ordered[:10]] != [r["player_id"] for r in top]:
            raise ValueError(f"Independent ordering mismatch for {role}")
    return len(saved)


def main():
    with tempfile.TemporaryDirectory(prefix="paprf-clean-replay-") as temp:
        root = Path(temp)
        for folder in ("data/raw", "work", "outputs/rankings", "outputs/figures", "outputs/tables"):
            (root / folder).mkdir(parents=True)
        for name in RAW:
            shutil.copyfile(ROOT / f"data/raw/{name}.csv", root / f"data/raw/{name}.csv")
        shutil.copytree(ROOT / "src", root / "src", ignore=shutil.ignore_patterns("__pycache__"))
        (root / "scripts").mkdir()
        for script in STEPS:
            name = f"scripts/{script}.py"
            shutil.copyfile(ROOT / name, root / name)
            subprocess.run([sys.executable, str(root / name)], cwd=root, check=True)
        results = []
        for file in CHECKS:
            current, rebuilt = digest(ROOT / file), digest(root / file)
            results.append(dict(file=file, published_sha256=current, rebuilt_sha256=rebuilt, identical=current == rebuilt))
        scalar_count = verify_scalar_scores(root)
        payload = dict(steps=STEPS, compared_files=results, identical_count=sum(r["identical"] for r in results),
                       scalar_point_scores_verified=scalar_count)
        (ROOT / "work/paprf_clean_rebuild.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        if any(not r["identical"] for r in results):
            raise ValueError("Rebuild disagrees with published data. Inspect work/paprf_clean_rebuild.json")
    print(f"All {len(results)} checked files match the scratch rebuild exactly.")


if __name__ == "__main__":
    main()
