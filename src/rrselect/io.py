"""Data loading helpers (Step 2). IDs are join keys; names are never used as keys."""
import pandas as pd
from . import config


def load_raw(filename: str, **kwargs) -> pd.DataFrame:
    path = config.RAW / filename
    if not path.exists():
        raise FileNotFoundError(f"{path} not found — place the original data pack CSVs in data/raw/")
    return pd.read_csv(path, **kwargs)


def load_external(filename: str, **kwargs) -> pd.DataFrame:
    path = config.EXTERNAL / filename
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, **kwargs)
