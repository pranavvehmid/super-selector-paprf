"""Generate the v4 research-review supplement from versioned evidence."""

import json

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Image, SimpleDocTemplate, Spacer

from build_paprf_review_pdf import ROOT, add_section, matrix, page, para

DEST = ROOT / "outputs/report/paprf_research_review_v4_supplement.pdf"


def data(name):
    return json.loads((ROOT / f"work/{name}.json").read_text(encoding="utf-8"))


def main():
    model = data("paprf_v4_validation")
    forward = data("paprf_forward_validation")
    split = data("paprf_split_reliability")
    rebuild = data("paprf_clean_rebuild")
    story = [
        Spacer(1, 28), para("PAPRF  /  SUPER SELECTOR ROUND 1", "Kicker"),
        para("V4 research review", "Large"),
        para("Methods, historical rankings and independent validation"),
        para("Supplement to the v1-to-v3 review  |  18 November 2026", "Caption"),
        para("Research conclusion", "Sub"),
        para("V4 keeps matching on innings, phase and competition family and regularises thin cells. The method broadens the assessed population to 149 batters and 156 bowlers. Earlier score ranks carry forward inconsistently. The interleaved halves likewise show little repeatability, even at a stricter sample gate."),
        para("From matched counts to a research score", "Sub"),
        para("Let a and b be ordinary and pressure ball counts in a supported player cell. Compute d = pressure outcome rate minus ordinary outcome rate. For batting the outcomes are runs, dots and striker dismissals per ball faced. Bowling uses economy per six legal balls, dot rate and credited wickets per legal ball."),
        para("Regularised cell lift = d x a b / [a b + 12(a + b)]", "Caption"),
        para("Average cell lifts with pressure-ball weights, standardise within role and cap each signed component at plus or minus three. Average the signed components and multiply by n/(n+60), where n is contributing pressure balls. Order research ranks by the 10th percentile over 500 whole-match resamples. Retain at least 475 valid draws."),
        para("Reproduction", "Sub"),
        para(f"A clean rebuild from the six organiser CSVs reproduced {rebuild['identical_count']} files, including all eight versioned top-ten lists. The scalar audit verified {rebuild['scalar_point_scores_verified']} v4 point scores. These checks establish that the calculations can be reproduced."),
        matrix(["Page", "Section"], [(2, "Historical v4 top tens"), (3, "Forward validation"),
                                       (4, "Interleaved match-halves audit")], [50, 430]),
    ]
    add_section(story, "01  /  RANKINGS", "Historical research top tens")
    for role, result in model["roles"].items():
        story.append(para(role.title() + "s", "Sub"))
        entries = [(r["research_rank"], r["name"], r["pressure_balls"], f"{r['p10']:+.3f}",
                    f"{r['p90']:+.3f}", f"{r['valid_draws']}/500") for r in result["top10"]]
        story.append(matrix(["Rank", "Player", "Pressure balls", "P10", "P90", "Valid draws"], entries,
                            [40, 183, 78, 56, 55, 68]))
    story.extend([Spacer(1, 8), para("The conditional score range describes resampling variation. It does not represent a confidence interval for rank or a future-performance forecast.", "Caption")])
    add_section(story, "02  /  CHRONOLOGY", "Does earlier lift carry forward?")
    story.append(para("Three later windows of 195 to 196 matches compare earlier v4 p10 with two point models and pressure volume. Peer scales are set using earlier matches. Correlations are computed on the same eligible player IDs for all four models in a window."))
    rows = []
    for fold in forward["folds"]:
        for role, stats in fold["roles"].items():
            metrics = stats["predictors"]
            rows.append((fold["fold"], role.title(), stats["common_players"],
                         f"{metrics['v4_p10']['spearman']:+.3f}", f"{metrics['pooled_point']['spearman']:+.3f}",
                         f"{metrics['v4_p10']['original_top10_assessable']}/10"))
    story.extend([
        matrix(["Window", "Role", "Common players", "V4 p10 rho", "Pooled rho", "V4 leaders assessable"], rows,
               [65, 65, 85, 78, 75, 112]),
        Spacer(1, 12), Image(str(ROOT / "outputs/figures/paprf_forward_validation.png"), width=480, height=184),
        para("Figure 1. V4 p10 beats the pooled point score in one of six role-window comparisons. Original-leader coverage counts which of the first ten predictions had enough later evidence.", "Caption"),
        para("Source: docs/methodology/paprf_forward_validation.md and work/paprf_forward_validation.json.", "Caption"),
    ])
    add_section(story, "03  /  MEASUREMENT", "Repeatability in interleaved halves")
    story.append(para("Each of 32 splits groups whole matches by competition family and year. Within each split, 200 shuffles break player pairing within exposure groups while retaining measured half-sample scores. Split ranges describe sensitivity to assignment. The same matches recur across splits."))
    rows = []
    for role, gates in split["roles"].items():
        for gate, record in gates.items():
            metrics = record["summary_p10_p50_p90"]
            lo, med, hi = metrics["composite_rho"]
            rows.append((role.title(), gate.title(), f"{metrics['common_players'][1]:.0f}", f"{med:+.3f}",
                         f"{lo:+.3f} to {hi:+.3f}", f"{record['splits_above_own_null_p90']}/32"))
    story.extend([
        matrix(["Role", "Gate", "Common players", "Median rho", "Observed p10 to p90", "Above shuffle p90"],
               rows, [60, 52, 83, 75, 115, 95]),
        Spacer(1, 12), Image(str(ROOT / "outputs/figures/paprf_split_reliability.png"), width=480, height=196),
        para("Figure 2. Primary gate requires 30 balls and three matches in each context per half. The strict gate requires 60 balls and six matches. Increasing the gate does not improve median correlation.", "Caption"),
        para("Source: docs/methodology/paprf_split_reliability.md and work/paprf_split_reliability.json.", "Caption"),
        para("Decision", "Sub"),
        para("Use v4 for historical research comparisons with an explicit stability caveat. Before making predictive claims, test a better pressure or opponent adjustment on data outside this research sample."),
    ])
    SimpleDocTemplate(str(DEST), pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=57,
                      title="PAPRF v4 research review supplement", author="Super Selector research",
                      invariant=True).build(story, onFirstPage=page, onLaterPages=page)
    print(f"Wrote {DEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
