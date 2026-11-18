"""Regularise fine-cell lifts and audit the PAPRF v4 ranks."""

import json
from collections import Counter, defaultdict
from statistics import correlation

import matplotlib.pyplot as plt
import numpy as np

from audit_paprf_context import TABLES, collect, combined, eligible, midranks, save
from build_paprf_v2 import DRAWS, MIN_VALID, SEED, resample
from build_paprf_v3 import combine_cells
from run_paprf_phase2 import ROOT, rows
from rrselect.reliability import SHRINKAGE_PRIOR_BALLS

LAMBDA = 12
CAP = 3
ROLES = ("batter", "bowler")
SCENARIOS = {
    "primary": (12, 3, 3), "lambda6": (6, 3, 3), "lambda24": (24, 3, 3),
    "uncapped": (12, np.inf, 3), "no_event_component": (12, 3, 2),
    "historical_dismissals": (12, 3, 3),
}


def load_cells(**kwargs):
    clusters = {"families": {}, "periods": {}, "counts": defaultdict(lambda: [0, 0, 0, 0])}
    _, _, source = collect(clusters, **kwargs)
    return (*combine_cells(clusters, (0, 1, 2)), clusters["families"], source)


def cell_lift(ordinary, pressure, role, strength):
    a, b = ordinary[..., 1], pressure[..., 1]
    supported = (a > 0) & (b > 0)
    ab = a.astype(float) * b
    scale = np.array([6 if role == "bowler" else 1, 1, 1])
    rates = (pressure[..., [0, 2, 3]] / np.maximum(b, 1)[..., None]
             - ordinary[..., [0, 2, 3]] / np.maximum(a, 1)[..., None]) * scale
    ridge = np.divide(ab, ab + strength * (a + b), out=np.zeros_like(ab), where=supported)
    return rates * ridge[..., None], np.where(supported, b, 0)


def vector(group):
    return [group.runs, group.balls, group.dots, group.events]


def normalise(deltas, peers, role, cap):
    means, sds = peers
    signs = (1, -1, -1) if role == "batter" else (-1, 1, 1)
    signed = np.divide(deltas - means, sds, out=np.zeros_like(deltas), where=sds > 0) * signs
    return np.clip(signed, -cap, cap)


def measure(groups, role, strength, min_balls=60, min_matches=6):
    records, support = [], {}
    for (record_role, player), cells in sorted(groups.items()):
        if record_role != role:
            continue
        kept = [(key, o, p) for key, (o, p) in sorted(cells.items()) if min(o.balls, p.balls) > 0]
        ordinary = combined(o for _, o, _ in kept)
        pressure = combined(p for _, _, p in kept)
        if not eligible(ordinary, pressure, min_balls, min_matches):
            continue
        lifted, balls = cell_lift(np.array([vector(o) for _, o, _ in kept]),
                                  np.array([vector(p) for _, _, p in kept]), role, strength)
        support[player] = kept
        records.append(dict(player_id=player, ordinary_balls=ordinary.balls, pressure_balls=pressure.balls,
                            ordinary_matches=len(ordinary.matches), pressure_matches=len(pressure.matches),
                            cells=len(kept), deltas=np.average(lifted, weights=balls, axis=0)))
    return records, support


def fit(groups, role, strength, cap, components, min_balls=60, min_matches=6):
    records, support = measure(groups, role, strength, min_balls, min_matches)
    deltas = np.array([r["deltas"] for r in records])
    peers = deltas.mean(axis=0), deltas.std(axis=0, ddof=1)
    for r in records:
        delta = r.pop("deltas")
        signed = normalise(delta, peers, role, cap)
        raw = float(signed[:components].mean())
        n = r["pressure_balls"]
        r.update({f"delta_{i}": float(d) for i, d in enumerate(delta, 1)})
        r.update({f"signed_z_{i}": float(z) for i, z in enumerate(signed, 1)})
        r.update(raw_score=raw, point_score=round(raw * n / (n + SHRINKAGE_PRIOR_BALLS), 6))
    records.sort(key=lambda r: (-r["point_score"], int(r["player_id"])))
    for i, r in enumerate(records, 1):
        r["point_rank"] = i
    return records, support, peers


