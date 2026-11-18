"""Audit matched context and chronological repeatability for the frozen labels."""

import csv
import json
from collections import defaultdict
from statistics import correlation, mean, stdev

from run_paprf_phase2 import INPUT, ROOT, PRESSURE_BANDS, Totals, digest, rows, shrink_to_peer

TABLES = ROOT / "outputs/tables"


def add(group, match, runs, balls, dots, events):
    group.runs += runs
    group.balls += balls
    group.dots += dots
    group.events += events
    if balls:
        group.matches.add(match)


def eligible(ordinary, pressure, balls, matches):
    return all(group.balls >= balls and len(group.matches) >= matches for group in (ordinary, pressure))


def combined(groups):
    result = Totals()
    for group in groups:
        result.balls += group.balls
        result.matches.update(group.matches)
    return result


def consolidate(role, cells, minimum_balls, minimum_matches):
    factor = 1 if role == "batter" else 6
    ordinary = combined(o for _, o, _ in cells)
    pressure = combined(p for _, _, p in cells)
    if not eligible(ordinary, pressure, minimum_balls, minimum_matches):
        return None
    weighted = [0.0, 0.0, 0.0]
    for _, o, p in cells:
        for i, (baseline, observed) in enumerate(zip(o.rates(factor), p.rates(factor))):
            weighted[i] += p.balls * (observed - baseline)
    return dict(ordinary_balls=ordinary.balls, pressure_balls=pressure.balls,
                ordinary_matches=len(ordinary.matches), pressure_matches=len(pressure.matches),
                retained_cells=len(cells), deltas=[d / pressure.balls for d in weighted])


def rank(records, role):
    signs = (1, -1, -1) if role == "batter" else (-1, 1, 1)
    columns = list(zip(*(r["deltas"] for r in records)))
    peers = [(mean(column), stdev(column) if len(column) > 1 else 0) for column in columns]
    for r in records:
        signed = [sign * (delta - mu) / sd if sd else 0.0
                  for delta, (mu, sd), sign in zip(r.pop("deltas"), peers, signs)]
        raw = mean(signed)
        signal, weight = shrink_to_peer(raw, r["pressure_balls"])
        r.update({f"signed_z_{i}": z for i, z in enumerate(signed, 1)})
        r.update(raw_signal=raw, shrinkage=weight, score=round(signal, 6))
    records.sort(key=lambda r: (-r["score"], int(r["player_id"])))
    for i, r in enumerate(records, 1):
        r["rank"] = i
    return peers


def midranks(values):
    positions = defaultdict(list)
    for i, value in enumerate(sorted(values, reverse=True), 1):
        positions[value].append(i)
    return [mean(positions[value]) for value in values]


