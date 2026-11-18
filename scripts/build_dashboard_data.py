"""Export reviewed aggregate evidence for the static PAPRF dashboard."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs/tables"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main():
    names = {r["player_id"]: r["player_name"] for r in read_csv(TABLES / "supplied_data_candidate_universe.csv")}
    ledger = read_csv(TABLES / "paprf_phase2_score_ledger.csv")
    rankings = {}
    contexts = {}
    for role in ("batter", "bowler"):
        rankings[role] = read_csv(ROOT / f"outputs/rankings/lens_a_{role}s_v1.csv")
        contexts[role] = read_csv(TABLES / f"{role}_context_metrics.csv")
        for row in contexts[role]:
            names[row["player_id"]] = row["player_name"]
        replay = [r for r in ledger if r["role"] == role and r["scenario"] == "v1_equal"][:10]
        if [(r["player_id"], float(r["score"])) for r in replay] != [
            (r["player_id"], float(r["reliability_signal"])) for r in rankings[role]
        ]:
            raise ValueError(f"{role} rankings and replay diverged")

    model = read_json("work/paprf_phase2_sensitivity.json")
    audit = read_json("work/paprf_phase1_audit.json")
    distribution = read_csv(TABLES / "paprf_pressure_distribution.csv")
    if sum(int(r["delivery_count"]) for r in distribution) != audit["delivery_rows"]:
        raise ValueError("Pressure distribution and audit totals diverged")
    data = dict(names=names, rankings=rankings, contexts=contexts, ledger=ledger,
                model=model, audit=audit, distribution=distribution,
                context_audit=read_json("work/paprf_context_audit.json"),
                research=read_json("work/paprf_v2_validation.json"),
                granularity=read_json("work/paprf_v3_validation.json"),
                regularised=read_json("work/paprf_v4_validation.json"),
                forward=read_json("work/paprf_forward_validation.json"),
                split_reliability=read_json("work/paprf_split_reliability.json"),
                role_profiles=read_json("work/paprf_contextual_roles.json"),
                role_validation=read_json("work/paprf_role_profile_validation.json"),
                unified=read_json("work/paprf_unified_ranking.json"),
                robustness=read_json("work/robustness-validation.json"))
    path = ROOT / "dashboard/evidence.js"
    path.write_text("globalThis.paprfEvidence = " + json.dumps(data, ensure_ascii=True, separators=(",", ":")) + ";\n",
                    encoding="utf-8")
    print(f"Wrote {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
