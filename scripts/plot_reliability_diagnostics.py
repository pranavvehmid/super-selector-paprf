"""Create compact Step 8 diagnostic plots from protected signals."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = ROOT / "outputs" / "figures"
FILES = (
    (
        "Batters",
        ROOT / "outputs" / "tables" / "batter_reliability_signals.csv",
        "pressure_balls",
        "batter_reliability_diagnostic.png",
    ),
    (
        "Bowlers",
        ROOT / "outputs" / "tables" / "bowler_reliability_signals.csv",
        "pressure_legal_balls",
        "bowler_reliability_diagnostic.png",
    ),
)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for role, path, sample_field, output_name in FILES:
        with path.open("r", encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        samples = [int(row[sample_field]) for row in rows]
        raw = [float(row["raw_signal"]) for row in rows]
        shrunk = [float(row["reliability_signal"]) for row in rows]

        figure, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        axes[0].scatter(samples, raw, alpha=0.55, s=24, label="Raw signal")
        axes[0].scatter(samples, shrunk, alpha=0.70, s=24, label="Shrunk signal")
        axes[0].axhline(0, color="black", linewidth=0.8)
        axes[0].set_xlabel("Pressure opportunities")
        axes[0].set_ylabel("Peer-standardised signal")
        axes[0].set_title(f"{role}: sample size and shrinkage")
        axes[0].legend(frameon=False)

        axes[1].hist(raw, bins=22, alpha=0.55, label="Raw signal")
        axes[1].hist(shrunk, bins=22, alpha=0.65, label="Shrunk signal")
        axes[1].axvline(0, color="black", linewidth=0.8)
        axes[1].set_xlabel("Peer-standardised signal")
        axes[1].set_ylabel("Players")
        axes[1].set_title(f"{role}: reliability-signal distribution")
        axes[1].legend(frameon=False)

        figure.suptitle(f"Step 8 diagnostic — {role}", fontsize=13, fontweight="bold")
        figure.tight_layout()
        figure.savefig(FIGURES_DIR / output_name, dpi=180, bbox_inches="tight")
        plt.close(figure)
        print(f"Wrote {(FIGURES_DIR / output_name).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