def bootstrap(role, cells, evidence, peers, index, weights):
    totals = np.zeros((len(weights), 3))
    n = np.zeros(len(weights))
    for cell, _, _ in cells:
        samples = []
        for bucket in (0, 1):
            data = evidence[cell, bucket]
            cols = [index[match] for match, _ in data]
            samples.append(weights[:, cols] @ np.asarray([counts for _, counts in data]))
        lift, balls = cell_lift(*samples, role, LAMBDA)
        totals += lift * balls[:, None]
        n += balls
    valid = n > 0
    delta = totals[valid] / n[valid, None]
    raw = normalise(delta, peers, role, CAP).mean(axis=1)
    return raw * n[valid] / (n[valid] + SHRINKAGE_PRIOR_BALLS)


def temporal(windows, role):
    ranks, ledger = [], []
    for name, groups in windows.items():
        scores, _, _ = fit(groups, role, LAMBDA, CAP, 3, 30, 3)
        ranks.append({r["player_id"]: r["point_score"] for r in scores})
        ledger.extend(dict(role=role, window=name, **r) for r in scores)
    a, b = ranks
    common = sorted(a.keys() & b.keys(), key=int)
    mid = [midranks([scores[pid] for pid in common]) for scores in ranks]
    rho = correlation(*mid) if all(len(set(values)) > 1 for values in mid) else None
    return dict(early=len(a), late=len(b), common=len(common), spearman=rho,
                shared_top10=len(set(list(a)[:10]) & set(list(b)[:10]))), ledger


def plot(roles):
    fig, axis = plt.subplots(figsize=(9.8, 3.8), layout="constrained")
    settings = list(SCENARIOS)[1:]
    grid = [[roles[role]["tests"].get(key, {}).get("overlap", np.nan) for key in settings] for role in ROLES]
    shade = axis.imshow(grid, cmap="PuRd", vmin=0, vmax=10, aspect="auto")
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            axis.text(x, y, "N/A" if np.isnan(cell) else f"{cell}/10", ha="center", va="center",
                      color="white" if cell >= 7 else "#25172c", fontweight="bold")
    labels = ["Lambda 6", "Lambda 24", "Uncapped", "Drop event", "Historical dismissals"]
    axis.set(xticks=range(len(settings)), xticklabels=labels, yticks=[0, 1], yticklabels=["Batters", "Bowlers"],
             title="PAPRF v4 · point top-ten agreement with primary model")
    fig.colorbar(shade, ax=axis, label="Shared players out of 10")
    fig.savefig(ROOT / "outputs/figures/paprf_v4_sensitivity.png", dpi=180)
    plt.close(fig)


