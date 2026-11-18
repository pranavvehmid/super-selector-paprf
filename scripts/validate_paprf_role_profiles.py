"""Reproduce role scores, test temporal ordering and estimate match uncertainty."""

import json
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from audit_paprf_context import save
from build_paprf_role_profiles import SELECT, WEIGHTS, calculate, read_inputs
from build_paprf_v2 import DRAWS, SEED, resample
from run_paprf_phase2 import ROOT, digest
from validate_paprf_forward import spearman

CUTOFFS = ("2024-05-08", "2025-09-06", "9999-12-31")
METHODS = ("primary", "orthogonal_boundary", "runs_only", "volume")


def cohort(data, metadata, start="", stop="9999-12-31"):
    result = {}
    for player, samples in sorted(data.items(), key=lambda item: int(item[0])):
        included = [v for match, v in samples.items() if start <= metadata[match][0] < stop]
        if len(included) < 6:
            continue
        total = np.asarray(included).sum(axis=0)
        if total[3] >= 60:
            result[player] = (total[:3] / total[3], int(total[3]), len(included))
    return result


def scale(values, means, sds, signs):
    return np.clip(np.divide(values - means, sds, out=np.zeros_like(values), where=sds > 0) * signs, -3, 3)


def moments(values):
    return values.mean(axis=0), values.std(axis=0, ddof=1)


def ordered(predicted):
    return sorted(predicted, key=lambda pid: (-predicted[pid], int(pid)))


def forecast(train, test, role, start, stop):
    players = list(train)
    values = np.array([r[0] for r in train.values()])
    means, sds = moments(values)
    centred = values - means
    x, y = centred[:, 0], centred[:, 1]
    slope = float(x @ y / (x @ x)) if x @ x else 0.0
    adjusted = values.copy()
    adjusted[:, 1] -= slope * x
    ortho_mean, ortho_sd = moments(adjusted)
    signs = (-1, -1, 1) if role.endswith("_bowler") else (1, 1, -1)
    primary_z = scale(values, means, sds, signs)
    orthogonal_z = scale(adjusted, ortho_mean, ortho_sd, signs)
    weights = WEIGHTS[role]
    predictions = {}
    for i, pid in enumerate(players):
        n = train[pid][1]
        shrink = n / (n + 120)
        predictions[pid] = {
            "primary": round(float(primary_z[i] @ weights) * shrink, 6),
            "orthogonal_boundary": round(float(orthogonal_z[i] @ weights) * shrink, 6),
            "runs_only": round(float(primary_z[i, 0]) * shrink, 6), "volume": n,
        }
    common = sorted(train.keys() & test.keys(), key=int)
    target_weights = (weights[0] + weights[1], 0, weights[2])
    outcomes = {pid: scale(v[0], means, sds, signs) for pid, v in test.items()}
    actual = {pid: float(outcomes[pid] @ target_weights) for pid in common}
    rate = {pid: float(outcomes[pid][0]) for pid in common}
    comparisons = {}
    for method in METHODS:
        scores = {pid: row[method] for pid, row in predictions.items()}
        top = ordered(scores)[:10]
        common_top = ordered({pid: scores[pid] for pid in common})[:10]
        comparisons[method] = dict(
            spearman=spearman([scores[pid] for pid in common], list(actual.values())),
            runs_spearman=spearman([scores[pid] for pid in common], list(rate.values())),
            top10_overlap=len(set(common_top) & set(ordered(actual)[:10])) if len(common) > 10 else None,
            earlier_top10_assessable=len(set(top) & test.keys()), earlier_top10_size=len(top),
        )
    ledger = []
    for pid in sorted(train.keys() | test.keys(), key=int):
        outcome = outcomes.get(pid)
        pred = predictions.get(pid, dict.fromkeys(METHODS))
        ledger.append(dict(role=role, test_start=start, test_stop_exclusive=stop, player_id=pid, common=pid in actual,
                           train_balls=train[pid][1] if pid in train else None,
                           test_balls=test[pid][1] if pid in test else None,
                           test_matches=test[pid][2] if pid in test else None,
                           **pred, actual=float(outcome @ target_weights) if outcome is not None else None,
                           actual_runs=float(outcome[0]) if outcome is not None else None))
    return dict(start=start, stop_exclusive=stop, train=len(train), test=len(test), common=len(common),
                means=means.tolist(), sd=sds.tolist(), boundary_slope=slope, comparisons=comparisons), ledger


