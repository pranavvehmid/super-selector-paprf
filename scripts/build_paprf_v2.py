"""Build phase-matched, match-resampled research rankings and a comparison plot."""

import json
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from audit_paprf_context import TABLES, collect, consolidate, rank, save
from run_paprf_phase2 import ROOT, digest, rows
from rrselect.reliability import SHRINKAGE_PRIOR_BALLS

SEED = 20261118
DRAWS = 500
CELL_CUTOFF = 12
MIN_VALID = 0.95


def resample(families):
    ids = sorted(families, key=int)
    index = {match: i for i, match in enumerate(ids)}
    rng = np.random.default_rng(SEED)
    weights = np.zeros((DRAWS, len(ids)), dtype=np.int16)
    for family in sorted(set(families.values())):
        cols = [index[match] for match in ids if families[match] == family]
        weights[:, cols] = rng.multinomial(len(cols), np.full(len(cols), 1 / len(cols)), size=DRAWS)
    return index, weights


def score_draws(role, player_cells, peer, grouped, index, weights):
    factor = np.array([1 if role == "batter" else 6, 1, 1])
    signs = (1, -1, -1) if role == "batter" else (-1, 1, 1)
    means, deviations = np.array(peer).T
    totals = np.zeros((DRAWS, 3))
    n = np.zeros(DRAWS)
    valid = np.ones(DRAWS, dtype=bool)
    for cell in player_cells:
        samples = []
        for bucket in (0, 1):
            entries = grouped[(cell, bucket)]
            cols = [index[match] for match, _ in entries]
            samples.append(weights[:, cols] @ np.asarray([counts for _, counts in entries]))
        ordinary, pressure = samples
        o_n, p_n = ordinary[:, 1], pressure[:, 1]
        supported = (o_n > 0) & (p_n > 0)
        valid &= supported
        o_rate = ordinary[:, [0, 2, 3]] / np.maximum(o_n[:, None], 1) * factor
        p_rate = pressure[:, [0, 2, 3]] / np.maximum(p_n[:, None], 1) * factor
        totals += (p_rate - o_rate) * p_n[:, None]
        n += p_n
    deltas = totals[valid] / n[valid, None]
    z = np.divide(deltas - means, deviations, out=np.zeros_like(deltas), where=deviations != 0)
    raw = (z * signs).mean(axis=1)
    return raw * n[valid] / (n[valid] + SHRINKAGE_PRIOR_BALLS)


def plot(top):
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), layout="constrained")
    for axis, (role, players) in zip(axes, top.items()):
        y = np.arange(len(players))
        label = [f"{r['research_rank']}. {r['name']}" for r in players]
        axis.hlines(y, [r["p10"] for r in players], [r["p90"] for r in players],
                    color="#e796c5", linewidth=5, label="Bootstrap 10th–90th percentile")
        axis.scatter([r["p10"] for r in players], y, color="#be006b", label="v2 ranking score", zorder=3)
        axis.scatter([r["point_score"] for r in players], y, marker="D", color="#442e73",
                     label="Matched point score", zorder=3)
        axis.set(yticks=y, yticklabels=label, xlabel="Standardised, shrunk pressure lift", title=role.title() + "s")
        axis.invert_yaxis()
        axis.grid(axis="x", alpha=.25)
    axes[1].legend(loc="upper right", bbox_to_anchor=(1, -0.15), fontsize=8)
    fig.suptitle("PAPRF v2 research top 10 · match-resampling uncertainty")
    fig.savefig(ROOT / "outputs/figures/paprf_v2_uncertainty.png", dpi=180)
    plt.close(fig)


