"""Validate training-only PAPRF scores in three disjoint future windows."""

import json
from collections import defaultdict
from statistics import correlation

import matplotlib.pyplot as plt
import numpy as np

from audit_paprf_context import add, collect, midranks, save
from build_paprf_v2 import DRAWS, MIN_VALID, SEED, resample
from build_paprf_v3 import bucket_pair
from build_paprf_v4 import CAP, LAMBDA, bootstrap, fit, measure, normalise
from run_paprf_phase2 import ROOT

PREDICTORS = ("v4_p10", "v4_point", "pooled_point", "pressure_volume")
LABELS = ("v4 p10", "v4 point", "Pooled point", "Pressure volume")


def rollup(clusters, match_ids, include_pooled=False):
    fine = defaultdict(lambda: defaultdict(bucket_pair))
    pooled = defaultdict(lambda: defaultdict(bucket_pair))
    evidence = defaultdict(lambda: defaultdict(list))
    for (role, player, cell, bucket, match), counts in clusters["counts"].items():
        if match not in match_ids:
            continue
        key = role, player
        add(fine[key][cell][bucket], match, *counts)
        if include_pooled:
            add(pooled[key][("pooled",)][bucket], match, *counts)
            evidence[key][cell, bucket].append((match, counts))
    return fine, pooled, evidence


def ordered(scores, ids=None):
    return sorted(scores.keys() if ids is None else ids, key=lambda pid: (-scores[pid], int(pid)))


def spearman(predictions, actual):
    x, y = midranks(predictions), midranks(actual)
    return correlation(x, y) if len(set(x)) > 1 and len(set(y)) > 1 else None


def compare(role, fold, train, test, index, weights):
    fine, pooled, evidence = train
    fine_fit, support, peer = fit(fine, role, LAMBDA, CAP, 3)
    pooled_fit, _, pooled_peer = fit(pooled, role, 0, CAP, 3)
    predictions = {
        "v4_p10": {},
        "v4_point": {r["player_id"]: r["point_score"] for r in fine_fit},
        "pooled_point": {r["player_id"]: r["point_score"] for r in pooled_fit},
        "pressure_volume": {r["player_id"]: r["pressure_balls"] for r in fine_fit},
    }
    valid_draws = {}
    for r in fine_fit:
        player = r["player_id"]
        draw = bootstrap(role, support[player], evidence[role, player], peer, index, weights)
        valid_draws[player] = len(draw)
        if len(draw) / DRAWS >= MIN_VALID:
            predictions["v4_p10"][player] = round(float(np.quantile(draw, .1)), 6)
    measured, _ = measure(test, role, LAMBDA, 30, 3)
    outcomes = {}
    for row in measured:
        z = normalise(row["deltas"], peer, role, CAP)
        outcomes[row["player_id"]] = row, float(z.mean()), float(z[0])
    common = sorted(set(outcomes).intersection(*(p.keys() for p in predictions.values())), key=int)
    if len(common) < 10:
        raise ValueError(f"{fold} {role} has fewer than ten assessable players")
    actual = {pid: outcomes[pid][1] for pid in common}
    rate = {pid: outcomes[pid][2] for pid in common}
    actual_top = ordered(actual)[:10]
    comparisons = {}
    for key, predicted in predictions.items():
        original_top = ordered(predicted)[:10]
        common_top = ordered(predicted, common)[:10]
        comparisons[key] = dict(
            training_eligible=len(predicted), original_top10_ids=original_top,
            original_top10_assessable=len(set(original_top) & outcomes.keys()),
            spearman=spearman([predicted[pid] for pid in common], [actual[pid] for pid in common]),
            rate_only_spearman=spearman([predicted[pid] for pid in common], [rate[pid] for pid in common]),
            top10_overlap=len(set(common_top) & set(actual_top)),
        )
    ledger = []
    for pid in sorted(set(outcomes).union(*(p.keys() for p in predictions.values())), key=int):
        observed = outcomes.get(pid)
        row = observed[0] if observed else {}
        ledger.append(dict(
            fold=fold, role=role, player_id=pid, common_evaluation=pid in actual,
            **{key: predicted.get(pid) for key, predicted in predictions.items()},
            training_valid_draws=valid_draws.get(pid),
            test_ordinary_balls=row.get("ordinary_balls"), test_pressure_balls=row.get("pressure_balls"),
            test_ordinary_matches=row.get("ordinary_matches"), test_pressure_matches=row.get("pressure_matches"),
            test_delta_rate=row["deltas"][0] if observed else None,
            test_delta_dots=row["deltas"][1] if observed else None,
            test_delta_event=row["deltas"][2] if observed else None,
            test_pressure_lift=observed[1] if observed else None, test_rate_lift=observed[2] if observed else None,
        ))
    return dict(
        test_eligible=len(outcomes), common_players=len(common), chance_top10_overlap=100 / len(common),
        predictors=comparisons,
        test_top10_ids=actual_top, v4_training_mean=peer[0].tolist(), v4_training_sd=peer[1].tolist(),
        pooled_training_mean=pooled_peer[0].tolist(), pooled_training_sd=pooled_peer[1].tolist(),
    ), ledger


