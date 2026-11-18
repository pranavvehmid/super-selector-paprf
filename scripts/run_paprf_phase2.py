"""Compare prespecified pressure and weight scenarios against frozen Lens A."""

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rrselect.baselines import eligible, PRESSURE_BANDS
from rrselect.reliability import shrink_to_peer

INPUT = ROOT / "data/processed/metric_attribution_deliveries.csv"
WEIGHTS = {"equal": (1, 1, 1), "rate_heavy": (2, 1, 1), "event_heavy": (1, 1, 2)}


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


@dataclass
class Totals:
    runs: int = 0
    balls: int = 0
    dots: int = 0
    events: int = 0
    matches: set = field(default_factory=set)

    def rates(self, factor):
        return factor * (self.runs / self.balls), self.dots / self.balls, self.events / self.balls


def promoted(row):
    wickets = int(row["pre_delivery_wickets"])
    if row["innings"] == "1":
        return "batter" if int(row["pre_delivery_legal_balls"]) < 36 and wickets >= 3 else None
    balls = int(row["pre_delivery_balls_remaining"])
    runs = int(row["pre_delivery_runs_required"])
    return "bowler" if 6 <= balls <= 24 and wickets <= 8 and 7 * balls <= 6 * runs <= 12 * balls else None


def aggregate():
    competitions = {r["comp_id"]: r["match_format"] for r in rows(ROOT / "data/raw/competitions.csv")}
    families = {
        r["match_id"]: "T20I" if competitions[r["comp_id"]] == "T20I" else "IPL"
        for r in rows(ROOT / "data/raw/matches.csv")
    }
    groups = defaultdict(Totals)
    exposure = Counter()
    for row in rows(INPUT):
        match = row["match_id"]
        base = row["pressure_band"] in PRESSURE_BANDS
        extra = None if base else promoted(row)
        contributions = (
            ("batter", row["striker_id"], int(row["batter_runs_attributed"]),
             row["batter_ball_faced"] == "true", row["batter_dot"] == "true", False),
            ("bowler", row["bowler_id"], int(row["bowler_runs_conceded"]),
             row["bowler_legal_ball"] == "true", row["bowler_dot"] == "true", row["bowler_wicket"] == "true"),
        )
        if row["is_wicket"] == "true" and row["dismissed_player_id"]:
            contributions += (("batter", row["dismissed_player_id"], 0, False, False, True),)
        for role in ("batter", "bowler"):
            exposure[(role, families[match], row["innings"], row["innings_phase"],
                      "reference" if base else "promoted" if extra == role else "ordinary")] += 1
        for role, player, runs, balls, dots, event in contributions:
            for scenario, pressure in (("v1", base), ("role_rule", base or extra == role)):
                group = groups[(role, scenario, player, pressure)]
                group.runs += runs
                group.balls += balls
                group.dots += dots
                group.events += event
                group.matches.add(match)
    return groups, exposure


def score(groups, role, scenario, weights):
    factor, signs = (1, (1, -1, -1)) if role == "batter" else (6, (-1, 1, 1))
    ids = sorted({p for r, s, p, _ in groups if (r, s) == (role, scenario)}, key=int)
    evidence = []
    for player in ids:
        ordinary = groups.get((role, scenario, player, False), Totals())
        pressure = groups.get((role, scenario, player, True), Totals())
        if not eligible(ordinary.balls, pressure.balls, len(ordinary.matches), len(pressure.matches)):
            continue
        deltas = [float(f"{p - o:.6f}") for o, p in zip(ordinary.rates(factor), pressure.rates(factor))]
        evidence.append((player, ordinary, pressure, deltas))
    columns = list(zip(*(item[3] for item in evidence)))
    peer = [(mean(col), stdev(col)) for col in columns]
    output = []
    for player, ordinary, pressure, deltas in evidence:
        signed = [sign * (delta - mu) / sd if sd else 0.0
                  for delta, (mu, sd), sign in zip(deltas, peer, signs)]
        raw = sum(w * z for w, z in zip(weights, signed)) / sum(weights)
        signal, shrinkage = shrink_to_peer(raw, pressure.balls)
        record = {"player_id": player}
        for prefix, group in (("ordinary", ordinary), ("pressure", pressure)):
            record.update({f"{prefix}_{name}": getattr(group, name) for name in ("runs", "balls", "dots", "events")})
            record[f"{prefix}_matches"] = len(group.matches)
        record.update({f"delta_{i}": delta for i, delta in enumerate(deltas, 1)})
        record.update({f"signed_z_{i}": z for i, z in enumerate(signed, 1)})
        record.update(raw_signal=raw, shrinkage=shrinkage, score=float(f"{signal:.6f}"))
        output.append(record)
    return sorted(output, key=lambda row: -row["score"]), peer


def main():
    groups, exposure = aggregate()
    results = {}
    ledger = []
    report = {"input_sha256": digest(INPUT), "roles": {}}
    for role in ("batter", "bowler"):
        suffix = "batters" if role == "batter" else "bowlers"
        frozen = ROOT / f"outputs/rankings/lens_a_{suffix}_v1.csv"
        official = [(r["player_id"], float(r["reliability_signal"])) for r in rows(frozen)]
        official_ids = {pid for pid, _ in official}
        reference = None
        for scenario, weight_set in (("v1", "equal"), ("role_rule", "equal"),
                                     ("v1", "rate_heavy"), ("v1", "event_heavy")):
            weights = WEIGHTS[weight_set]
            ranked, peer = score(groups, role, scenario, weights)
            top = [(r["player_id"], r["score"]) for r in ranked[:10]]
            top_ids = {pid for pid, _ in top}
            eligible_ids = {r["player_id"] for r in ranked}
            if scenario == "v1" and weight_set == "equal":
                if top != official:
                    raise ValueError(f"{role} v1 replay differs from frozen ranks or scores: {top}")
                reference = eligible_ids
            key = f"{scenario}_{weight_set}"
            results[key] = {
                "weight_parts": weights, "peer_mean_and_sample_sd": peer,
                "eligible": len(eligible_ids), "eligible_added": len(eligible_ids - reference),
                "eligible_lost": len(reference - eligible_ids), "overlap_of_10": len(top_ids & official_ids),
                "entered_top10": sorted(top_ids - official_ids, key=int),
                "left_top10": sorted(official_ids - top_ids, key=int),
                "top10_in_order": top,
            }
            ledger.extend({"role": role, "scenario": key, "rank": i, **r} for i, r in enumerate(ranked, 1))
        report["roles"][role] = {"frozen_sha256": digest(frozen), "scenarios": results.copy()}
    report["exposure"] = [dict(role=r, competition=c, innings=i, phase=p, bucket=b, deliveries=n)
                          for (r, c, i, p, b), n in sorted(exposure.items())]
    with (ROOT / "outputs/tables/paprf_phase2_score_ledger.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ledger[0]))
        writer.writeheader()
        writer.writerows(ledger)
    (ROOT / "work/paprf_phase2_sensitivity.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Phase 2 ledger and sensitivity report written after exact v1 replay.")


if __name__ == "__main__":
    main()
