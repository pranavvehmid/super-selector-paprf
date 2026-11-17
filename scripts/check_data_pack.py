"""Structural check only: are the six CSVs present with the documented row/column counts? No analysis."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd
from rrselect import config


def main() -> int:
    ok = True
    for name, exp in config.EXPECTED_FILES.items():
        p = config.RAW / name
        if not p.exists():
            print(f"MISSING  {name}")
            ok = False
            continue
        df = pd.read_csv(p, low_memory=False)
        status = "OK      " if (len(df), df.shape[1]) == (exp["rows"], exp["cols"]) else "MISMATCH"
        ok &= status.strip() == "OK"
        print(f"{status} {name}: {len(df)} rows x {df.shape[1]} cols (expected {exp['rows']} x {exp['cols']})")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
