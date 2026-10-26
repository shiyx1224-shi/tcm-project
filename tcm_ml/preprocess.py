"""Train-only preprocessing: missing values, text TF-IDF, numerics, labels."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

from .load import TARGET_COL, TEXT_FEATURE_COLS


def _combine_text(frame: pd.DataFrame) -> pd.Series:
    parts = [frame[c].fillna("").astype(str).str.strip() for c in TEXT_FEATURE_COLS]
    combined = parts[0]
    for part in parts[1:]:
        combined = combined + " [SEP] " + part
    return combined


def _numeric_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Engineered numerical descriptors from clinical text (no labels)."""
    out = pd.DataFrame(index=frame.index)
    for col in TEXT_FEATURE_COLS:
        text = frame[col].fillna("").astype(str)
        out[f"{col}_char_len"] = text.str.len().astype(float)
        out[f"{col}_token_approx"] = text.str.count(r"\S+").astype(float)
    out["total_char_len"] = out[[f"{c}_char_len" for c in TEXT_FEATURE_COLS]].sum(axis=1)
    return out


def _categorical_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Lightweight categorical bins derived only from text length (not disease IDs).

    TCM-SD has no native symptom categorical matrix. We avoid lcd_name/lcd_id
    because they are leakage-prone for a symptoms→syndrome research question.
    """
    lengths = frame["description"].fillna("").astype(str).str.len()
    bins = pd.cut(
        lengths,
        bins=[-0.1, 50, 150, 400, 10_000],
        labels=["very_short", "short", "medium", "long"],
    )
    return pd.DataFrame({"description_length_bin": bins.astype(str)}, index=frame.index)


@dataclass
class TransformedSplit:
    name: str
    X: sparse.csr_matrix
    y: np.ndarray
    y_labels: np.ndarray
    row_index: np.ndarray
    n_unknown_labels: int


class SyndromePreprocessor:
    """Fit on training rows only; transform validation/test without refitting."""

    def __init__(
        self,
        max_tfidf_features: int = 20000,
        select_k: int = 5000,
        random_state: int = 42,
    ) -> None:
        self.max_tfidf_features = max_tfidf_features
        self.select_k = select_k
        self.random_state = random_state

        self.tfidf = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
            min_df=2,
            max_features=max_tfidf_features,
            lowercase=False,
            sublinear_tf=True,
        )
        self.scaler = StandardScaler()
        self.onehot = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
        self.label_encoder = LabelEncoder()
        self.selector: SelectKBest | None = None
        self.feature_blocks_: dict[str, slice] | None = None
        self.fitted_: bool = False

    def _prepare_feature_frames(
        self, frame: pd.DataFrame, *, require_target: bool
    ) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame, pd.Series | None]:
        # Missing-value handling for text: empty string; numerics filled after engineering
        clean = frame.copy()
        for col in TEXT_FEATURE_COLS:
            if col not in clean.columns:
                clean[col] = ""
            clean[col] = clean[col].fillna("").astype(str)

        y: pd.Series | None = None
        if require_target:
            if TARGET_COL not in clean.columns:
                raise KeyError(f"Missing target column {TARGET_COL}")
            mask = clean[TARGET_COL].fillna("").astype(str).str.strip() != ""
            clean = clean.loc[mask].copy()
            y = clean[TARGET_COL].astype(str)
        else:
            # Inference: keep rows that have at least some clinical text
            text_lens = sum(clean[c].str.strip().str.len() for c in TEXT_FEATURE_COLS)
            clean = clean.loc[text_lens > 0].copy()
            if clean.empty:
                raise ValueError("No non-empty clinical text fields to transform.")

        text = _combine_text(clean)
        numeric = _numeric_frame(clean).fillna(0.0)
        categorical = _categorical_frame(clean).fillna("missing")
        return clean, text, numeric, categorical, y

    def _prepare_xy_frames(self, frame: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame, pd.Series]:
        _, text, numeric, categorical, y = self._prepare_feature_frames(frame, require_target=True)
        assert y is not None
        return text, numeric, categorical, y

    def transform_features(self, frame: pd.DataFrame) -> sparse.csr_matrix:
        """Transform clinical text into the model feature matrix (no labels required)."""
        if not self.fitted_ or self.selector is None:
            raise RuntimeError("Call fit() on training data before transform_features().")
        _, text, numeric, categorical, _ = self._prepare_feature_frames(frame, require_target=False)
        X_text = self.tfidf.transform(text)
        X_num = self.scaler.transform(numeric)
        X_cat = self.onehot.transform(categorical)
        X = sparse.hstack(
            [X_text, sparse.csr_matrix(X_num), X_cat],
            format="csr",
        )
        return self.selector.transform(X).tocsr()

    def fit(self, train_df: pd.DataFrame) -> "SyndromePreprocessor":
        text, numeric, categorical, y = self._prepare_xy_frames(train_df)

        X_text = self.tfidf.fit_transform(text)
        X_num = self.scaler.fit_transform(numeric)
        X_cat = self.onehot.fit_transform(categorical)
        X = sparse.hstack(
            [X_text, sparse.csr_matrix(X_num), X_cat],
            format="csr",
        )

        y_enc = self.label_encoder.fit_transform(y)
        k = min(self.select_k, X.shape[1])
        self.selector = SelectKBest(score_func=chi2, k=k)
        # chi2 requires non-negative features; TF-IDF/OHE are >=0, scaled numerics may be negative
        # Shift numeric block to non-negative for selection scoring only via absolute value copy
        X_for_select = X.copy()
        # numeric columns sit after tfidf
        n_text = X_text.shape[1]
        n_num = X_num.shape[1]
        num_block = X_for_select[:, n_text : n_text + n_num]
        X_for_select[:, n_text : n_text + n_num] = abs(num_block)
        self.selector.fit(X_for_select, y_enc)

        self.feature_blocks_ = {
            "tfidf": slice(0, n_text),
            "numeric": slice(n_text, n_text + n_num),
            "categorical": slice(n_text + n_num, X.shape[1]),
        }
        self.fitted_ = True
        return self

    def transform(self, frame: pd.DataFrame, name: str) -> TransformedSplit:
        if not self.fitted_ or self.selector is None:
            raise RuntimeError("Call fit() on training data before transform().")

        text, numeric, categorical, y = self._prepare_xy_frames(frame)
        X_text = self.tfidf.transform(text)
        X_num = self.scaler.transform(numeric)
        X_cat = self.onehot.transform(categorical)
        X = sparse.hstack(
            [X_text, sparse.csr_matrix(X_num), X_cat],
            format="csr",
        )
        X_sel = self.selector.transform(X)

        known = set(self.label_encoder.classes_)
        unknown_mask = ~y.isin(known)
        n_unknown = int(unknown_mask.sum())
        # Map known labels; unknown get -1 and should be excluded from supervised metrics later
        y_enc = np.full(len(y), -1, dtype=int)
        known_idx = np.where(~unknown_mask)[0]
        if len(known_idx):
            y_enc[known_idx] = self.label_encoder.transform(y.iloc[known_idx])

        return TransformedSplit(
            name=name,
            X=X_sel.tocsr(),
            y=y_enc,
            y_labels=y.to_numpy(),
            row_index=y.index.to_numpy(),
            n_unknown_labels=n_unknown,
        )

    def fit_transform_parts(
        self, parts: dict[str, pd.DataFrame]
    ) -> dict[str, TransformedSplit]:
        self.fit(parts["train"])
        return {name: self.transform(frame, name) for name, frame in parts.items()}

    def save(self, directory) -> None:
        from pathlib import Path

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, directory / "syndrome_preprocessor.joblib")
        meta = {
            "max_tfidf_features": self.max_tfidf_features,
            "select_k": self.select_k,
            "random_state": self.random_state,
            "n_classes": int(len(self.label_encoder.classes_)),
            "classes": self.label_encoder.classes_.tolist(),
            "text_features": list(TEXT_FEATURE_COLS),
            "fitted": self.fitted_,
        }
        (directory / "preprocessor_meta.json").write_text(
            __import__("json").dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def load(directory) -> "SyndromePreprocessor":
        from pathlib import Path

        return joblib.load(Path(directory) / "syndrome_preprocessor.joblib")
