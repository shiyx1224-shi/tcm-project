"""Load the TCM-SD release from data/raw/TCM-SD."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

TEXT_FEATURE_COLS = ("chief_complaint", "description", "detection")
TARGET_COL = "norm_syndrome"
ID_COL = "user_id"
LEAKAGE_COLS = ("syndrome", "norm_syndrome", "lcd_id", "lcd_name", "user_id")


def project_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "data" / "raw" / "TCM-SD").exists():
            return candidate
    raise FileNotFoundError("Could not locate data/raw/TCM-SD from the current directory.")


def raw_dir(root: Path | None = None) -> Path:
    root = root or project_root()
    path = root / "data" / "raw" / "TCM-SD"
    if not (path / "test.json").exists():
        raise FileNotFoundError(f"Missing TCM-SD files under {path}")
    train = path / "train.json"
    if not train.exists():
        zipped = path / "TCM_SD_train_dev.zip"
        if zipped.exists():
            import zipfile

            with zipfile.ZipFile(zipped) as archive:
                archive.extractall(path)
        else:
            raise FileNotFoundError(f"Missing {train}; run bash scripts/download_tcm_sd.sh")
    return path


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_tcm_sd(root: Path | None = None, official_splits: bool = False) -> pd.DataFrame:
    """Load all TCM-SD rows into one frame.

    By default ignores the upstream train/dev/test markers so we can build a
    custom 70/10/20 split. Pass official_splits=True to keep a `source_split`
    column for reference only.
    """
    path = raw_dir(root)
    frames = []
    for name in ("train", "dev", "test"):
        part = pd.DataFrame(_read_jsonl(path / f"{name}.json"))
        if official_splits:
            part["source_split"] = name
        frames.append(part)
    df = pd.concat(frames, ignore_index=True)
    for col in TEXT_FEATURE_COLS:
        df[col] = df[col].fillna("").astype(str)
    df[TARGET_COL] = df[TARGET_COL].fillna("").astype(str)
    df[ID_COL] = df[ID_COL].fillna("").astype(str)
    df["case_fingerprint"] = (
        df["chief_complaint"].str.strip()
        + " || "
        + df["description"].str.strip()
        + " || "
        + df["detection"].str.strip()
    )
    return df
