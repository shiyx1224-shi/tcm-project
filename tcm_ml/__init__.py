"""TCM-SD ML package: split, preprocess, and traditional ML baselines."""

from .checks import assert_no_feature_label_leakage, assert_no_split_overlap
from .load import load_tcm_sd
from .logistic_regression import (
    SyndromeLogisticRegressionPipeline,
    train_logistic_regression,
)
from .preprocess import SyndromePreprocessor
from .random_forest import SyndromeRandomForestPipeline, train_random_forest
from .split import make_leakage_safe_groups, split_groups_70_10_20
from .svm import SyndromeSVMPipeline, train_svm

# Huang CNN is imported lazily via tcm_ml.huang_cnn (requires torch)

__all__ = [
    "load_tcm_sd",
    "make_leakage_safe_groups",
    "split_groups_70_10_20",
    "SyndromePreprocessor",
    "SyndromeRandomForestPipeline",
    "train_random_forest",
    "SyndromeLogisticRegressionPipeline",
    "train_logistic_regression",
    "SyndromeSVMPipeline",
    "train_svm",
    "assert_no_split_overlap",
    "assert_no_feature_label_leakage",
]
