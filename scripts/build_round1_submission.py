"""Verify every frozen Lens A score and compile a pressure-first submission PDF."""

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from statistics import mean, stdev

from build_paprf_latex import DOWNLOAD, REPORT, report_table, table_macro, tex
from run_paprf_phase2 import INPUT, ROOT, digest, rows


METRICS = {
    "batter": (("runs_per_ball", "dot_rate", "dismissal_rate"), "balls", (1, -1, -1)),
    "bowler": (("economy", "dot_rate", "wicket_rate"), "legal_balls", (-1, 1, 1)),
}
WRAP = r">{\raggedright\arraybackslash}X"


def macro(name, content):
    return rf"\newcommand{{\{name}}}{{{content}}}"


def scope_note(discipline, row, metrics, signs):
    labels = ("faster scoring", "fewer dots", "fewer dismissals") if discipline == "batter" else (
        "fewer conceded runs", "more dots", "more wickets")
    favourable = [label for label, metric, sign in zip(labels, metrics, signs)
                  if sign * float(row[metric + "_delta"]) > 0]
    return ", ".join(favourable) or "Peer-adjusted lift only"


def verified_tables():
    manifest = json.loads((ROOT / "outputs/rankings/ranking_manifest_v1.json").read_text())
    base = ROOT / "outputs/tables"
    verified, tables, leaders = 0, [], []
    for discipline, (metrics, ball_key, signs) in METRICS.items():
        key = discipline + "s"
        accepted = list(rows(ROOT / manifest["files"][key]["path"]))
        source = list(rows(base / f"{discipline}_pressure_baselines.csv"))
        eligible = [r for r in source if min(int(r[f"{b}_{ball_key}"]) for b in ("ordinary", "pressure")) >= 60
                    and min(int(r[f"{b}_matches"]) for b in ("ordinary", "pressure")) >= 6]
        if {r["player_id"] for r in eligible} != {r["player_id"] for r in source if r["eligible"] == "true"}:
            raise ValueError(f"{discipline}: evidence gate does not reconcile")
        values = [[float(r[metric + "_delta"]) for r in eligible] for metric in metrics]
        peers = [(mean(column), stdev(column)) for column in values]
        scores = {}
        for r in eligible:
            n = int(r[f"pressure_{ball_key}"])
            standard = [d * (float(r[metric + "_delta"]) - center) / spread if spread else 0
                        for metric, d, (center, spread) in zip(metrics, signs, peers)]
            scores[r["player_id"]] = f"{mean(standard) * n / (n + 60):.6f}"
        existing = {r["player_id"]: r["reliability_signal"] for r in rows(base / f"{discipline}_reliability_signals.csv")}
        if scores != existing:
            raise ValueError(f"{discipline}: independent score mismatch")
        ordered = sorted(scores, key=lambda pid: -float(scores[pid]))[:10]
        if ordered != manifest["files"][key]["player_ids_in_rank_order"] or [
            (r["rank"], r["player_id"], r["reliability_signal"]) for r in accepted
        ] != [(str(i), pid, scores[pid]) for i, pid in enumerate(ordered, 1)]:
            raise ValueError(f"{discipline}: rank or manifest mismatch")
        verified += len(scores)
        leaders.append(accepted)
        lookup = {r["player_id"]: r for r in eligible}
        spreads = table_macro(discipline.title() + "PeerTable", ("Component", "Mean gap", "Sample SD"),
                              [(m.replace("_", " "), f"{a:.9f}", f"{b:.9f}") for m, (a, b) in zip(metrics, peers)],
                              WRAP + "rr")
        evidence_headers = ("Rank", "Player (ID)", "Balls O/P", "Matches O/P", "Rate gap", "Dot gap", "Event gap")
        evidence = []
        implications = []
        for r in accepted:
            pid = r["player_id"]
            p = lookup[pid]
            evidence.append((r["rank"], f"{r['player_name']} ({pid})",
                             f"{p['ordinary_' + ball_key]}/{p['pressure_' + ball_key]}",
                             f"{p['ordinary_matches']}/{p['pressure_matches']}",
                             f"{float(p[metrics[0] + '_delta']):+.3f}",
                             f"{100 * float(p[metrics[1] + '_delta']):+.2f}",
                             f"{100 * float(p[metrics[2] + '_delta']):+.2f}"))
            implications.append((r["player_name"], scope_note(discipline, p, metrics, signs)))
        tables.extend((spreads,
                       table_macro(discipline.title() + "Evidence", evidence_headers, evidence, "r" + WRAP + "rrrrr"),
                       table_macro(discipline.title() + "Fit", ("Player", "Observed pressure contribution"),
                                   implications, WRAP + WRAP)))
    return verified, leaders, tables


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True, help="Tectonic executable")
    args = parser.parse_args()
    count, (batters, bowlers), tables = verified_tables()
    audit = json.loads((ROOT / "work/paprf_phase1_audit.json").read_text())
    pressure = audit["band_totals"]
    model = json.loads((ROOT / "work/robustness-validation.json").read_text())["roles"]
    repeat = json.loads((ROOT / "work/paprf_split_reliability.json").read_text())
    author = re.search(r'name:\s*"([^"]+)"', (ROOT / "dashboard/author.js").read_text(encoding="utf-8")).group(1)
    excluded = [r for r in rows(INPUT) if r["metric_eligible"] == "false"]
    tables.extend((
        macro("AuthorName", tex(author)), macro("ScoreCount", str(count)),
        macro("Matches", f"{audit['distinct_match_ids']:,}"), macro("Deliveries", f"{audit['delivery_rows']:,}"),
        macro("Flagged", f"{pressure['elevated'] + pressure['high']:,}"),
        macro("FlaggedShare", tex(f"{100 * (pressure['elevated'] + pressure['high']) / audit['delivery_rows']:.1f}%")),
        macro("Ambiguous", str(len(excluded))),
        macro("AmbiguousDismissals", str(sum(r["is_wicket"] == "true" and bool(r["dismissed_player_id"].strip())
                                            for r in excluded))),
        macro("BattersEligible", str(model["batter"]["eligible_base_count"])),
        macro("BowlersEligible", str(model["bowler"]["eligible_base_count"])),
        macro("HolderRaw", batters[0]["raw_signal"]), macro("HolderScore", batters[0]["reliability_signal"]),
        table_macro("EntryTable", ("Rank", "Batter", "Score", "Bowler", "Score"),
                    [(a["rank"], a["player_name"], a["reliability_signal"], b["player_name"], b["reliability_signal"])
                     for a, b in zip(batters, bowlers)], "r" + WRAP + "r" + WRAP + "r"),
        table_macro("SensitivityTable", ("Scenario", "Batters", "Bowlers"),
                    [(f"{p}-ball prior, shared with v1", *(f"{model[d]['prior_top10_overlap_with_60'][str(p)]}/10"
                                                          for d in METRICS)) for p in (30, 90)]
                    + [("High band only, eligible", *(model[d]["eligible_high_only_count"] for d in METRICS)),
                       ("High band only, shared with v1", *(f"{model[d]['high_only_top10_overlap_with_base']}/10"
                                                          for d in METRICS))], WRAP + "rr"),
        table_macro("RepeatTable", ("Discipline", "Common IDs", "Observed rho", "Shuffle rho", "Above p90"),
                    [(d.title(), f"{r['summary_p10_p50_p90']['common_players'][1]:.0f}",
                      f"{r['summary_p10_p50_p90']['composite_rho'][1]:+.3f}",
                      f"{r['shuffle_rho_p10_p50_p90'][1]:+.3f}",
                      f"{r['splits_above_own_null_p90']}/{repeat['splits']}")
                     for d in METRICS for r in (repeat["roles"][d]["primary"],)], WRAP + "rrrr"),
    ))
    generated = REPORT / "round1_evidence.tex"
    generated.write_text("\n\n".join(tables) + "\n", encoding="utf-8")
    source = REPORT / "round1_submission.tex"
    with tempfile.TemporaryDirectory(prefix="paprf-round1-") as temp:
        for path in (source, generated):
            shutil.copy(path, temp)
        subprocess.run([args.engine, source.name], cwd=temp, check=True)
        filename = source.with_suffix(".pdf").name
        shutil.copyfile(f"{temp}/{filename}", REPORT / filename)
        shutil.copyfile(REPORT / filename, DOWNLOAD / filename)
    print(f"Verified {count} eligible scores and 20 dropdown entries. PDF SHA-256 {digest(REPORT / filename)}")


if __name__ == "__main__":
    main()
