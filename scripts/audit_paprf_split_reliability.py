"""Estimate repeatability across disjoint, date-interleaved match halves."""

import json
from collections import defaultdict
from statistics import correlation

import matplotlib.pyplot as plt
import numpy as np

from audit_paprf_context import add, collect, midranks, save
from build_paprf_v3 import bucket_pair
from build_paprf_v4 import CAP, LAMBDA, measure, normalise
from run_paprf_phase2 import ROOT
from rrselect.reliability import SHRINKAGE_PRIOR_BALLS

SEED = 20261119
SPLITS = 32
PERMUTATIONS = 200
GATES = {"primary": (30, 3), "strict": (60, 6)}
ROLES = ("batter", "bowler")
OUTCOMES = ("composite", "rate", "dots", "event")


def split_matches(strata, rng):
    assignment = {}
    for key in sorted(strata):
        match_ids = rng.permutation(sorted(strata[key], key=int))
        first = rng.integers(2)
        for i, match in enumerate(match_ids):
            assignment[match] = int((i + first) % 2)
    return assignment


def rollup(match_counts, assignment):
    halves = [defaultdict(lambda: defaultdict(bucket_pair)) for _ in range(2)]
    for (role, player, cell, bucket, match), counts in match_counts.items():
        add(halves[assignment[match]][role, player][cell][bucket], match, *counts)
    return halves


def score_halves(halves, role, peer):
    result = []
    for half in halves:
        records, _ = measure(half, role, LAMBDA, *GATES["primary"])
        by_id = {}
        for row in records:
            signed = normalise(row.pop("deltas"), peer, role, CAP)
            n = row["pressure_balls"]
            score = round(float(signed.mean()) * n / (n + SHRINKAGE_PRIOR_BALLS), 6)
            by_id[row["player_id"]] = row | dict(zip(OUTCOMES, [score, *map(float, signed)]))
        result.append(by_id)
    return result


def passes(row, balls, matches):
    return min(row["ordinary_balls"], row["pressure_balls"]) >= balls and min(
        row["ordinary_matches"], row["pressure_matches"]
    ) >= matches


def rho(x, y):
    a, b = midranks(x), midranks(y)
    return correlation(a, b) if len(set(a)) > 1 and len(set(b)) > 1 else None


def null_correlations(x, y, full_exposure, rng):
    a, b = np.asarray(midranks(x)), np.asarray(midranks(y))
    a, b = a - a.mean(), b - b.mean()
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    if denominator == 0:
        raise ValueError("A composite ranking has no variation")
    groups = np.array_split(np.argsort(full_exposure, kind="stable"), 3)
    draws = np.empty((PERMUTATIONS, len(a)))
    for i in range(PERMUTATIONS):
        for group in groups:
            draws[i, group] = b[rng.permutation(group)]
    return draws @ a / denominator


def quantiles(values):
    return [float(v) for v in np.quantile(values, [.1, .5, .9])]


def compare(scores, gate, exposure, rng):
    first, second = ({pid: row for pid, row in by_id.items() if passes(row, *gate)} for by_id in scores)
    ids = sorted(first.keys() & second.keys(), key=int)
    if len(ids) < 10:
        raise ValueError("Fewer than ten common eligible players in a split")
    one = [first[pid]["composite"] for pid in ids]
    two = [second[pid]["composite"] for pid in ids]
    draws = null_correlations(one, two, [exposure.get(pid, 0) for pid in ids], rng)
    actual = rho(one, two)
    top = [set(sorted(ids, key=lambda pid: (-half[pid]["composite"], int(pid)))[:10]) for half in (first, second)]
    record = dict(
        half_a_eligible=len(first), half_b_eligible=len(second), common_players=len(ids),
        shared_top10=len(top[0] & top[1]), random_overlap_reference=100 / len(ids),
        null_p10=float(np.quantile(draws, .1)), null_p90=float(np.quantile(draws, .9)),
        above_null_p90=bool(actual > np.quantile(draws, .9)),
    )
    for key in OUTCOMES:
        record[f"{key}_rho"] = rho([first[pid][key] for pid in ids], [second[pid][key] for pid in ids])
    return record, draws


