import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from log_progress import build_entry, update_log


def test_entry_appended_and_next_action_updated():
    text = "# LOG\n\n**Next action:** old\n\n---\n"
    entry = build_entry("1", "Did a thing", "a.py", "D-001: x", "do next", date="2026-11-17")
    out = update_log(text, entry, "do next")
    assert "**Next action:** do next" in out
    assert "## 2026-11-17 — Did a thing (step: 1)" in out
    assert out.endswith("\n")
