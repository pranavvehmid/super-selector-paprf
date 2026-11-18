"""Compare the granularity of matched cells with unchanged pressure labels."""

import json
from collections import defaultdict
from statistics import correlation

import matplotlib.pyplot as plt
import numpy as np

from audit_paprf_context import TABLES, add, collect, consolidate, midranks, rank, save
from build_paprf_v2 import CELL_CUTOFF, DRAWS, MIN_VALID, SEED, resample, score_draws
from run_paprf_phase2 import ROOT, Totals, rows

DESIGNS = {
    "fine_v2": (0, 1, 2),
    "phase_family_v3": (1, 2),
    "innings_phase": (0, 1),
}


def bucket_pair():
    return Totals(), Totals()


def combine_cells(clusters, dimensions):
    match_cells = defaultdict(lambda: np.zeros(4, dtype=int))
    for (role, player, fine_cell, bucket, match), values in clusters["counts"].items():
        cell = tuple(fine_cell[i] for i in dimensions)
        match_cells[role, player, cell, bucket, match] += values
    pooled = defaultdict(lambda: defaultdict(bucket_pair))
    periods = {period: defaultdict(lambda: defaultdict(bucket_pair)) for period in ("early", "late")}
    evidence = defaultdict(lambda: defaultdict(list))
    for (role, player, cell, bucket, match), values in match_cells.items():
        key = role, player
        add(pooled[key][cell][bucket], match, *(int(v) for v in values))
        add(periods[clusters["periods"][match]][key][cell][bucket], match, *(int(v) for v in values))
        evidence[key][cell, bucket].append((match, values))
    return pooled, periods, evidence


def fit(cells, role, minimum_balls, minimum_matches):
    records, support = [], {}
    for (record_role, player), groups in sorted(cells.items()):
        if record_role != role:
            continue
        kept = [(key, o, p) for key, (o, p) in sorted(groups.items()) if min(o.balls, p.balls) >= CELL_CUTOFF]
        value = consolidate(role, kept, minimum_balls, minimum_matches)
        if value:
            support[player] = [key for key, _, _ in kept]
            records.append(dict(player_id=player, **value))
    for record in records:
        record.update({f"delta_{i}": delta for i, delta in enumerate(record["deltas"], 1)})
    return records, support, rank(records, role)


def temporal_check(periods, role):
    early, _, _ = fit(periods["early"], role, 30, 3)
    late, _, _ = fit(periods["late"], role, 30, 3)
    a = {row["player_id"]: row["score"] for row in early}
    b = {row["player_id"]: row["score"] for row in late}
    common = sorted(a.keys() & b.keys(), key=int)
    ranks = [midranks([period[player] for player in common]) for period in (a, b)]
    rho = correlation(*ranks) if all(len(set(r)) > 1 for r in ranks) else None
    overlap = set(list(a)[:10]) & set(list(b)[:10])
    summary = dict(early_eligible=len(a), late_eligible=len(b), common_eligible=len(common),
                   spearman=rho, shared_top10=len(overlap))
    records = [dict(window=window, **r) for window, cohort in (("early", early), ("late", late)) for r in cohort]
    return summary, records


def assess(pooled, evidence, role, index, weights, names, old):
    points, support, peers = fit(pooled, role, 60, 6)
    records = []
    for point in points:
        player = point["player_id"]
        draws = score_draws(role, support[player], peers, evidence[role, player], index, weights)
        quantiles = [round(float(q), 6) for q in np.quantile(draws, [.1, .5, .9])] if len(draws) else [None] * 3
        records.append(dict(
            name=names.get(player, player), v2_rank=old.get(player, {}).get("research_rank"),
            **point, valid_draws=len(draws), p10=quantiles[0], p50=quantiles[1], p90=quantiles[2],
            research_rank=None,
        ))
    qualified = sorted((r for r in records if r["valid_draws"] / DRAWS >= MIN_VALID),
                       key=lambda r: (-r["p10"], int(r["player_id"])))
    for i, record in enumerate(qualified, 1):
        record["research_rank"] = i
    if len(qualified) < 10:
        raise ValueError(f"Insufficient eligible players for {role}")
    return records, qualified, peers


