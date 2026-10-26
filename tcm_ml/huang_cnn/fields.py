"""Build Huang-inspired field tensors from TCM-SD free text.

Huang et al. (2022) use 60 standardized four-examination symptom *fields*
(label-encoded → one-hot → embedding). TCM-SD does **not** provide that
schema. Here each of the three clinical text columns is sliced into 20
character-position slots (60 slots total) so the model can consume a
field-embedding matrix of similar width. This is an adaptation, not the
paper's TCM field ontology.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from ..load import TARGET_COL, TEXT_FEATURE_COLS

PAD_ID = 0
UNK_ID = 1
SLOTS_PER_TEXT_FIELD = 20
N_VIRTUAL_FIELDS = SLOTS_PER_TEXT_FIELD * len(TEXT_FEATURE_COLS)  # 60


@dataclass
class FieldVocab:
    char2id: dict[str, int]
    id2char: dict[int, str]

    @property
    def size(self) -> int:
        return len(self.char2id)

    @staticmethod
    def build(texts: Iterable[str], max_chars: int = 8000) -> "FieldVocab":
        counts: dict[str, int] = {}
        for text in texts:
            for ch in str(text):
                if ch.isspace():
                    continue
                counts[ch] = counts.get(ch, 0) + 1
        # Keep frequent chars; reserve 0=PAD, 1=UNK
        ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[: max_chars - 2]
        char2id = {"<PAD>": PAD_ID, "<UNK>": UNK_ID}
        for ch, _ in ordered:
            char2id[ch] = len(char2id)
        id2char = {i: c for c, i in char2id.items()}
        return FieldVocab(char2id=char2id, id2char=id2char)

    def encode_char(self, ch: str) -> int:
        return self.char2id.get(ch, UNK_ID)


def _slots_from_text(text: str, vocab: FieldVocab, n_slots: int) -> list[int]:
    """Map a free-text field into n_slots categorical ids.

    Uses overlapping character bigrams when possible (richer than single
    character sampling) so each virtual field resembles a sparse categorical
    symptom code more closely than a raw char index.
    """
    chars = [c for c in str(text) if not c.isspace()]
    if not chars:
        return [PAD_ID] * n_slots
    # Build bigram token ids (hash into vocab space via first char id + offset)
    tokens: list[int] = []
    for i, ch in enumerate(chars):
        tokens.append(vocab.encode_char(ch))
        if i + 1 < len(chars):
            # Combine two char ids into a stable pseudo-id within vocab range
            a = vocab.encode_char(ch)
            b = vocab.encode_char(chars[i + 1])
            tokens.append(UNK_ID + 1 + ((a * 397 + b) % max(vocab.size - 2, 1)))
    positions = np.linspace(0, len(tokens) - 1, num=n_slots)
    return [int(tokens[int(round(p))]) for p in positions]


def frame_to_field_ids(frame: pd.DataFrame, vocab: FieldVocab) -> np.ndarray:
    """Return int64 array (n_samples, 60) of virtual field token ids."""
    cols = [frame[c].fillna("").astype(str).tolist() for c in TEXT_FEATURE_COLS]
    n = len(frame)
    out = np.zeros((n, N_VIRTUAL_FIELDS), dtype=np.int64)
    for i in range(n):
        offset = 0
        for col_vals in cols:
            slots = _slots_from_text(col_vals[i], vocab, SLOTS_PER_TEXT_FIELD)
            out[i, offset : offset + SLOTS_PER_TEXT_FIELD] = slots
            offset += SLOTS_PER_TEXT_FIELD
    return out


def build_train_vocab(train_df: pd.DataFrame) -> FieldVocab:
    texts = []
    for col in TEXT_FEATURE_COLS:
        texts.extend(train_df[col].fillna("").astype(str).tolist())
    return FieldVocab.build(texts)


def encode_labels(train_df: pd.DataFrame, val_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[str]]:
    classes = sorted(train_df[TARGET_COL].astype(str).unique().tolist())
    class_to_idx = {c: i for i, c in enumerate(classes)}
    y_train = np.asarray([class_to_idx[c] for c in train_df[TARGET_COL].astype(str)], dtype=np.int64)
    # Drop validation rows with unseen labels (should be none in our split)
    val_mask = val_df[TARGET_COL].astype(str).isin(class_to_idx)
    val_df = val_df.loc[val_mask]
    y_val = np.asarray([class_to_idx[c] for c in val_df[TARGET_COL].astype(str)], dtype=np.int64)
    return y_train, y_val, classes
