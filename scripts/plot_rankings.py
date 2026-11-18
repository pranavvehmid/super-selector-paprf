"""Plot the frozen v1 top-10 rankings for the submission report."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
FILES = (
    (
        "Batters",
        ROOT / "outputs" / "rankings" / "lens_a_batters_v1.csv",
        "batter_top10_v1.png",
        "#2a6fbb",
    ),
    (
        "Bowlers",
        ROOT / "outputs" / "rankings" / "lens_a_bowlers_v1.csv",
        "bowler_top10_v1.png",
        "#b84a3a",
    ),
)
OUTPUT_DIR = ROOT / "outputs" / "figures"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for role, path, filename, color in FILES:
        with path.open("r", encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        rows.reverse()
        labels = [f"{row['rank']}. {row['player_name']}" for row in rows]
        values = [float(row["reliability_signal"]) for row in rows]
        figure, axis = plt.subplots(figsize=(9, 5.5))
        bars = axis.barh(labels, values, color=color, alpha=0.88)
        axis.set_xlabel("Shrinkage-protected reliability signal")
        axis.set_title(f"RR Super Select — Top 10 {role} under pressure (v1)")
        axis.axvline(0, color="black", linewidth=0.8)
        for bar, value in zip(bars, values):
            axis.text(value + 0.015, bar.get_y() + bar.get_height() / 2, f"{value:.2f}", va="center", fontsize=9)
        axis.set_xlim(0, max(values) * 1.18)
        figure.tight_layout()
        output_path = OUTPUT_DIR / filename
        figure.savefig(output_path, dpi=180, bbox_inches="tight")
        plt.close(figure)
        print(f"Wrote {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
