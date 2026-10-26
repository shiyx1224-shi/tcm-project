"""Leakage-aware 70/10/20 group split for TCM-SD."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .load import ID_COL, TARGET_COL


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def add(self, item: str) -> None:
        self.parent.setdefault(item, item)

    def find(self, item: str) -> str:
        self.add(item)
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def make_leakage_safe_groups(df: pd.DataFrame) -> pd.Series:
    """Connect rows that share a patient id OR identical clinical text.

    Returns a Series of group ids aligned to ``df.index`` so the same patient
    and duplicate clinical cases stay inside one partition.
    """
    uf = UnionFind()
    for idx, row in df[[ID_COL, "case_fingerprint"]].iterrows():
        user_node = f"user:{row[ID_COL]}"
        case_node = f"case:{row['case_fingerprint']}"
        row_node = f"row:{idx}"
        uf.union(row_node, user_node)
        uf.union(row_node, case_node)

    groups = pd.Series(
        {idx: uf.find(f"row:{idx}") for idx in df.index},
        name="leakage_group",
    )
    # Compact to stable integer ids for readability
    mapping = {g: i for i, g in enumerate(sorted(groups.unique()))}
    return groups.map(mapping).astype(int)


def _group_table(df: pd.DataFrame, groups: pd.Series) -> pd.DataFrame:
    tmp = df[[TARGET_COL]].copy()
    tmp["leakage_group"] = groups.to_numpy()
    tmp["n"] = 1
    mode = (
        tmp.groupby(["leakage_group", TARGET_COL])["n"]
        .sum()
        .reset_index()
        .sort_values(["leakage_group", "n"], ascending=[True, False])
        .drop_duplicates("leakage_group")
        .rename(columns={TARGET_COL: "group_label"})
    )
    sizes = tmp.groupby("leakage_group")["n"].sum().rename("group_size")
    return mode.set_index("leakage_group").join(sizes)


def _stratified_group_split(
    group_ids: np.ndarray,
    labels: np.ndarray,
    test_size: float,
    random_state: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Split unique groups with stratification when class counts allow it."""
    label_counts = pd.Series(labels).value_counts()
    rare = set(label_counts[label_counts < 2].index)
    if rare:
        # Fall back to unstratified for robustness with tiny classes
        return train_test_split(
            group_ids,
            test_size=test_size,
            random_state=random_state,
            shuffle=True,
        )

    try:
        return train_test_split(
            group_ids,
            test_size=test_size,
            random_state=random_state,
            shuffle=True,
            stratify=labels,
        )
    except ValueError:
        return train_test_split(
            group_ids,
            test_size=test_size,
            random_state=random_state,
            shuffle=True,
        )


def split_groups_70_10_20(
    df: pd.DataFrame,
    groups: pd.Series | None = None,
    random_state: int = 42,
) -> dict[str, pd.DataFrame]:
    """Create 70% train / 10% validation / 20% test partitions by group.

    Proportions are targeted at the **group** level (then mapped to rows), which
    keeps patients and duplicate clinical cases from crossing splits.
    """
    if groups is None:
        groups = make_leakage_safe_groups(df)
    if not groups.index.equals(df.index):
        groups = groups.reindex(df.index)

    gtable = _group_table(df, groups)
    group_ids = gtable.index.to_numpy()
    labels = gtable["group_label"].to_numpy()

    train_g, temp_g = _stratified_group_split(
        group_ids, labels, test_size=0.30, random_state=random_state
    )
    temp_labels = gtable.loc[temp_g, "group_label"].to_numpy()
    # Of the held-out 30%: 1/3 -> val (10%), 2/3 -> test (20%)
    val_g, test_g = _stratified_group_split(
        temp_g, temp_labels, test_size=2 / 3, random_state=random_state
    )

    assign = {}
    for g in train_g:
        assign[int(g)] = "train"
    for g in val_g:
        assign[int(g)] = "validation"
    for g in test_g:
        assign[int(g)] = "test"

    out = df.copy()
    out["leakage_group"] = groups.to_numpy()
    out["partition"] = out["leakage_group"].map(assign)
    if out["partition"].isna().any():
        raise RuntimeError("Some rows were not assigned a partition.")

    parts = {
        name: out.loc[out["partition"] == name].copy()
        for name in ("train", "validation", "test")
    }
    return parts


def partition_summary(parts: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    total = sum(len(p) for p in parts.values())
    for name, frame in parts.items():
        rows.append(
            {
                "partition": name,
                "n_rows": len(frame),
                "pct_rows": round(100 * len(frame) / total, 2),
                "n_groups": frame["leakage_group"].nunique(),
                "n_patients": frame[ID_COL].nunique(),
                "n_labels": frame[TARGET_COL].nunique(),
            }
        )
    return pd.DataFrame(rows)
