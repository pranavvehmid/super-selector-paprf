"""Generate the printed companion to the interactive dashboard."""

from math import erf, sqrt
from pathlib import Path

from build_paprf_research_library import CHAPTERS


ROLES = {
    "opener": "Opener", "top_order": "Top-order batter", "middle_lower": "Middle/lower-order batter",
    "late_entrant": "Late entrant", "powerplay_bowler": "Powerplay bowler",
    "middle_bowler": "Middle-overs bowler", "death_bowler": "Death bowler",
}
SITE = "https://dashboard-seven-delta-35.vercel.app/"
FIGURE_NOTES = (
    ("paprf_role_annual_examples.png", "Annual contextual run residuals. Points show runs per ball with exposure labels. Partial years and changing schedules limit comparisons."),
    ("paprf_role_component_heatmaps.png", "Role metric Spearman correlations. Shared information between runs and boundaries motivates the residualised-boundary sensitivity test."),
    ("paprf_role_forward_validation.png", "Later-window contextual role validation. Spearman correlations use common eligible IDs. Absent estimates indicate inadequate support."),
    ("paprf_pressure_distribution.png", "Delivery counts by innings, phase and pressure band. First-innings powerplay elevated and high counts are structurally zero."),
    ("paprf_v2_uncertainty.png", "Pressure v2 conditional score uncertainty. Intervals span empirical p10 to p90 from whole-match resampling."),
    ("paprf_v4_sensitivity.png", "Pressure v4 assumptions. Cells show the number of names shared with the primary v4 point top ten."),
    ("paprf_forward_validation.png", "Pressure rank backtest. Markers compare prior rankings with later measured lift among common eligible players."),
    ("paprf_split_reliability.png", "Pressure split-half repeatability. Conditional shuffle distributions preserve exposure groups inside each split."),
    ("report_pressure_curve.pdf", "Chase rule at selected match states. Dashed lines mark the elevated and high gates. The default dashboard example reaches 0.800 at 12 required runs per over."),
    ("report_index_contributions.pdf", "Ultimate Top 10 index contributions for both disciplines. Start at 50, add the evidence-adjusted primary contribution and then the capped increment available to a secondary role."),
    ("report_role_distribution.pdf", "Eligible role scores grouped into the dashboard's six score intervals. Counts use role eligibility and can count one player in multiple roles."),
    ("report_dataset_coverage.pdf", "Raw rows in each supplied file. The logarithmic scale shows their orders of magnitude. Rows across files describe different units."),
)


def f(value, places=3):
    return "--" if value is None else f"{float(value):.{places}f}"


def pct(value):
    return "--" if value is None else f"{100 * value:.1f}%"


def figure(path, caption):
    return "\n".join((r"\begin{figure}[htbp]", r"\centering",
                      rf"\includegraphics[width=\linewidth,height=.72\textheight,keepaspectratio]{{{path}}}",
                      rf"\caption{{{caption}}}", r"\end{figure}"))