def plot(designs):
    names = ["Fine v2", "Phase + family v3", "Innings + phase"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")
    x = np.arange(len(names))
    for offset, role, color in [(-.18, "batter", "#b70065"), (.18, "bowler", "#534286")]:
        stats = [designs[key][role] for key in DESIGNS]
        axes[0].bar(x + offset, [r["bootstrap_eligible"] for r in stats], .36, color=color, label=role.title() + "s")
        axes[1].bar(x + offset, [r["temporal"]["spearman"] for r in stats], .36, color=color)
    for axis in axes:
        axis.set_xticks(x, names, rotation=10)
        axis.grid(axis="y", alpha=.2)
        axis.axhline(0, color="#bbbbbb", linewidth=.8)
    axes[0].set(ylabel="Players passing 95% valid draws", title="Coverage after whole-match resampling")
    axes[1].set(ylabel="Spearman rank correlation", title="Repeatability across chronological halves", ylim=(-1, 1))
    axes[0].legend()
    fig.savefig(ROOT / "outputs/figures/paprf_v3_granularity.png", dpi=180)
    plt.close(fig)


def main():
    clusters = {"families": {}, "periods": {}, "counts": defaultdict(lambda: [0, 0, 0, 0])}
    _, _, source = collect(clusters)
    index, weights = resample(clusters["families"])
    names = {r["player_id"]: r["player_name"] for r in rows(TABLES / "supplied_data_candidate_universe.csv")}
    previous = json.loads((ROOT / "work/paprf_v2_validation.json").read_text(encoding="utf-8"))
    old = {role: {r["player_id"]: r for r in previous["roles"][role]["top10"]} for role in ("batter", "bowler")}
    designs, ledger, temporal_ledger = {}, [], []
    for design, dimensions in DESIGNS.items():
        pooled, periods, evidence = combine_cells(clusters, dimensions)
        designs[design] = {}
        for role in old:
            records, qualified, peers = assess(pooled, evidence, role, index, weights, names, old[role])
            top = qualified[:10]
            top_ids = {r["player_id"] for r in top}
            if design == "fine_v2" and [(r["player_id"], r["p10"]) for r in top] != [
                (r["player_id"], r["p10"]) for r in old[role].values()
            ]:
                raise ValueError(f"{role} does not reproduce v2 on fine cells")
            temporal, temporal_rows = temporal_check(periods, role)
            qualified_ids = {r["player_id"] for r in qualified}
            matched_ids = {r["player_id"] for r in records}
            dropped = [
                dict(player_id=pid, name=r["name"], v2_rank=r["research_rank"],
                     reason="Outside top ten" if pid in qualified_ids else
                     "Too few valid draws" if pid in matched_ids else "Insufficient matched support")
                for pid, r in old[role].items() if pid not in top_ids
            ]
            designs[design][role] = dict(matched_eligible=len(records), bootstrap_eligible=len(qualified),
                                         shared_with_v2=len(old[role].keys() & top_ids), top10=top,
                                         v2_departures=dropped, peer_mean_and_sample_sd=peers, temporal=temporal)
            ledger.extend(dict(design=design, role=role, **r) for r in records)
            temporal_ledger.extend(dict(design=design, role=role, **r) for r in temporal_rows)
            if design == "phase_family_v3":
                save(f"../rankings/paprf_{role}s_v3.csv", top)
    save("paprf_v3_granularity_ledger.csv", ledger)
    save("paprf_v3_temporal_ledger.csv", temporal_ledger)
    report = dict(source=source, draws=DRAWS, seed=SEED, minimum_valid=MIN_VALID, cell_cutoff=CELL_CUTOFF,
                  designs=designs)
    (ROOT / "work/paprf_v3_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    plot(designs)
    print("Wrote PAPRF v3 granularity and repeatability evidence after exact v2 replay.")


if __name__ == "__main__":
    main()