def historic_uncertainty(samples, fitted, scales, role, index, weights):
    by_id = {r["player_id"]: r for r in fitted}
    ids = sorted(by_id, key=int)
    scores = np.empty((len(ids), DRAWS))
    signs = (-1, -1, 1) if role.endswith("_bowler") else (1, 1, -1)
    means, sd = (np.asarray(scales[k]) for k in ("means", "sample_sds"))
    for i, pid in enumerate(ids):
        match_ids = list(samples[pid])
        cols = [index[match] for match in match_ids]
        totals = weights[:, cols] @ np.array([samples[pid][m] for m in match_ids])
        n = totals[:, 3]
        residual = totals[:, :3] / np.maximum(n[:, None], 1)
        z = scale(residual, means, sd, signs)
        scores[i] = np.where(n > 0, np.round((z @ WEIGHTS[role]) * n / (n + 120), 6), np.nan)
    rank_order = np.argsort(np.where(np.isnan(scores), np.inf, -scores), axis=0, kind="stable")
    inclusions = np.zeros(len(ids), dtype=int)
    for draw, order in enumerate(rank_order.T):
        qualified = [i for i in order[:10] if np.isfinite(scores[i, draw])]
        inclusions[qualified] += 1
    records = []
    for i, pid in enumerate(ids):
        qs = np.nanquantile(scores[i], [.1, .5, .9])
        r = by_id[pid]
        records.append(dict(role=role, player_id=pid, name=r["name"], point_rank=r["rank"],
                            valid_draws=int(np.isfinite(scores[i]).sum()), top10_draws=int(inclusions[i]),
                            top10_share=float(inclusions[i] / DRAWS), p10=float(qs[0]), p50=float(qs[1]), p90=float(qs[2])))
    return sorted(records, key=lambda r: r["point_rank"])


def plot(roles):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout="constrained", sharey=True)
    labels = [r.replace("_", " ").title() for r in roles]
    y = np.arange(len(labels))
    for j, axis in enumerate(axes):
        window = next(iter(roles.values()))["forward"][j]
        title = (f"{window['start']} to before {window['stop_exclusive']}"
                 if window["stop_exclusive"] != CUTOFFS[-1] else f"{window['start']} to data end")
        for method, colour, marker in (("primary", "#b30065", "o"), ("orthogonal_boundary", "#503b83", "s"),
                                         ("runs_only", "#778995", "^"), ("volume", "#bb7156", "d")):
            correlations = [r["forward"][j]["comparisons"][method]["spearman"] for r in roles.values()]
            axis.scatter([float("nan") if v is None else v for v in correlations], y,
                         color=colour, marker=marker, label=method.replace("_", " ").title(), alpha=.85)
        axis.set(yticks=y, yticklabels=labels, xlim=(-1, 1), xlabel="Spearman with later runs-and-events score",
                 title=title)
        axis.axvline(0, color="#777777", linewidth=.8)
        axis.grid(axis="x", alpha=.2)
    axes[0].invert_yaxis()
    axes[1].legend(fontsize=8)
    fig.suptitle("Contextual role profiles · forward ordering benchmarks")
    fig.savefig(ROOT / "outputs/figures/paprf_role_forward_validation.png", dpi=170)
    plt.close(fig)


def main():
    data, metadata, matches, sources = read_inputs()
    reference = json.loads((ROOT / "work/paprf_contextual_roles.json").read_text(encoding="utf-8"))
    hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in sources}
    if reference["input_hashes"] != hashes:
        raise ValueError("Role profile inputs changed")
    samples = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: np.zeros(4))))

    def add(role, player, match, values):
        aggregate = samples[role][player][match]
        aggregate[:3] += values[SELECT]
        aggregate[3] += 1

    _, names, _, _, _ = calculate(data, metadata, observe=add)
    index, weights = resample({m: metadata[m][1] for m in matches})
    roles, forward_rows, uncertainty = {}, [], []
    for role, prior in reference["roles"].items():
        full = cohort(samples[role], metadata)
        means, sd = moments(np.array([v[0] for v in full.values()]))
        np.testing.assert_allclose(means, prior["primary"]["means"], atol=1e-12)
        np.testing.assert_allclose(sd, prior["primary"]["sample_sds"], atol=1e-12)
        if len(full) != prior["primary"]["eligible"]:
            raise ValueError(f"{role} historical eligible pool replay failed")
        from_means = np.asarray(prior["primary"]["means"])
        from_sd = np.asarray(prior["primary"]["sample_sds"])
        signs = (-1,-1,1) if role.endswith("_bowler") else (1,1,-1)
        scores = {pid: round(float(scale(v,from_means,from_sd,signs) @ WEIGHTS[role]) * n/(n+120),6)
                  for pid,(v,n,_) in full.items()}
        ordered_ids = ordered(scores)
        if [(pid, scores[pid]) for pid in ordered_ids[:10]] != [(r["player_id"], r["score"]) for r in prior["top10"]]:
            raise ValueError(f"{role} historical leaderboard replay failed")
        fitted = [dict(player_id=pid, name=names[pid], rank=i) for i,pid in enumerate(ordered_ids,1)]
        intervals = historic_uncertainty(samples[role], fitted, prior["primary"], role, index, weights)
        uncertainty.extend(intervals)
        tests = []
        for start, stop in zip(CUTOFFS, CUTOFFS[1:]):
            train = cohort(samples[role], metadata, stop=start)
            test = cohort(samples[role], metadata, start, stop)
            result, ledger = forecast(train, test, role, start, stop)
            tests.append(result)
            forward_rows.extend(ledger)
        roles[role] = dict(forward=tests, historical_top10=intervals[:10])
    save("paprf_role_forward_player_ledger.csv", forward_rows)
    save("paprf_role_bootstrap_ledger.csv", uncertainty)
    (ROOT / "work/paprf_role_profile_validation.json").write_text(json.dumps(
        dict(source=hashes, seed=SEED, draws=DRAWS, roles=roles), indent=2) + "\n", encoding="utf-8")
    plot(roles)
    print("Replayed seven role top tens and wrote forward and bootstrap validation.")


if __name__ == "__main__":
    main()