def write_evidence(data, report, report_table, tex):
    def grid(headers, values, layout):
        return report_table(headers, values, layout.replace("X", r">{\raggedright\arraybackslash}X"))

    discipline_lists = data["disciplines"]["lists"]
    text = [
        r"\section{Dataset coverage and pressure evidence}",
        "The organiser's six files are audited before state reconstruction. The first summary counts raw rows, "
        "columns and exact duplicates. Field-level values below count blank cells, which may be valid when "
        "an event is inapplicable. The denominator for a blank percentage is the total rows in its file.",
        grid(("Source file", "Rows", "Fields", "Exact duplicates"),
             ((name, f"{r['row_count']:,}", r["column_count"], r["exact_duplicate_row_count"])
              for name, r in data["datasets"].items()), "Xrrr"),
    ]
    for name, r in data["datasets"].items():
        blanks = [(key, f"{n:,}", pct(n / r["row_count"])) for key, n in r["blank_counts"].items() if n]
        text.extend((rf"\subsection*{{{tex(name)}}}",
                     grid(("Field with blanks", "Blank rows", "Share"), blanks, "Xrr") if blanks
                     else "The file has no recorded blank fields."))
    bands = data["audit"]["band_totals"]
    pressure_count = bands["elevated"] + bands["high"]
    total = data["audit"]["delivery_rows"]
    text.extend((
        r"\subsection{Pressure exposure by innings and phase}",
        f"The retained ledger contains {total:,} events. Elevated plus high comprises "
        rf"{bands['elevated']:,} + {bands['high']:,} = {pressure_count:,} events. Dividing by {total:,} "
        rf"and multiplying by 100 gives {tex(pct(pressure_count / total))}. Phase shares use the corresponding innings-phase subtotal.",
        grid(("Innings", "Phase", "Band", "Events", "All share", "Phase share"),
              ((r["innings"], r["innings_phase"], r["pressure_band"], r["delivery_count"],
                f"{r['pct_of_all_deliveries']}%", f"{r['pct_within_innings_phase']}%")
               for r in data["distribution"]), "rXXrrr"),
    ))

    text.extend((r"\clearpage", r"\section{Ultimate Top 10 player evidence}",
                 "The following pages reproduce the dashboard drill-down for every ranked batter and bowler in "
                 "the two Ultimate Top 10 lists. Annual raw rates include warm-up observations where available. "
                 "Residuals use scored opportunities only. A dash indicates unavailable evidence."))
    for discipline, model in discipline_lists.items():
        ranked = model["top10"]
        assert [r["rank"] for r in ranked] == list(range(1, 11))
        if discipline == "bowler":
            text.append(r"\clearpage")
        text.extend((rf"\subsection{{{discipline.title()} score ledger}}",
                     f"{model['eligible']} of {model['observed']} observed players qualify. "
                     f"{model['pressure_submission_overlap']} names also appear in this discipline's archived pressure top ten.",
                     grid(("Rank", "Player", "Primary role", "Balls", "Matches", "Final index"),
                          ((r["rank"], r["name"], ROLES[r["primary_role"]], r["primary_balls"],
                            r["primary_matches"], f(r["score"], 6)) for r in ranked), "rXXrrr")))
        names = {r["player_id"]: r["name"] for r in model["ranked"]}
        text.extend((r"\subsubsection*{Sensitivity and player movement}",
                     grid(("Alternative", "Shared", "Max shift", "Entered", "Left", "Rank 1"),
                          ((label, f"{r['overlap']}/10", r["max_rank_shift"], ", ".join(r["entered"]) or "--",
                            ", ".join(r["left"]) or "--", names[r["top10_ids"][0]]) for label, r in (
                              ("No secondary credit", model["methods"]["primary_only"]),
                              ("India events times 1.5", model["methods"]["india_1_5"]),
                              ("Residualised boundaries", model["methods"]["residualised_boundary"]))), "XrrXXX")))
        first, second = ranked[:2]
        text.extend((r"\subsubsection*{Comparison of ranks one and two}",
                     grid(("Measure", first["name"], second["name"]),
                          ((label, f(first[key], digits), f(second[key], digits)) for label, key, digits in (
                              ("Primary scored opportunities", "primary_balls", 0),
                              ("Primary scored matches", "primary_matches", 0),
                              ("Role reference", "primary_reference", 6),
                              ("Evidence-adjusted primary", "primary_adjusted", 6),
                              ("Secondary credit", "secondary_credit", 6),
                              ("Final contextual index", "score", 6))), "Xrr")))
        for r in ranked:
            profiles = model["profiles"][r["player_id"]]
            primary = next(p for p in profiles if p["role"] == r["primary_role"])
            weights = data["role_profiles"]["weights"][primary["role"]]
            scale = model["methods"]["unified_v1"]["scales"][primary["role"]]
            composite = sum(weight * z for weight, z in zip(weights, primary["signed_z"]))
            normal = (composite - scale["mean"]) / scale["sample_sd"] if scale["sample_sd"] else 0
            reference = 50 * (1 + erf(normal / sqrt(2)))
            retention = r["primary_balls"] / (r["primary_balls"] + 120)
            adjusted = 50 + retention * (reference - 50)
            credit = max((.1 * min(1, p["balls"] / r["primary_balls"]) * max(0, p["adjusted"] - 50)
                          for p in profiles if p is not primary), default=0)
            assert round(min(100, adjusted + credit), 6) == r["score"], r["name"]
            secondary = "No secondary role meets the support gate."
            if r["secondary_role"]:
                secondary = (f"{ROLES[r['secondary_role']]} contributes {f(credit, 6)} points "
                             f"from {r['secondary_balls']} balls with adjusted value {f(r['secondary_adjusted'], 6)}.")
            text.extend((
                r"\clearpage",
                rf"\subsection{{{discipline.title()} {r['rank']}. {tex(r['name'])}}}",
                tex(f"Player ID {r['player_id']}. Primary role: {ROLES[primary['role']]}. "
                    f"{r['primary_balls']} scored balls in {r['primary_matches']} matches, "
                    f"representing {pct(r['primary_share'])} of scored opportunities in this discipline."),
                grid(("Primary metric", "Signed z", "Weight", "Contribution"),
                     ((label, f(z, 6), pct(weight), f(weight * z, 6)) for label, z, weight in
                      zip(("Runs", "Boundaries", "Dismissals or wickets"), primary["signed_z"], weights)), "Xrrr"),
                tex(f"Weighted total {f(composite, 6)}. Among {scale['eligible']} role peers the mean is "
                    f"{f(scale['mean'], 6)} and sample SD {f(scale['sample_sd'], 6)}. The role z-score is "
                    f"{f(normal, 6)} and Q = {f(reference, 6)}. Retention is {f(retention, 6)}. "
                    f"The running total moves from 50 to {f(adjusted, 6)} after the primary adjustment, "
                    f"then to {f(r['score'], 6)}. {secondary}"),
                grid(("Supported role", "Balls", "India", "Adjusted", "Pressure lift", "Top 10 share"),
                     ((ROLES[p["role"]], p["balls"], p["india_balls"], f(p["adjusted"]),
                       f(p["pressure_rate_lift"], 4), pct(p["bootstrap_top10_share"])) for p in profiles),
                     "Xrrrrr"),
                grid(("Primary role venue", "Scored balls", "Run residual per ball"),
                     ((region, item["balls"], f(item["run_residual"], 4)) for region, item in
                      primary["geography"].items()), "Xrr"),
                grid(("Year", "Observed balls", "Scored balls",
                      "Economy" if discipline == "bowler" else "Strike rate", "Run residual / ball"),
                     ((y["year"], y["balls"], y["scored_balls"], f(y["raw_rate"], 2), f(y["run_residual"], 4))
                      for y in primary["annual"]), "Xrrrr"),
                tex(f"Ball-weighted annual residual slope: {f(primary['trend']['annual_rate_residual_slope'], 4)} "
                    "runs per ball per year.") if primary["trend"] else "",
            ))
    text.extend((r"\clearpage", r"\section{Seven role leaderboards and validation}",
                 "Top-ten shares come from historical match resampling. Pressure lift is the pressure-minus-ordinary "
                 "run residual per opportunity and needs 30 scored balls in each context. A negative residual favours "
                 "bowlers. India means venue country. These diagnostics use different units from the final index."))
    for role, stats in data["role_profiles"]["roles"].items():
        valid = data["role_validation"]["roles"][role]
        shares = {r["player_id"]: r["top10_share"] for r in valid["historical_top10"]}
        text.extend((
            rf"\subsection{{{ROLES[role]}}}",
            tex(f"{stats['primary']['eligible']} eligible. Top-ten overlap with primary: India weighting "
                f"{stats['india_1_5']['shared_with_primary']}/10, equal weighting "
                f"{stats['equal_weights']['shared_with_primary']}/10, and boundary residualisation "
                f"{stats['orthogonal_boundary']['shared_with_primary']}/10."),
            grid(("Rank", "Player", "Role score", "Balls", "India balls", "Resample share"),
                 ((r["rank"], r["name"], f(r["score"], 6), r["scored_balls"], r["india_scored_balls"],
                   pct(shares.get(r["player_id"]))) for r in stats["top10"]), "rXrrrr"),
            grid(("Later test starts", "Common", "Primary", "Boundary alt.", "Runs only", "Volume", "Assessable"),
                 ((w["start"], w["common"], *(f(w["comparisons"][key]["spearman"]) for key in
                     ("primary", "orthogonal_boundary", "runs_only", "volume")),
                   f"{w['comparisons']['primary']['earlier_top10_assessable']}/{w['comparisons']['primary']['earlier_top10_size']}")
                  for w in valid["forward"]), "Xrrrrrr"),
        ))
    text.extend((r"\clearpage", r"\section{Pressure validation and model comparisons}",
                 "Forward results report Spearman rank correlation on common eligible IDs. "
                 "Split-half summaries show median and empirical p10 to p90. Under uniform independent "
                 "top-ten membership in a common pool of size $N$, expected overlap is $100/N$."))
    for discipline in discipline_lists:
        text.extend((
            rf"\subsection{{{discipline.title()} forward and split-half tests}}",
            grid(("Later period", "Common", "v4 p10", "v4 point", "Pooled", "Volume", "Chance", "Assessable"),
                 ((f"{fold['test_start']} to {fold['test_end']}", s["common_players"],
                   *(f(s["predictors"][k]["spearman"]) for k in ("v4_p10", "v4_point", "pooled_point",
                                                               "pressure_volume")), f(s["chance_top10_overlap"]),
                   f"{s['predictors']['v4_p10']['original_top10_assessable']}/10")
                  for fold in data["forward"]["folds"] for s in (fold["roles"][discipline],)), "Xrrrrrrr"),
            grid(("Gate balls / matches", "Common median", "Observed p10 / p50 / p90",
                  "Shuffled p10 / p50 / p90", "Above null p90"),
                 (("30 / 3" if key == "primary" else "60 / 6", r["summary_p10_p50_p90"]["common_players"][1],
                   " / ".join(map(f, r["summary_p10_p50_p90"]["composite_rho"])),
                   " / ".join(map(f, r["shuffle_rho_p10_p50_p90"])),
                   f"{r['splits_above_own_null_p90']}/{data['split_reliability']['splits']}")
                  for key, r in data["split_reliability"]["roles"][discipline].items()), "XrXXr"),
        ))
        v2 = data["research"]["roles"][discipline]
        v4 = data["regularised"]["roles"][discipline]
        lens = data["robustness"]["roles"][discipline]
        text.extend((
            grid(("Archived v1 alternative", "Shared names"),
                 [(f"Shrinkage prior {n} balls", lens["prior_top10_overlap_with_60"][str(n)]) for n in (30, 90)]
                 + [("High band only", lens["high_only_top10_overlap_with_base"])], "Xr"),
            grid(("v2 balls per context cell", "Eligible", "Shared names"),
                 ((k, r["eligible"], r["shared_with_cutoff_12"]) for k, r in v2["threshold_sensitivity"].items()), "Xrr"),
            grid(("v3 matching design", "Point eligible", "Draw eligible", "Common", "Temporal rho"),
                 ((k.replace("_", " "), r["matched_eligible"], r["bootstrap_eligible"],
                   r["temporal"]["common_eligible"], f(r["temporal"]["spearman"]))
                  for k, roles in data["granularity"]["designs"].items() for r in (roles[discipline],)), "Xrrrr"),
            grid(("v4 assumption", "Point eligible", "Shared names"),
                 ((k.replace("_", " "), r["eligible"], r["overlap"]) for k, r in v4["tests"].items()), "Xrr"),
        ))
        for label, stats, prior_key, point_key in (
            ("v2", data["research"]["roles"][discipline], "v1_frozen_rank", "matched_point_rank"),
            ("v3", data["granularity"]["designs"]["phase_family_v3"][discipline], "v2_rank", "rank"),
            ("v4", data["regularised"]["roles"][discipline], "v3_top10_rank", "point_rank"),
        ):
            text.extend((
                r"\clearpage",
                rf"\subsubsection*{{{discipline.title()} {label} match-resampling rankings}}",
                grid(("Rank", "Player", "Prior rank", "Point rank", "p10", "p90", "Valid"),
                     ((r["research_rank"], r["name"], r[prior_key] or "--", r[point_key], f(r["p10"], 6),
                       f(r["p90"], 6), r["valid_draws"]) for r in stats["top10"]), "rXrrrrr"),
            ))
            departures = {"v2": "left_v1_top10", "v3": "v2_departures", "v4": "v3_departures"}[label]
            if stats[departures]:
                text.append(grid(("Player leaving the prior top ten", "Prior rank", "Reason"),
                                 ((r["name"], r.get("v3_rank", r.get("v2_rank", r.get("rank"))),
                                   r.get("reason", r.get("status", "")).replace("_", " "))
                                  for r in stats[departures]), "XrX"))
    text.extend((r"\clearpage", r"\section{Visual evidence atlas}",
                 "The first eight figures reproduce the dashboard's published Figure Atlas. The remaining four "
                 "are fixed printable views of the interactive pressure curve, impact bridge and dataset and role views."))
    for path, caption in FIGURE_NOTES:
        text.append(figure(path, tex(caption)))
    text.extend((r"\clearpage", r"\section{Research documentation and data provenance}",
                 "The research library preserves full protocols, data definitions, exclusions, experiment history "
                 "and linked ledgers. The editable report archive also includes these chapters as Markdown.",
                 r"\begin{enumerate}",
                 *(rf"\item \href{{{SITE}library.html\#{key}}}{{{tex(title)}}}" for key, title, _ in CHAPTERS),
                 r"\end{enumerate}"))
    report.write_text("\n\n".join(text) + "\n", encoding="utf-8")


