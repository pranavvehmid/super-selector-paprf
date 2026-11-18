"""Publish project-authored Markdown chapters and figures as static site assets."""

import html
import re
import shutil
from pathlib import Path
from urllib.parse import quote, urlsplit

import markdown

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "dashboard"
REPO = "https://github.com/pranavvehmid/super-selector-paprf/blob/main/"
CHAPTERS = (
    ("plan", "Research plan and phase history", "methodology/paprf_four_phase_plan.md"),
    ("unified", "Unified index and leaderboard directory", "methodology/paprf_unified_ranking.md"),
    ("roles", "Contextual outcomes and seven roles", "methodology/paprf_contextual_role_profiles.md"),
    ("role-validation", "Role validation and score uncertainty", "methodology/paprf_role_profile_validation.md"),
    ("source-dictionary", "Organiser data dictionary", "data_dictionary.md"),
    ("source-audit", "Dataset quality and exclusions", "data_quality_report.md"),
    ("phase-one", "Phase 1 evidence and distribution", "methodology/paprf_phase1_evidence.md"),
    ("pressure-method", "Pre-delivery pressure definition", "methodology/pressure_definition.md"),
    ("v1", "Archived Lens A formula ledger", "methodology/lens_a_formula_ledger.md"),
    ("experiment", "Pressure and weight experiments", "methodology/paprf_phase2_experiment.md"),
    ("matched", "Matched-context audit", "methodology/paprf_matched_context_and_repeatability.md"),
    ("v2", "Pressure v2 and resampling", "methodology/paprf_v2_uncertainty.md"),
    ("v3", "Pressure v3 and cell granularity", "methodology/paprf_v3_cell_granularity.md"),
    ("v4", "Pressure v4 regularisation", "methodology/paprf_v4_reanalysis.md"),
    ("forward", "Forward validation of pressure rankings", "methodology/paprf_forward_validation.md"),
    ("split", "Interleaved split-half reliability", "methodology/paprf_split_reliability.md"),
)
FIGURES = (
    "paprf_role_annual_examples.png", "paprf_role_component_heatmaps.png",
    "paprf_role_forward_validation.png", "paprf_pressure_distribution.png",
    "paprf_v2_uncertainty.png", "paprf_v4_sensitivity.png",
    "paprf_forward_validation.png", "paprf_split_reliability.png",
)


def local_links(body, location, chapter_links):
    def rewrite(match):
        parsed = urlsplit(html.unescape(match[1]))
        if parsed.scheme or not parsed.path:
            return match[0]
        target = (location.parent / parsed.path).resolve()
        if not target.is_relative_to(ROOT):
            return 'href="#library-top"'
        if target in chapter_links:
            return f'href="#{chapter_links[target]}"'
        if target.is_relative_to(ROOT / "data"):
            return 'href="#source-dictionary"'
        suffix = "#" + quote(parsed.fragment) if parsed.fragment else ""
        return f'href="{REPO}{quote(target.relative_to(ROOT).as_posix())}{suffix}"'

    return re.sub(r'href="([^"]*)"', rewrite, body)


def main():
    chapter_links = {(ROOT / "docs" / relative).resolve(): key for key, _, relative in CHAPTERS}
    contents = []
    for key, _, relative in CHAPTERS:
        source = ROOT / "docs" / relative
        body = markdown.markdown(source.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
        body = re.sub(r"<(/?)h([1-5])>", lambda m: f"<{m[1]}h{int(m[2])+1}>", body)
        contents.append(f'<article id="{key}">{local_links(body, source, chapter_links)}</article>')
    toc = "".join(f'<li><a href="#{k}">{html.escape(title)}</a></li>' for k, title, _ in CHAPTERS)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PAPRF research library</title><link rel="stylesheet" href="styles.css">
<link rel="stylesheet" href="publication.css"></head><body>
<header class="site-header"><div class="mast"><a class="brand" href="index.html">PAPRF</a>
<span class="mast-label">Research library</span></div>
<nav aria-label="Research"><a href="index.html#unified">Unified index</a><a href="index.html#pipeline">Methods overview</a>
<a href="index.html#figures">Figure atlas</a><a href="#library-top">Contents</a></nav></header>
<main class="library" id="library-top"><section class="panel"><p class="kicker">RESEARCH RECORD</p>
<h1>Methods &amp; evidence</h1><p>Full research chapters, formulas and versioned validation. File links open the underlying evidence in the project's private GitHub repository.</p>
<ol class="library-index">{toc}</ol></section>
{"".join(contents)}</main><footer><a href="#library-top">Back to contents</a></footer></body></html>"""
    (SITE / "library.html").write_text(page + "\n", encoding="utf-8")
    (SITE / "figures").mkdir(exist_ok=True)
    for name in FIGURES:
        shutil.copyfile(ROOT / "outputs/figures" / name, SITE / "figures" / name)
    print(f"Published {len(CHAPTERS)} research chapters and {len(FIGURES)} figures locally.")


if __name__ == "__main__":
    main()
