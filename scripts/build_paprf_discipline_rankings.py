"""Rebuild contextual indices separately for batting and bowling roles."""

import json

from audit_paprf_context import save
from build_paprf_unified_ranking import (
    SCENARIOS, TABLES, aggregate, evidence_profiles, primary_assignments, role_scores,
)
from run_paprf_phase2 import ROOT, digest, rows


def main():
    paths = [TABLES / f"paprf_role_{x}.csv" for x in
             ("profile_scores", "profile_splits", "profile_trends", "bootstrap_ledger")]
    records, splits, trends, bootstrap = [list(rows(p)) for p in paths]
    result, ledger, assignments_ledger = {}, [], []
    for discipline in ("batter", "bowler"):
        local_splits = [r for r in splits if r["discipline"] == discipline]
        local_records = [r for r in records if r["role"].endswith("_bowler") == (discipline == "bowler")]
        methods, historical = {}, set()
        for label, (source_scenario, coefficient) in SCENARIOS.items():
            lookup, scales = role_scores(local_records, source_scenario)
            if label == "unified_v1":
                assignments = primary_assignments(local_splits, lookup)
            ranked = aggregate(assignments, lookup, coefficient)
            if len(ranked) < 10:
                raise ValueError(f"{discipline} has fewer than ten eligible players")
            top = ranked[:10]
            ids = [r["player_id"] for r in top]
            if label == "unified_v1":
                historical = set(ids)
                primary = ranked
                primary_scores = lookup
                primary_ranks = {r["player_id"]: r["rank"] for r in ranked}
            methods[label] = dict(
                scales=scales, coefficient=coefficient, top10_ids=ids, overlap=len(historical & set(ids)),
                max_rank_shift=max(abs(r["rank"] - primary_ranks[r["player_id"]]) for r in ranked),
                entered=[r["name"] for r in top if r["player_id"] not in historical],
                left=[r["name"] for r in primary[:10] if r["player_id"] not in ids],
            )
            ledger.extend(dict(discipline=discipline, scenario=label, **r) for r in ranked)
        assignments_ledger.extend(dict(discipline=discipline, **r) for r in assignments)
        save(f"../rankings/paprf_contextual_{discipline}s_top10_v2.csv", primary[:10])
        pressure = ROOT / f"outputs/rankings/lens_a_{discipline}s_v1.csv"
        result[discipline] = dict(
            observed=len(assignments), eligible=len(primary), top10=primary[:10], ranked=primary,
            unranked=[a for a in assignments if not a["eligible"]], methods=methods,
            profiles=evidence_profiles(primary, primary_scores, local_splits, trends, bootstrap),
            pressure_submission_overlap=len(historical & {r["player_id"] for r in rows(pressure)}),
        )
        print(f"{discipline.title()}s: {len(primary)} eligible of {len(assignments)} observed.")
    save("paprf_contextual_discipline_assignments_v2.csv", assignments_ledger)
    save("paprf_contextual_discipline_scores_v2.csv", ledger)
    output = dict(version="contextual_v2_by_discipline", sources={p.relative_to(ROOT).as_posix(): digest(p) for p in paths}, lists=result)
    (ROOT / "work/paprf_contextual_discipline_v2.json").write_text(json.dumps(output, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