def plot_evidence(data, directory):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output = []
    rose, ink = "#A8245C", "#27212A"

    def save(fig, name):
        path = Path(directory) / name
        fig.savefig(path, bbox_inches="tight", metadata={"CreationDate": None})
        plt.close(fig)
        output.append(path)

    fig, ax = plt.subplots(figsize=(9, 4.2), layout="constrained")
    rates = [0, 7, 12, 18]
    for balls, wickets, style in [(30, 2, ":"), (90, 4, "-"), (110, 7, "--")]:
        ax.plot(rates, [.55 * min(1, max(0, (r - 7) / 5)) + .25 * wickets / 10 + .20 * balls / 120
                        for r in rates], linestyle=style, linewidth=2, label=f"{balls} balls, {wickets} wickets")
    for threshold, label in [(.4, "Elevated"), (.65, "High")]:
        ax.axhline(threshold, color="grey", linestyle="--", linewidth=.8)
        ax.text(.2, threshold + .015, label, color=ink)
    ax.set(xlabel="Required runs per over", ylabel="Pre-delivery chase pressure (0–1)", ylim=(0, 1), xlim=(0, 18))
    ax.legend(loc="lower right")
    save(fig, "report_pressure_curve.pdf")

    fig, axes = plt.subplots(1, 2, figsize=(10.6, 5.2), sharex=True, layout="constrained")
    for ax, (discipline, model) in zip(axes, data["disciplines"]["lists"].items()):
        ranked = model["top10"]
        primary = [r["primary_adjusted"] - 50 for r in ranked]
        secondary = [min(r["secondary_credit"], 100 - r["primary_adjusted"]) for r in ranked]
        y = range(len(ranked))
        ax.barh(y, primary, left=50, color=rose, label="Primary lift from 50")
        ax.barh(y, secondary, left=[r["primary_adjusted"] for r in ranked], color="#42394b",
                label="Secondary increment")
        ax.set(yticks=y, yticklabels=[r["name"] for r in ranked], xlim=(49, 100),
               xlabel="Index points", title=discipline.title() + "s")
        ax.invert_yaxis()
        ax.axvline(50, color=ink, linewidth=.8)
    axes[0].legend(loc="lower right", fontsize=8)
    save(fig, "report_index_contributions.pdf")

    fig, axes = plt.subplots(4, 2, figsize=(9, 8), sharex=True, layout="constrained")
    bounds = ["<-1", "[-1,-.5)", "[-.5,0)", "[0,.5)", "[.5,1)", ">=1"]
    for ax, (role, counts) in zip(axes.flat, data["role_histograms"]["counts"].items()):
        bars = ax.bar(bounds, counts, color=rose)
        ax.bar_label(bars, fontsize=8, padding=2)
        ax.set(title=ROLES[role], ylabel="Players", ylim=(0, max(counts) * 1.25))
        ax.tick_params(axis="x", labelbottom=True, labelsize=8)
    axes.flat[-1].set_axis_off()
    fig.supxlabel("Reliability-adjusted role score interval")
    save(fig, "report_role_distribution.pdf")

    fig, ax = plt.subplots(figsize=(9, 4), layout="constrained")
    names, counts = zip(*[(k, r["row_count"]) for k, r in data["datasets"].items()])
    bars = ax.barh(names, counts, color=rose)
    ax.bar_label(bars, labels=[f"{n:,}" for n in counts], padding=3)
    ax.set(xscale="log", xlim=(10, max(counts) * 3), xlabel="Raw file rows (logarithmic scale)")
    ax.invert_yaxis()
    save(fig, "report_dataset_coverage.pdf")
    return output
