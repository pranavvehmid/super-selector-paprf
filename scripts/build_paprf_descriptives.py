"""Build reproducible PAPRF pressure-context tables and one explanatory chart."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "pressure_labeled_deliveries.csv"
TABLE = ROOT / "outputs" / "tables" / "paprf_pressure_distribution.csv"
FIGURE = ROOT / "outputs" / "figures" / "paprf_pressure_distribution.png"
AUDIT = ROOT / "work" / "paprf_phase1_audit.json"
BANDS = ("ordinary", "elevated", "high")
PHASES = ("powerplay", "middle", "death")
CELLS = [(innings, phase, band) for innings in ("1", "2") for phase in PHASES for band in BANDS]


def recompute(row: dict[str, str]) -> tuple[float, str, str]:
    balls = int(row["pre_delivery_legal_balls"])
    wickets = int(row["pre_delivery_wickets"])
    phase = "powerplay" if balls < 36 else "middle" if balls < 90 else "death"
    if row["innings"] == "1":
        index = 0.70 * min(max((balls - 72) / 48, 0), 1) + 0.30 * wickets / 10
    else:
        required_rate = 6 * int(row["pre_delivery_runs_required"]) / max(
            int(row["pre_delivery_balls_remaining"]), 1
        )
        index = 0.55 * min(max((required_rate - 7) / 5, 0), 1)
        index += 0.25 * (wickets / 10) + 0.20 * (balls / 120)
    # Compare the published six-decimal index and its displayed band.
    published = float(f"{index:.6f}")
    band = "high" if published >= 0.65 else "elevated" if published >= 0.40 else "ordinary"
    return published, phase, band


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def main() -> None:
    counts: Counter[tuple[str, str, str]] = Counter()
    matches: set[str] = set()
    phase_counts: Counter[tuple[str, str]] = Counter()
    audit_errors: Counter[str] = Counter()
    with INPUT.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            if row["innings"] not in {"1", "2"}:
                raise ValueError(f"Unexpected innings for match {row['match_id']}")
            expected_index, expected_phase, expected_band = recompute(row)
            audit_errors["index"] += expected_index != float(row["pressure_index"])
            audit_errors["phase"] += expected_phase != row["innings_phase"]
            audit_errors["band"] += expected_band != row["pressure_band"]
            counts[(row["innings"], row["innings_phase"], row["pressure_band"])] += 1
            phase_counts[(row["innings"], row["innings_phase"])] += 1
            matches.add(row["match_id"])
    total = counts.total()
    if not total:
        raise ValueError("Pressure-labelled input is empty")
    if audit_errors.total():
        raise ValueError(f"Phase 1 formula reconciliation failed: {dict(audit_errors)}")

    TABLE.parent.mkdir(parents=True, exist_ok=True)
    with TABLE.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=[
            "innings", "innings_phase", "pressure_band", "delivery_count", "all_deliveries",
            "innings_phase_deliveries", "pct_of_all_deliveries", "pct_within_innings_phase",
        ])
        writer.writeheader()
        for innings, phase, band in CELLS:
            count = counts[(innings, phase, band)]
            phase_total = phase_counts[(innings, phase)]
            writer.writerow({
                "innings": innings,
                "innings_phase": phase,
                "pressure_band": band,
                "delivery_count": count,
                "all_deliveries": total,
                "innings_phase_deliveries": phase_total,
                "pct_of_all_deliveries": f"{100 * count / total:.6f}",
                "pct_within_innings_phase": f"{100 * count / phase_total:.6f}" if phase_total else "",
            })

    audit = {
        "input": INPUT.relative_to(ROOT).as_posix(),
        "input_sha256": sha256(INPUT),
        "delivery_rows": total,
        "distinct_match_ids": len(matches),
        "recalculation_mismatches": dict(audit_errors),
        "band_totals": {band: sum(counts[key] for key in CELLS if key[2] == band) for band in BANDS},
        "ranking_file_hashes": {
            path.name: sha256(path) for path in sorted((ROOT / "outputs" / "rankings").glob("*_v1.*"))
        },
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for axis, innings in zip(axes, ("1", "2")):
        bottoms = [0, 0, 0]
        for band, color in zip(BANDS, ("#b0b0b0", "#e6a23c", "#c74e4e")):
            values = [counts[(innings, phase, band)] for phase in PHASES]
            axis.bar(PHASES, values, bottom=bottoms, label=band.title(), color=color)
            bottoms = [bottom + value for bottom, value in zip(bottoms, values)]
        axis.set_title(f"Innings {innings}")
        axis.set_xlabel("Phase")
    axes[0].set_ylabel("Deliveries")
    axes[0].set_ylim(0, max(phase_counts.values()) * 1.08)
    axes[1].legend(title="Pressure band")
    fig.suptitle("PAPRF v1 pressure-context distribution")
    fig.tight_layout()
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {TABLE.relative_to(ROOT)}")
    print(f"Wrote {FIGURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