def collect(clusters=None, *, striker_dismissals_only=False, dismissal_audit=None):
    comp_path = ROOT / "data/raw/competitions.csv"
    match_path = ROOT / "data/raw/matches.csv"
    inputs = {p.relative_to(ROOT).as_posix(): digest(p) for p in (INPUT, match_path, comp_path)}
    competitions = {r["comp_id"]: r for r in rows(comp_path)}
    matches = {r["match_id"]: r for r in rows(match_path)}
    retained = {r["match_id"] for r in rows(INPUT)}
    dates = sorted((matches[m]["match_date"], int(m)) for m in retained)
    split = dates[len(dates) // 2][0]
    matched = defaultdict(lambda: defaultdict(lambda: (Totals(), Totals())))
    temporal = defaultdict(lambda: defaultdict(lambda: (Totals(), Totals())))
    count = 0
    for row in rows(INPUT):
        count += 1
        match_id = row["match_id"]
        match = matches[match_id]
        comp = competitions[match["comp_id"]]
        if comp["match_format"] == "T20I":
            family = "T20I"
        elif comp["comp_name"].startswith("IPL "):
            family = "IPL"
        else:
            raise ValueError(f"Unexpected tournament for retained match {match_id}")
        cell = (row["innings"], row["innings_phase"], family)
        period = "early" if match["match_date"] < split else "late"
        if clusters is not None:
            clusters["families"][match_id] = family
            if "periods" in clusters:
                clusters["periods"][match_id] = period
        bucket = int(row["pressure_band"] in PRESSURE_BANDS)
        contributions = [
            ("batter", row["striker_id"], int(row["batter_runs_attributed"]),
             row["batter_ball_faced"] == "true", row["batter_dot"] == "true", 0),
            ("bowler", row["bowler_id"], int(row["bowler_runs_conceded"]),
             row["bowler_legal_ball"] == "true", row["bowler_dot"] == "true", row["bowler_wicket"] == "true"),
        ]
        if row["is_wicket"] == "true":
            dismissed = row["dismissed_player_id"]
            striker_ball = dismissed == row["striker_id"] and row["batter_ball_faced"] == "true"
            if dismissal_audit is not None:
                reason = ("missing_id" if not dismissed else "non_striker" if dismissed != row["striker_id"]
                          else "striker_counted_ball" if striker_ball else "striker_uncounted_ball")
                dismissal_audit[row["pressure_band"], reason] += 1
            if dismissed and (striker_ball or not striker_dismissals_only):
                contributions.append(("batter", dismissed, 0, 0, 0, 1))
        for role, player, *totals in contributions:
            add(matched[role, player][cell][bucket], match_id, *totals)
            add(temporal[role, player][period][bucket], match_id, *totals)
            if clusters is not None:
                group = clusters["counts"][(role, player, cell, bucket, match_id)]
                for i, value in enumerate(totals):
                    group[i] += value
    early = sum(day < split for day, _ in dates)
    return matched, temporal, dict(inputs=inputs, deliveries=count, split_date=split,
                                  early_matches=early, late_matches=len(dates)-early,
                                  first_date=dates[0][0], last_date=dates[-1][0])


def save(name, records):
    with (TABLES / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def counts(group, prefix):
    return {f"{prefix}_{key}": getattr(group, key) for key in ("runs", "balls", "dots", "events")} | {
        f"{prefix}_matches": len(group.matches)
    }


def main():
    matched, temporal, report = collect()
    report["roles"] = {}
    match_ledger, temporal_ledger, scores = [], [], []
    for role in ("batter", "bowler"):
        lists = {key: [] for key in ("matched", "early", "late")}
        for (r, pid), groups in sorted(matched.items()):
            if r != role:
                continue
            kept = []
            for cell, (o, p) in sorted(groups.items()):
                use = min(o.balls, p.balls) >= 12
                match_ledger.append(dict(role=role, player_id=pid, innings=cell[0], phase=cell[1],
                                         competition_family=cell[2], retained=use, **counts(o, "ordinary"),
                                         **counts(p, "pressure")))
                if use:
                    kept.append((cell, o, p))
            result = consolidate(role, kept, 60, 6)
            if result:
                lists["matched"].append(dict(role=role, scenario="matched", player_id=pid, **result))
            for period, (o, p) in sorted(temporal[role, pid].items()):
                temporal_ledger.append(dict(role=role, player_id=pid, period=period,
                                            **counts(o, "ordinary"), **counts(p, "pressure")))
                result = consolidate(role, [(period, o, p)], 30, 3)
                if result:
                    lists[period].append(dict(role=role, scenario=period, player_id=pid, **result))
        diagnostics = {}
        for key, players in lists.items():
            for player in players:
                player.update({f"delta_{i}": d for i, d in enumerate(player["deltas"], 1)})
            peer = rank(players, role)
            diagnostics[key] = dict(eligible=len(players), peer_mean_and_sample_sd=peer,
                                    top10_ids=[p["player_id"] for p in players[:10]])
            scores.extend(players)
        frozen = ROOT / f"outputs/rankings/lens_a_{role}s_v1.csv"
        reference_ids = {row["player_id"] for row in rows(frozen)}
        matched_ids = {p["player_id"] for p in lists["matched"]}
        restricted_v1 = sorted(
            (r for r in rows(TABLES / f"{role}_reliability_signals.csv") if r["player_id"] in matched_ids),
            key=lambda r: (-float(r["reliability_signal"]), int(r["player_id"])),
        )[:10]
        restricted_ids = [r["player_id"] for r in restricted_v1]
        early = {p["player_id"]: p["score"] for p in lists["early"]}
        late = {p["player_id"]: p["score"] for p in lists["late"]}
        common = sorted(early.keys() & late.keys())
        early_ranks = midranks([early[pid] for pid in common])
        late_ranks = midranks([late[pid] for pid in common])
        rho = correlation(early_ranks, late_ranks) if len(set(early_ranks)) > 1 and len(set(late_ranks)) > 1 else None
        shared = set(diagnostics["early"]["top10_ids"]) & set(diagnostics["late"]["top10_ids"])
        report["roles"][role] = dict(
            frozen_sha256=digest(frozen), scenarios=diagnostics,
            matched_overlap_ids=sorted(reference_ids & set(diagnostics["matched"]["top10_ids"])),
            frozen_ids_still_eligible_matched=sorted(reference_ids & matched_ids),
            restricted_v1_top10_ids=restricted_ids,
            restricted_v1_vs_matched_overlap_ids=sorted(set(restricted_ids) & set(diagnostics["matched"]["top10_ids"])),
            common_period_eligible_ids=common, spearman=rho, shared_period_top10_ids=sorted(shared),
        )
    save("paprf_matched_cells.csv", match_ledger)
    save("paprf_temporal_periods.csv", temporal_ledger)
    save("paprf_context_audit_scores.csv", scores)
    (ROOT / "work/paprf_context_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Wrote matched-context and temporal ledgers plus audit summary.")


if __name__ == "__main__":
    main()
