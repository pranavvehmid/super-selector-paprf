"""Integrate existing contextual role signals into a reproducible overall index."""

import json
from collections import defaultdict
from math import erf, sqrt
from statistics import mean, stdev

from audit_paprf_context import save
from build_paprf_role_profiles import WEIGHTS
from run_paprf_phase2 import ROOT, digest, rows

TABLES = ROOT / "outputs/tables"
SCENARIOS = {"unified_v1": ("primary", .10), "primary_only": ("primary", 0),
             "india_1_5": ("india_1_5", .10), "residualised_boundary": ("orthogonal_boundary", .10)}


def role_scores(records, scenario):
    groups = defaultdict(list)
    for r in records:
        if r["scenario"] != scenario:
            continue
        role = r["role"]
        z = [float(r[key]) for key in ("signed_z_rate", "signed_z_boundary", "signed_z_event")]
        c = sum(w*x for w, x in zip(WEIGHTS[role], z))
        n = int(r["scored_balls"])
        reliability = n / (n + 120)
        if abs(c * reliability - float(r["score"])) > .00000051:
            raise ValueError(f"Role score does not reconcile for {role} {r['player_id']}")
        groups[role].append(dict(
            player_id=r["player_id"], role=role, name=r["name"], role_rank=int(r["rank"]),
            role_score=float(r["score"]), unshrunk=c, balls=n, matches=int(r["scored_matches"]),
            india_balls=int(r["india_scored_balls"]), retention=reliability, signed_z=z,
            ordinary_balls=int(r["ordinary_balls"]), pressure_balls=int(r["pressure_balls"]),
            pressure_rate_lift=float(r["pressure_rate_lift"]) if r["pressure_rate_lift"] else None,
        ))
    lookup, scales = {}, {}
    for role, pool in groups.items():
        values = [r["unshrunk"] for r in pool]
        mu, sd = mean(values), stdev(values) if len(values) > 1 else 0
        scales[role] = dict(mean=mu, sample_sd=sd, eligible=len(pool))
        for r in pool:
            z = (r["unshrunk"] - mu) / sd if sd else 0
            q = 50 * (1 + erf(z / sqrt(2)))
            r.update(role_z=z, reference=q, adjusted=50 + r["retention"] * (q - 50))
            lookup[r["player_id"], role] = r
    return lookup, scales


def primary_assignments(splits, lookup):
    players = defaultdict(list)
    for r in splits:
        if r["dimension"] == "overall":
            players[r["player_id"]].append(r)
    output = []
    for pid, choices in sorted(players.items(), key=lambda item: int(item[0])):
        warmup_only = not any(int(r["scored_balls"]) for r in choices)
        primary = min(choices, key=lambda r: (-int(r["balls"] if warmup_only else r["scored_balls"]),
                                               -int(r["scored_matches"]),
                                               -lookup.get((pid, r["role"]), {}).get("unshrunk", -10), r["role"]))
        n = int(primary["scored_balls"])
        total = sum(int(r["scored_balls"]) for r in choices)
        output.append(dict(player_id=pid, name=primary["player_name"], primary_role=primary["role"],
                           primary_balls=n, primary_matches=int(primary["scored_matches"]),
                           primary_share=n / total if total else None,
                           observed_roles=len(choices), eligible=(pid, primary["role"]) in lookup,
                           reason="" if (pid, primary["role"]) in lookup else "Primary role below 60 scored balls or six matches"))
    return output


def aggregate(assignments, lookup, coefficient):
    ranked = []
    by_player = defaultdict(list)
    for (pid, _), role in lookup.items():
        by_player[pid].append(role)
    for a in assignments:
        if not a["eligible"]:
            continue
        pid, primary_id = a["player_id"], a["primary_role"]
        primary = lookup[pid, primary_id]
        alternatives = [r for r in by_player[pid] if r["role"] != primary_id]
        for r in alternatives:
            r["credit"] = coefficient * min(1, r["balls"] / primary["balls"]) * max(0, r["adjusted"] - 50)
        secondary = min(alternatives, key=lambda r: (-r["credit"], -r["balls"], r["role"])) if alternatives else None
        credit = secondary["credit"] if secondary else 0.0
        score = round(min(100, primary["adjusted"] + credit), 6)
        ranked.append(dict(**a, primary_reference=primary["reference"], primary_adjusted=primary["adjusted"],
                           primary_retention=primary["retention"], secondary_role=secondary["role"] if secondary else None,
                           secondary_balls=secondary["balls"] if secondary else None,
                           secondary_adjusted=secondary["adjusted"] if secondary else None,
                           secondary_credit=credit, score=score))
    ranked.sort(key=lambda r: (-r["score"], int(r["player_id"])))
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
    return ranked


