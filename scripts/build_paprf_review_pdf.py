"""Generate the editable-by-source PAPRF research review draft."""

import json
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "outputs/report/paprf_research_review_v3.pdf"
INK = colors.HexColor("#25172C")
PINK = colors.HexColor("#A60061")
TINT = colors.HexColor("#FBE7F2")
MUTED = colors.HexColor("#5C4D64")
STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK, spaceAfter=10))
STYLES.add(ParagraphStyle("Kicker", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=PINK, spaceAfter=11))
STYLES.add(ParagraphStyle("Large", fontName="Helvetica-Bold", fontSize=38, leading=42, textColor=INK, spaceAfter=16))
STYLES.add(ParagraphStyle("Heading", fontName="Helvetica-Bold", fontSize=24, leading=27, textColor=INK, spaceAfter=14))
STYLES.add(ParagraphStyle("Sub", fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=PINK, spaceBefore=8, spaceAfter=6))
STYLES.add(ParagraphStyle("Caption", fontName="Helvetica", fontSize=8.5, leading=12, textColor=MUTED, spaceAfter=8))
STYLES.add(ParagraphStyle("Cell", fontName="Helvetica", fontSize=9, leading=11, textColor=INK))
STYLES.add(ParagraphStyle("HeaderCell", parent=STYLES["Cell"], textColor=colors.white, fontName="Helvetica-Bold"))


def para(text, style="Body"):
    return Paragraph(escape(str(text)), STYLES[style])


def matrix(headers, entries, widths):
    data = [[para(cell, "HeaderCell") for cell in headers]]
    data.extend([para(cell, "Cell") for cell in row] for row in entries)
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PINK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, TINT]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def page(canvas, document):
    width, height = A4
    canvas.setFillColor(PINK)
    canvas.rect(0, height - 11, width, 11, fill=1, stroke=0)
    canvas.setStrokeColor(TINT)
    canvas.line(50, 47, width - 50, 47)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(50, 33, "PAPRF  /  SUPER SELECTOR ROUND 1  /  RESEARCH REVIEW DRAFT")
    canvas.drawRightString(width - 50, 33, str(document.page))


def add_section(story, number, title):
    story.extend([PageBreak(), para(number, "Kicker"), para(title, "Heading")])