def plot(report):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), layout="constrained", sharey=True)
    colours = ("#b20065", "#e281b5", "#4a3d83", "#708194")
    x = np.arange(len(report))
    for role, axis in zip(("batter", "bowler"), axes):
        for i, (key, label, colour) in enumerate(zip(PREDICTORS, LABELS, colours)):
            values = [fold["roles"][role]["predictors"][key]["spearman"] for fold in report]
            axis.bar(x + (i - 1.5) * .19, values, .18, label=label, color=colour)
        axis.axhline(0, color="#352849", linewidth=.8)
        axis.set(xticks=x, xticklabels=[fold["fold"] for fold in report], ylim=(-1, 1), title=role.title() + "s")
        axis.grid(axis="y", alpha=.2)
    axes[0].set_ylabel("Spearman correlation with later pressure lift")
    axes[1].legend(fontsize=8, loc="upper right")
    fig.suptitle("PAPRF retrospective forward validation")
    fig.savefig(ROOT / "outputs/figures/paprf_forward_validation.png", dpi=180)
    plt.close(fig)


def main():
    clusters = {"families": {}, "dates": {}, "counts": defaultdict(lambda: [0, 0, 0, 0])}
    _, _, source = collect(clusters, striker_dismissals_only=True)
    dates = clusters["dates"]
    match_order = sorted(dates, key=lambda m: (dates[m], int(m)))
    cutoffs = [dates[match_order[len(match_order) * k // 4]] for k in (1, 2, 3)]
    report, ledger = [], []
    earlier_tests = set()
    for fold_number, (start, stop) in enumerate(zip(cutoffs, cutoffs[1:] + ["9999-12-31"]), 1):
        train_ids = {m for m, date in dates.items() if date < start}
        test_ids = {m for m, date in dates.items() if start <= date < stop}
        if train_ids & test_ids or earlier_tests & test_ids or not train_ids or not test_ids:
            raise ValueError("Invalid chronological split")
        earlier_tests.update(test_ids)
        index, weights = resample({m: clusters["families"][m] for m in train_ids})
        train = rollup(clusters, train_ids, include_pooled=True)
        test, _, _ = rollup(clusters, test_ids)
        result = dict(fold=f"Fold {fold_number}", train_end=max(dates[m] for m in train_ids),
                      test_start=start, test_end=max(dates[m] for m in test_ids),
                      training_matches=len(train_ids), test_matches=len(test_ids), roles={})
        for role in ("batter", "bowler"):
            result["roles"][role], player_rows = compare(role, result["fold"], train, test, index, weights)
            ledger.extend(player_rows)
        report.append(result)
    save("paprf_forward_validation_ledger.csv", ledger)
    out = dict(source=source, seed=SEED, bootstrap_draws=DRAWS, folds=report)
    (ROOT / "work/paprf_forward_validation.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    plot(report)
    print("Wrote forward-validation scores, coverage, and benchmark comparisons.")


if __name__ == "__main__":
    main()