def main():
    files = [TABLES / f"paprf_role_{name}.csv" for name in
             ("profile_scores", "profile_splits", "profile_trends", "bootstrap_ledger")]
    records, splits, trends, bootstrap = (list(rows(file)) for file in files)
    assignments, base, summaries, role_evidence = None, None, {}, None
    index = {}
    for label, (scenario, coefficient) in SCENARIOS.items():
        lookup, scales = role_scores(records, scenario)
        if assignments is None:
            assignments = primary_assignments(splits, lookup)
        ranked = aggregate(assignments, lookup, coefficient)
        ids = [r["player_id"] for r in ranked[:10]]
        if label == "unified_v1":
            base = set(ids)
            role_evidence = lookup
        summaries[label] = dict(top10_ids=ids, overlap=len(base & set(ids)), scales=scales, coefficient=coefficient)
        index[label] = ranked
    original = index["unified_v1"]
    original_ranks = {r["player_id"]: r["rank"] for r in original}
    original_top = {r["player_id"] for r in original[:10]}
    for label, group in index.items():
        current_top = {r["player_id"] for r in group[:10]}
        summaries[label].update(
            max_rank_shift=max(abs(r["rank"] - original_ranks[r["player_id"]]) for r in group),
            entered=[r["name"] for r in group[:10] if r["player_id"] not in original_top],
            left=[r["name"] for r in original[:10] if r["player_id"] not in current_top],
        )
    save("paprf_unified_assignments.csv", assignments)
    save("paprf_unified_score_ledger.csv", [dict(scenario=label, **r) for label, group in index.items() for r in group])
    save("../rankings/paprf_unified_top10_v1.csv", original[:10])

    profiles = defaultdict(list)
    shares = {(r["player_id"], r["role"]): float(r["top10_share"]) for r in bootstrap}
    trend = {(r["player_id"], r["role"]): r for r in trends}
    ids = {r["player_id"] for r in original}
    annual = defaultdict(list)
    geography = defaultdict(dict)
    for r in splits:
        pid, role = r["player_id"], r["role"]
        if pid not in ids:
            continue
        key = pid, role
        if r["dimension"] == "year":
            annual[key].append(dict(year=r["group"], balls=int(r["balls"]), scored_balls=int(r["scored_balls"]),
                                    raw_rate=float(r["strike_rate_or_economy"]) if r["strike_rate_or_economy"] else None,
                                    run_residual=float(r["runs_residual"]) if r["runs_residual"] else None))
        elif r["dimension"] == "venue_country_group":
            geography[key][r["group"]] = dict(balls=int(r["scored_balls"]),
                                              run_residual=float(r["runs_residual"]) if r["runs_residual"] else None)
    for key, r in role_evidence.items():
        pid, role = key
        if pid in ids:
            profiles[pid].append({**r, "bootstrap_top10_share": shares.get(key), "trend": trend.get(key),
                                  "annual": annual[key], "geography": geography[key]})
    result = dict(
        version="unified_v1", source_hashes={p.relative_to(ROOT).as_posix(): digest(p) for p in files},
        observed=len(assignments), eligible=len(original), top10=original[:10], ranked=original,
        unranked=[a for a in assignments if not a["eligible"]],
        methods=summaries, profiles=dict(profiles),
    )
    (ROOT / "work/paprf_unified_ranking.json").write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Unified index ranks {len(original)} of {len(assignments)} observed players.")


if __name__ == "__main__":
    main()