def main():
    result = json.loads((ROOT / "work/paprf_v3_validation.json").read_text(encoding="utf-8"))
    designs = result["designs"]
    v3 = designs["phase_family_v3"]
    fine = designs["fine_v2"]
    story = [
        Spacer(1, 42), para("SUPER SELECTOR  /  ROUND 1", "Kicker"), para("T20 under pressure", "Large"),
        para("Pressure-Adjusted Performance and Resilience Framework"),
        para("Research review draft  |  PAPRF v1 to v3  |  18 November 2026", "Caption"),
        Spacer(1, 24),
        para("What changed", "Sub"),
        para("The original Lens A v1 ranks compare a player's pressure performance with their own ordinary baseline. The v2 research model matches similar contexts and uses whole-match resampling. V3 merges innings within phase and competition family to recover coverage."),
        para(f"Coverage rose from {fine['batter']['bootstrap_eligible']} to {v3['batter']['bootstrap_eligible']} batters and from {fine['bowler']['bootstrap_eligible']} to {v3['bowler']['bootstrap_eligible']} bowlers. Chronological results still give little evidence of persistent ranks. The v3 lists describe the current research candidate."),
        Spacer(1, 12), para("Contents", "Sub"),
        matrix(["Page", "Section"], [
            (2, "Dataset, pressure and estimation"), (3, "Granularity and temporal validation"),
            (4, "Research top tens"), (5, "Evidence index and limitations"),
        ], [50, 430]),
    ]
    add_section(story, "01  /  METHOD", "From delivery to ranking")
    story.extend([
        para("Population and attribution", "Sub"),
        para(f"The retained IPL and T20I sample contains {result['source']['deliveries']:,} delivery rows in 782 matches. Pre-delivery state is reconstructed from earlier events in delivery order. Match and competition metadata join by ID. Batting opportunities and bowling legal balls have separate denominators. The attribution audit excludes 257 ambiguous rows from player-rate attribution."),
        para("Pressure label", "Sub"),
        para("Let L be completed legal balls, W wickets lost, R runs required and B balls remaining before the rated delivery. Clamp(x) bounds x to [0, 1]. The first innings uses late urgency and wickets. The chase also uses required rate."),
        para("Innings 1: 0.70 clamp((L - 72) / 48) + 0.30 clamp(W / 10)", "Caption"),
        para("Innings 2: 0.55 clamp((6R / max(B, 1) - 7) / 5) + 0.25 clamp(W / 10) + 0.20 clamp(L / 120)", "Caption"),
        para("Below 0.40 is ordinary. From 0.40 to below 0.65 is elevated, and 0.65 or above is high. The pressure bucket combines the last two categories. The first-innings formula structurally assigns ordinary to every powerplay event."),
        para("Matched pressure lift and resampling", "Sub"),
        para("Compute pressure rate minus ordinary rate separately in each retained player cell. Average these differences using pressure balls as weights. Batting uses runs per ball, dot rate and dismissals per ball. Bowling uses runs per six legal balls, dot rate and credited wickets per legal ball."),
        para("Signed z = sign x (delta - eligible peer mean) / peer sample standard deviation", "Caption"),
        para("Score = mean(three signed z values) x pressure balls / (pressure balls + 60)", "Caption"),
        para("Use 12 balls per bucket per cell and 60 balls plus six opportunity-bearing matches per bucket across retained cells. For each of 500 draws, sample matches with replacement within IPL and T20I and recompute rates, cell weights and shrinkage. Keep the observed support and peer scales fixed. P10 is the ranking score. A player needs at least 475 draws with nonzero denominators in all retained cells."),
    ])
    add_section(story, "02  /  VALIDATION", "Coverage and repeatability")
    names = {"fine_v2": "Fine v2", "phase_family_v3": "Phase + family v3", "innings_phase": "Innings + phase"}
    comparison = []
    for key, roles in designs.items():
        for role, stats in roles.items():
            temporal = stats["temporal"]
            comparison.append((names[key], role.title(), stats["matched_eligible"], stats["bootstrap_eligible"],
                               temporal["common_eligible"], f"{temporal['spearman']:+.3f}"))
    story.extend([
        para("The 782 matches were divided at 8 May 2024 into two windows with 391 matches each. Spearman correlation uses only players eligible in both windows under the same design. Each window recomputes point scores, with 30 balls and three matches per context across supported cells."),
        matrix(["Design", "Role", "Matched", "Bootstrap eligible", "Common players", "Spearman"], comparison,
               [124, 49, 58, 85, 86, 78]),
        Spacer(1, 12),
        Image(str(ROOT / "outputs/figures/paprf_v3_granularity.png"), width=480, height=196),
        para("Figure 1. Coarser strata increase coverage. Temporal correlations remain close to zero for v3, and its two window top tens share zero players in both roles.", "Caption"),
        para("The v3 top ten shares four batters and three bowlers with v2. Differences reflect support, weighting of contexts, and peer re-standardisation. The coverage gain does not resolve the setting-versus-chasing confound introduced by merging innings."),
    ])
    add_section(story, "03  /  RANKINGS", "PAPRF v3 research top tens")
    for role in ("batter", "bowler"):
        story.append(para(role.title() + "s", "Sub"))
        entries = [(r["research_rank"], r["name"], r["rank"], f"{r['p10']:.3f}",
                    f"{r['p90']:.3f}", f"{r['valid_draws']}/500") for r in v3[role]["top10"]]
        story.append(matrix(["v3", "Player", "Point rank", "P10", "P90", "Valid draws"], entries,
                            [40, 190, 62, 61, 57, 70]))
    story.extend([Spacer(1, 8), para("The conditional percentile range describes score variation under resampling. It is not an interval for rank or for future performance.", "Caption")])
    add_section(story, "04  /  EVIDENCE", "Reproduction and review notes")
    story.extend([
        para("Evidence map", "Sub"),
        matrix(["Subject", "Repository path"], [
            ("Original equations and attribution", "docs/methodology/lens_a_formula_ledger.md"),
            ("Pressure and weight sensitivity", "docs/methodology/paprf_phase2_experiment.md"),
            ("Matched cells and temporal comparison", "docs/methodology/paprf_matched_context_and_repeatability.md"),
            ("Bootstrap definitions and v2 movement", "docs/methodology/paprf_v2_uncertainty.md"),
            ("Granularity protocol and v3 findings", "docs/methodology/paprf_v3_cell_granularity.md"),
            ("Inputs, hashes, cohorts and movement", "work/paprf_v3_validation.json"),
            ("Player-level matched scores", "outputs/tables/paprf_v3_granularity_ledger.csv"),
            ("Player-level scores by window", "outputs/tables/paprf_v3_temporal_ledger.csv"),
        ], [180, 300]),
        para("Reproduce the diagnostics", "Sub"),
        para("From the repository root, run python scripts/build_paprf_v3.py with the local organiser data and attributed delivery file. The seed is 20261118. The script checks the fine-cell replay against both v2 top tens and their p10 scores. Run python scripts/build_paprf_review_pdf.py with ReportLab to regenerate this review."),
        para("Open research questions", "Sub"),
        para("Partial pooling may retain useful information in thin cells while preserving innings. Audit dismissal-rate influence before relying on extreme batting contributions. Compare designs on an identical temporal cohort and reserve an untouched future period for prediction claims. The current results describe historical pressure lift in this sample."),
    ])
    SimpleDocTemplate(str(DEST), pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=57,
                      title="PAPRF research review draft", author="Super Selector research",
                      invariant=True).build(story, onFirstPage=page, onLaterPages=page)
    print(f"Wrote {DEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