def chart(records, full_null):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained", sharey=True)
    for role, axis in zip(ROLES, axes):
        observed = [[r["composite_rho"] for r in records if r["role"] == role and r["gate"] == gate] for gate in GATES]
        null = [full_null[role, gate] for gate in GATES]
        for values, offset, colour, label in ((observed, -.16, "#af0067", "Observed splits"),
                                              (null, .16, "#72649b", "Within-exposure shuffle")):
            for pos, data in enumerate(values):
                lo, med, hi = quantiles(data)
                axis.vlines(pos + offset, lo, hi, color=colour, linewidth=4, alpha=.65)
                axis.scatter(pos + offset, med, color=colour, label=label if pos == 0 else None, zorder=3)
        axis.axhline(0, color="#777777", linewidth=.8)
        axis.set(xticks=[0, 1], xticklabels=["30 balls / 3 matches", "60 balls / 6 matches"],
                 title=role.title() + "s", ylim=(-.55, .55))
        axis.grid(axis="y", alpha=.18)
    axes[0].set_ylabel("Split-half Spearman correlation")
    axes[1].legend(fontsize=8)
    fig.suptitle("PAPRF v4 measurement repeatability · median and 10th–90th percentile")
    fig.savefig(ROOT / "outputs/figures/paprf_split_reliability.png", dpi=180)
    plt.close(fig)


def main():
    clusters = {"families": {}, "dates": {}, "counts": defaultdict(lambda: [0, 0, 0, 0])}
    _, _, source = collect(clusters, striker_dismissals_only=True)
    strata = defaultdict(list)
    for match, family in clusters["families"].items():
        strata[family, clusters["dates"][match][:4]].append(match)
    model = json.loads((ROOT / "work/paprf_v4_validation.json").read_text(encoding="utf-8"))
    if source["inputs"] != model["source"]["inputs"]:
        raise ValueError("v4 peer scales refer to different source inputs")
    # Exposure for the null uses full-sample opportunities for every observed player.
    exposure = {role: defaultdict(int) for role in ROLES}
    for (role, pid, _, bucket, _), counts in clusters["counts"].items():
        if bucket:
            exposure[role][pid] += counts[1]
    splits_rng, null_rng = [np.random.default_rng(s) for s in np.random.SeedSequence(SEED).spawn(2)]
    records, memberships, player_ledger, full_null = [], [], [], defaultdict(list)
    for split in range(1, SPLITS + 1):
        assignment = split_matches(strata, splits_rng)
        halves = rollup(clusters["counts"], assignment)
        memberships.extend(dict(split=split, match_id=match, half=half) for match, half in sorted(assignment.items()))
        for role in ROLES:
            reference = model["roles"][role]
            peer = (np.asarray(reference["peer_means"]), np.asarray(reference["peer_sample_sd"]))
            scores = score_halves(halves, role, peer)
            for half, by_id in enumerate(scores):
                player_ledger.extend(dict(split=split, role=role, half=half,
                                          strict_eligible=passes(row, *GATES["strict"]), **row)
                                     for row in by_id.values())
            for gate, thresholds in GATES.items():
                metrics, draws = compare(scores, thresholds, exposure[role], null_rng)
                records.append(dict(split=split, role=role, gate=gate, **metrics))
                full_null[role, gate].extend(draws)
    roles = {}
    for role in ROLES:
        roles[role] = {}
        for gate in GATES:
            subset = [r for r in records if r["role"] == role and r["gate"] == gate]
            key_metrics = ("common_players", "shared_top10", "random_overlap_reference",
                           *(f"{m}_rho" for m in OUTCOMES))
            spread = {key: quantiles([r[key] for r in subset if r[key] is not None]) for key in key_metrics}
            half_r = spread["composite_rho"][1]
            roles[role][gate] = dict(
                summary_p10_p50_p90=spread, shuffle_rho_p10_p50_p90=quantiles(full_null[role, gate]),
                splits_above_own_null_p90=sum(r["above_null_p90"] for r in subset),
                full_sample_spearman_brown_heuristic=2 * half_r / (1 + half_r) if half_r >= 0 else None,
            )
    save("paprf_split_reliability.csv", records)
    save("paprf_split_match_membership.csv", memberships)
    save("paprf_split_player_ledger.csv", player_ledger)
    report = dict(source=source, seed=SEED, splits=SPLITS, permutations_per_split=PERMUTATIONS,
                  strata={f"{family}_{year}": len(ids) for (family, year), ids in sorted(strata.items())},
                  roles=roles)
    (ROOT / "work/paprf_split_reliability.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    chart(records, full_null)
    print("Wrote split-half results, exact match memberships, null comparison and figure.")


if __name__ == "__main__":
    main()
