"""Split overlap and target-leakage checks (no model training)."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from .load import ID_COL, LEAKAGE_COLS, TARGET_COL, TEXT_FEATURE_COLS


def assert_no_split_overlap(parts: dict[str, pd.DataFrame]) -> dict:
    """Ensure patients, clinical fingerprints, and leakage groups do not cross splits."""
    report: dict = {"ok": True, "checks": {}}

    def _overlap(series_map: dict[str, set]) -> dict[str, int]:
        names = list(series_map)
        out = {}
        for i, a in enumerate(names):
            for b in names[i + 1 :]:
                out[f"{a}∩{b}"] = len(series_map[a] & series_map[b])
        return out

    patients = {k: set(v[ID_COL]) for k, v in parts.items()}
    cases = {k: set(v["case_fingerprint"]) for k, v in parts.items()}
    groups = {k: set(v["leakage_group"]) for k, v in parts.items()}

    for label, mapping in (
        ("patient_user_id", patients),
        ("case_fingerprint", cases),
        ("leakage_group", groups),
    ):
        overlaps = _overlap(mapping)
        report["checks"][label] = overlaps
        if any(v > 0 for v in overlaps.values()):
            report["ok"] = False

    if not report["ok"]:
        raise AssertionError(f"Split overlap detected: {report['checks']}")
    return report


def assert_no_feature_label_leakage(
    feature_columns: Iterable[str],
    banned: Iterable[str] = LEAKAGE_COLS,
) -> dict:
    """Fail if model feature matrix would include identifiers or label columns."""
    feats = set(feature_columns)
    banned_set = set(banned)
    leaked = sorted(feats & banned_set)
    report = {
        "ok": len(leaked) == 0,
        "feature_columns": sorted(feats),
        "banned_present": leaked,
        "recommended_text_features": list(TEXT_FEATURE_COLS),
        "target": TARGET_COL,
    }
    if leaked:
        raise AssertionError(f"Leakage columns present in features: {leaked}")
    return report


def label_coverage_report(parts: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Which syndrome labels appear in each partition."""
    all_labels = sorted(set().union(*(set(p[TARGET_COL]) for p in parts.values())))
    rows = []
    for label in all_labels:
        row = {"norm_syndrome": label}
        for name, frame in parts.items():
            row[name] = int((frame[TARGET_COL] == label).sum())
        row["missing_from_train"] = row["train"] == 0
        rows.append(row)
    return pd.DataFrame(rows).sort_values("train", ascending=False)
