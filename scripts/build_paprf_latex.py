"""Generate native LaTeX evidence tables and an optional compiled report."""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

from build_dashboard_data import build_evidence
from build_paprf_report_evidence import plot_evidence, write_evidence
from build_paprf_research_library import CHAPTERS, FIGURES
from run_paprf_phase2 import ROOT, digest, rows

REPORT = ROOT / "outputs/report/latex"
DOWNLOAD = ROOT / "dashboard/reports"


def tex(value):
    escaped = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}"}
    return "".join(escaped.get(c, c) for c in str(value))


def report_table(headers, values, layout):
    table = [r"\begin{center}", rf"\begin{{tabularx}}{{\linewidth}}{{{layout}}}",
             r"\toprule", " & ".join(map(tex, headers)) + r" \\", r"\midrule"]
    table.extend(" & ".join(map(tex, row)) + r" \\" for row in values)
    return "\n".join(table + [r"\bottomrule", r"\end{tabularx}", r"\end{center}"])


def table_macro(name, headers, values, layout):
    return "\n".join((rf"\newcommand{{\{name}}}{{", report_table(headers, values, layout), "}"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", help="Tectonic executable. Omit to generate sources only.")
    args = parser.parse_args()
    ranks = ROOT / "outputs/rankings"
    paths = [ranks / f"{prefix}_{role}_{suffix}.csv"
             for prefix, suffix in (("lens_a", "v1"), ("paprf_contextual", "top10_v2"))
             for role in ("batters", "bowlers")]
    pressure_bat, pressure_bowl, contextual_bat, contextual_bowl = [list(rows(p)) for p in paths]
    evidence = build_evidence()
    for discipline, records in (("batter", contextual_bat), ("bowler", contextual_bowl)):
        published = evidence["disciplines"]["lists"][discipline]["top10"]
        assert [(r["player_id"], float(r["score"])) for r in records] == [
            (r["player_id"], r["score"]) for r in published
        ], f"{discipline} dashboard and report rankings diverge"
    role_path = ranks / "paprf_contextual_role_top10_v1.csv"
    figures = [ROOT / "outputs/figures" / name for name in FIGURES]
    evidence_files = (
        "paprf_role_profile_validation.json", "paprf_clean_rebuild.json", "data-quality-audit.json",
        "paprf_phase1_audit.json", "paprf_v2_validation.json", "paprf_v3_validation.json",
        "paprf_v4_validation.json", "paprf_forward_validation.json", "paprf_split_reliability.json",
        "paprf_contextual_roles.json", "paprf_contextual_discipline_v2.json", "robustness-validation.json",
    )
    paths.extend([role_path, *figures, *(ROOT / "work" / name for name in evidence_files),
                  ROOT / "outputs/tables/paprf_pressure_distribution.csv",
                  ROOT / "outputs/tables/paprf_role_profile_scores.csv"])
    inputs = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}
    run = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:12]
    audit = json.loads((ROOT / "work/paprf_phase1_audit.json").read_text(encoding="utf-8"))
    rebuild = json.loads((ROOT / "work/paprf_clean_rebuild.json").read_text(encoding="utf-8"))
    author = re.search(r'name:\s*"([^"]+)"', (ROOT / "dashboard/author.js").read_text(encoding="utf-8")).group(1)
    layout = r"r>{\raggedright\arraybackslash}Xr>{\raggedright\arraybackslash}Xr"
    macros = [
        rf"\newcommand{{\ResearchAuthor}}{{{tex(author)}}}",
        rf"\newcommand{{\RunID}}{{{run}}}",
        rf"\newcommand{{\DeliveryCount}}{{{audit['delivery_rows']:,}}}",
        rf"\newcommand{{\MatchCount}}{{{audit['distinct_match_ids']:,}}}",
        rf"\newcommand{{\ReplayCount}}{{{rebuild['identical_count']}}}",
        table_macro("PressureTable", ("Rank", "Batter", "Lift", "Bowler", "Lift"),
                    [(i, a["player_name"], f"{float(a['reliability_signal']):.3f}", b["player_name"],
                      f"{float(b['reliability_signal']):.3f}") for i, (a, b) in enumerate(zip(pressure_bat, pressure_bowl), 1)],
                    layout),
        table_macro("ContextTable", ("Rank", "Batter", "Index", "Bowler", "Index"),
                    [(i, a["name"], f"{float(a['score']):.3f}", b["name"],
                      f"{float(b['score']):.3f}") for i, (a, b) in enumerate(zip(contextual_bat, contextual_bowl), 1)],
                    layout),
        table_macro("RoleTable", ("Role", "Leader", "Scored balls"),
                    [(r["role"].replace("_", " ").title(), r["name"], r["scored_balls"])
                     for r in rows(role_path) if r["rank"] == "1"], r"lXr"),
    ]
    (REPORT / "generated.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")
    appendix = REPORT / "evidence_appendix.tex"
    write_evidence(evidence, appendix, report_table, tex)
    manifest = dict(run_id=run, input_hashes=inputs, independently_rebuilt_files=rebuild["identical_count"])
    DOWNLOAD.mkdir(exist_ok=True)
    files = [REPORT / name for name in ("paprf_research.tex", "generated.tex", "README.md")] + [appendix, *figures]
    with tempfile.TemporaryDirectory(prefix="paprf-latex-") as temp:
        for file in files:
            shutil.copyfile(file, f"{temp}/{file.name}")
        for figure in plot_evidence(evidence, temp):
            files.append(figure)
        if args.engine:
            subprocess.run([args.engine, "--keep-logs", "paprf_research.tex"], cwd=temp, check=True)
            shutil.copyfile(f"{temp}/paprf_research.pdf", REPORT / "paprf_research.pdf")
            shutil.copyfile(REPORT / "paprf_research.pdf", DOWNLOAD / "paprf_research.pdf")
        with ZipFile(DOWNLOAD / "paprf_research_source.zip", "w", ZIP_DEFLATED) as archive:
            for file in files:
                archive.write(file, file.name)
            for _, _, name in CHAPTERS:
                archive.write(ROOT / "docs" / name, "research/" + name)
    manifest["pdf_available"] = bool(args.engine)
    (ROOT / "work/publication_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared publication evidence run {run}.")


if __name__ == "__main__":
    main()
