"""Append an entry to PROJECT_LOG.md and refresh the 'Next action' line. Usage: see AGENTS.md."""
import argparse
import datetime as dt
import re
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "PROJECT_LOG.md"


def build_entry(step, summary, files, decision, next_action, date=None):
    date = date or dt.date.today().isoformat()
    lines = [f"\n## {date} — {summary.splitlines()[0][:80]} (step: {step})", f"- {summary}"]
    if files:
        lines.append(f"- Files: {files}")
    if decision:
        lines.append(f"- Decision: {decision}")
    if next_action:
        lines.append(f"- Next: {next_action}")
    return "\n".join(lines) + "\n"


def update_log(text, entry, next_action=None):
    if next_action:
        text = re.sub(r"^\*\*Next action:\*\*.*$", lambda m: f"**Next action:** {next_action}", text, count=1, flags=re.M)
    return text.rstrip("\n") + "\n" + entry


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--files", default="")
    ap.add_argument("--decision", default="")
    ap.add_argument("--next", default="")
    a = ap.parse_args()
    entry = build_entry(a.step, a.summary, a.files, a.decision, a.next)
    LOG.write_text(update_log(LOG.read_text(), entry, a.next or None))
    print("Appended to PROJECT_LOG.md")


if __name__ == "__main__":
    main()