def main():
    audits = Counter()
    pooled, windows, evidence, families, source = load_cells(striker_dismissals_only=True, dismissal_audit=audits)
    historical, _, _, _, _ = load_cells()
    index, weights = resample(families)
    if not np.all(weights.sum(axis=1) == len(index)):
        raise ValueError("Wrong match count in bootstrap draw")
    names = {r["player_id"]: r["player_name"] for r in rows(TABLES / "supplied_data_candidate_universe.csv")}
    report = dict(source=source, seed=SEED, draws=DRAWS, min_valid=MIN_VALID, strength=LAMBDA, clip=CAP,
                  dismissal_audit=[dict(band=k[0], attribution=k[1], events=v) for k, v in sorted(audits.items())], roles={})
    rank_ledger, sensitivity, time_ledger, cell_ledger, progression = [], [], [], [], []
    for role in ROLES:
        v3 = ROOT / f"outputs/rankings/paprf_{role}s_v3.csv"
        old = {r["player_id"]: int(r["research_rank"]) for r in rows(v3)}
        scores, support, peers = fit(pooled, role, LAMBDA, CAP, 3)
        point_top = {r["player_id"] for r in scores[:10]}
        for r in scores:
            pid = r["player_id"]
            draws = bootstrap(role, support[pid], evidence[role, pid], peers, index, weights)
            sample = [round(float(q), 6) for q in np.quantile(draws, [.1, .5, .9])] if len(draws) else [None] * 3
            r.update(name=names.get(pid, pid), v3_top10_rank=old.get(pid), valid_draws=len(draws),
                     p10=sample[0], p50=sample[1], p90=sample[2], research_rank=None)
            for (innings, phase, family), ordinary, pressure in support[pid]:
                cell_ledger.append(dict(role=role, player_id=pid, innings=innings, phase=phase, family=family,
                                        ordinary_runs=ordinary.runs, ordinary_balls=ordinary.balls,
                                        ordinary_dots=ordinary.dots, ordinary_events=ordinary.events,
                                        pressure_runs=pressure.runs, pressure_balls=pressure.balls,
                                        pressure_dots=pressure.dots, pressure_events=pressure.events))
        ranked = sorted((r for r in scores if r["valid_draws"] / DRAWS >= MIN_VALID),
                        key=lambda r: (-r["p10"], int(r["player_id"])))
        if len(ranked) < 10:
            raise ValueError(f"{role} has fewer than ten eligible players")
        for i, r in enumerate(ranked, 1):
            r["research_rank"] = i
        top = ranked[:10]
        save(f"../rankings/paprf_{role}s_v4.csv", top)
        tests = {}
        for scenario, parameters in SCENARIOS.items():
            if scenario == "historical_dismissals" and role == "bowler":
                continue
            groups = historical if scenario == "historical_dismissals" else pooled
            alternatives, _, _ = fit(groups, role, *parameters)
            ids = [r["player_id"] for r in alternatives[:10]]
            tests[scenario] = dict(eligible=len(alternatives), top10_ids=ids, overlap=len(point_top & set(ids)))
            sensitivity.extend(dict(role=role, scenario=scenario, **r) for r in alternatives)
        time, time_rows = temporal(windows, role)
        top_ids = {r["player_id"] for r in top}
        versions = {
            "v1": {r["player_id"]: int(r["rank"]) for r in rows(ROOT / f"outputs/rankings/lens_a_{role}s_v1.csv")},
            "v2": {r["player_id"]: int(r["research_rank"]) for r in rows(ROOT / f"outputs/rankings/paprf_{role}s_v2.csv")},
            "v3": old,
            "v4": {r["player_id"]: r["research_rank"] for r in top},
        }
        for pid in sorted(set().union(*versions.values()), key=int):
            progression.append(dict(role=role, player_id=pid, name=names.get(pid, pid),
                                    **{f"{v}_top10_rank": ranks.get(pid) for v, ranks in versions.items()}))
        by_id = {r["player_id"]: r for r in scores}
        departures = [dict(player_id=pid, name=names.get(pid, pid), v3_rank=rank,
                           reason="Outside top ten" if by_id.get(pid, {}).get("research_rank") else
                           "Too few valid draws" if pid in by_id else "Insufficient matched support")
                      for pid, rank in old.items() if pid not in top_ids]
        report["roles"][role] = dict(eligible_point=len(scores), eligible_bootstrap=len(ranked), top10=top,
                                     shared_with_v3=len(top_ids & old.keys()), v3_departures=departures,
                                     v4_overlap_by_version={key: len(top_ids & ranks.keys()) for key, ranks in versions.items()},
                                     tests=tests, temporal=time, peer_means=peers[0].tolist(),
                                     peer_sample_sd=peers[1].tolist())
        rank_ledger.extend(dict(role=role, **r) for r in scores)
        time_ledger.extend(time_rows)
    for name, records in (("rank_ledger", rank_ledger), ("sensitivity", sensitivity),
                          ("temporal", time_ledger), ("cells", cell_ledger), ("progression", progression)):
        save(f"paprf_v4_{name}.csv", records)
    (ROOT / "work/paprf_v4_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    plot(report["roles"])
    print("Wrote v4 rankings, attribution audit, stress tests and temporal evidence.")


if __name__ == "__main__":
    main()
