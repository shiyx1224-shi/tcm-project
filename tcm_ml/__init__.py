"""TCM-SD data splitting and preprocessing (no classifier training)."""

from .checks import assert_no_feature_label_leakage, assert_no_split_overlap
from .load import load_tcm_sd
from .preprocess import SyndromePreprocessor
from .split import make_leakage_safe_groups, split_groups_70_10_20

__all__ = [
    "load_tcm_sd",
    "make_leakage_safe_groups",
    "split_groups_70_10_20",
    "SyndromePreprocessor",
    "assert_no_split_overlap",
    "assert_no_feature_label_leakage",
]
