"""Dispatcher placeholder: python scripts/run_step.py <module>. Modules raise NotImplementedError until built."""
import importlib
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

if __name__ == "__main__":
    importlib.import_module(f"rrselect.{sys.argv[1]}").run()