def main():
    clusters = {"families": {}, "counts": defaultdict(lambda: [0, 0, 0, 0])}
    matched, _, source = collect(clusters)
    index, weights = resample(clusters["families"])
    if not np.all(weights.sum(axis=1) == len(index)):
        raise ValueError("A bootstrap draw has the wrong total match count")
    evidence = defaultdict(lambda: defaultdict(list))
    for (role, player, cell, bucket, match), counts in clusters["counts"].items():
        evidence[(role, player)][(cell, bucket)].append((match, counts))
    names = {r["player_id"]: r["player_name"] for r in rows(TABLES / "supplied_data_candidate_universe.csv")}
    prior = json.loads((ROOT / "work/paprf_context_audit.json").read_text(encoding="utf-8"))
    summary = dict(source=source, seed=SEED, draws=DRAWS, cell_cutoff=CELL_CUTOFF, minimum_valid=MIN_VALID,
                   roles={}, frozen_hashes={})
    ledger, threshold_ledger, top = [], [], {}
    for role in ("batter", "bowler"):
        old = ROOT / f"outputs/rankings/lens_a_{role}s_v1.csv"
        summary["frozen_hashes"][role] = digest(old)
        old_rows = list(rows(old))
        frozen = {r["player_id"]: int(r["rank"]) for r in old_rows}
        scenarios = {}
        records = []
        for cutoff in (6, CELL_CUTOFF, 24):
            cohort, support = [], {}
            for (r, pid), groups in sorted(matched.items()):
                if r != role:
                    continue
                cells = [(key, o, p) for key, (o, p) in sorted(groups.items()) if min(o.balls, p.balls) >= cutoff]
                score = consolidate(role, cells, 60, 6)
                if score:
                    cohort.append(dict(player_id=pid, **score))
                    support[pid] = [key for key, _, _ in cells]
            peer = rank(cohort, role)
            ids = [r["player_id"] for r in cohort[:10]]
            scenarios[cutoff] = dict(eligible=len(cohort), top10_ids=ids)
            threshold_ledger.extend(dict(role=role, cutoff=cutoff, **r) for r in cohort)
            if cutoff != CELL_CUTOFF:
                continue
            if ids != prior["roles"][role]["scenarios"]["matched"]["top10_ids"]:
                raise ValueError(f"{role} matched point replay disagrees with previous audit")
            for r in cohort:
                pid = r["player_id"]
                draws = score_draws(role, support[pid], peer, evidence[(role, pid)], index, weights)
                quantiles = [round(float(q), 6) for q in np.quantile(draws, [.1, .5, .9])] if len(draws) else [None] * 3
                records.append(dict(
                    role=role, player_id=pid, name=names.get(pid, pid), v1_frozen_rank=frozen.get(pid),
                    matched_point_rank=r["rank"], point_score=r["score"], ordinary_balls=r["ordinary_balls"],
                    pressure_balls=r["pressure_balls"], valid_draws=len(draws), p10=quantiles[0],
                    p50=quantiles[1], p90=quantiles[2], research_rank=None,
                ))
        qualified = sorted((r for r in records if r["valid_draws"] / DRAWS >= MIN_VALID),
                           key=lambda r: (-r["p10"], int(r["player_id"])))
        for position, r in enumerate(qualified, 1):
            r["research_rank"] = position
        if len(qualified) < 10:
            raise ValueError(f"{role} research ranking has fewer than ten qualifying players")
        top[role] = qualified[:10]
        save(f"../rankings/paprf_{role}s_v2.csv", top[role])
        ledger.extend(sorted(records, key=lambda r: (r["research_rank"] is None, r["research_rank"] or 0, int(r["player_id"]))))
        research_ids = {r["player_id"] for r in top[role]}
        reference_ids = set(scenarios[CELL_CUTOFF]["top10_ids"])
        for scenario in scenarios.values():
            scenario["shared_with_cutoff_12"] = len(set(scenario["top10_ids"]) & reference_ids)
        summary["roles"][role] = dict(
            resample_qualified=len(qualified), threshold_sensitivity=scenarios, top10=top[role],
            shared_with_v1=sorted(research_ids & frozen.keys()),
            shared_with_matched_point=sorted(research_ids & reference_ids),
            left_v1_top10=[dict(player_id=pid, rank=position, name=names.get(pid, pid),
                                research_rank=next((r["research_rank"] for r in records if r["player_id"] == pid), None),
                                status=("outside_top10" if any(r["player_id"] == pid and r["research_rank"] for r in records)
                                        else "insufficient_resample_support" if any(r["player_id"] == pid for r in records)
                                        else "insufficient_matched_support"))
                           for pid, position in frozen.items() if pid not in research_ids],
        )
    save("paprf_v2_uncertainty.csv", ledger)
    save("paprf_v2_threshold_sensitivity.csv", threshold_ledger)
    (ROOT / "work/paprf_v2_validation.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot(top)
    print("Wrote PAPRF v2 research rankings, ledgers and match-resampling figure.")


if __name__ == "__main__":
    main()
