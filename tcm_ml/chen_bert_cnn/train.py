"""Train Chen-inspired BERT+TextCNN on TCM-SD train/validation partitions.

CPU note: full-sequence BERT caches for ~38k×128×H do not fit in RAM, so the
frozen encoder is run online each batch (no full embedding dump). That is an
explicit adaptation for this environment.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

from ..compare_models import write_model_comparison
from ..evaluation import evaluate_multiclass
from ..load import TEXT_FEATURE_COLS, TARGET_COL, project_root
from .model import ChenBertCNN

# Compact Chinese BERT-family encoder (CPU-feasible online forwards).
DEFAULT_MODEL_NAME = "hfl/rbt3"


def _encode_labels(
    train_df: pd.DataFrame, val_df: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray, list[str], pd.DataFrame]:
    classes = sorted(train_df[TARGET_COL].astype(str).unique().tolist())
    class_to_idx = {c: i for i, c in enumerate(classes)}
    y_train = np.asarray(
        [class_to_idx[c] for c in train_df[TARGET_COL].astype(str)], dtype=np.int64
    )
    val_df = val_df.loc[val_df[TARGET_COL].astype(str).isin(class_to_idx)].copy()
    y_val = np.asarray(
        [class_to_idx[c] for c in val_df[TARGET_COL].astype(str)], dtype=np.int64
    )
    return y_train, y_val, classes, val_df


def _texts_from_frame(frame: pd.DataFrame) -> list[str]:
    records = frame[list(TEXT_FEATURE_COLS)].fillna("").astype(str).to_dict(orient="records")
    texts = []
    for row in records:
        parts = [str(row[c]).strip() for c in TEXT_FEATURE_COLS if str(row[c]).strip()]
        texts.append(" [SEP] ".join(parts))
    return texts


class TextLabelDataset(Dataset):
    def __init__(self, texts: list[str], labels: np.ndarray, tokenizer, max_length: int):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        enc = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }


def _class_weights(y: np.ndarray, n_classes: int) -> torch.Tensor:
    counts = np.bincount(y, minlength=n_classes).astype(np.float64)
    counts[counts == 0] = 1.0
    weights = counts.sum() / (n_classes * counts)
    return torch.tensor(weights, dtype=torch.float32)


def _plot_curves(history: dict[str, list[float]], out_path: Path) -> None:
    epochs = range(1, len(history["train_loss"]) + 1)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(epochs, history["train_loss"], color="#1f4e79", label="train")
    axes[0].plot(epochs, history["val_loss"], color="#c45c26", label="validation")
    axes[0].set_title("Chen-inspired BERT+CNN — loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Cross-entropy")
    axes[0].legend(frameon=False)
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)

    axes[1].plot(epochs, history["train_acc"], color="#1f4e79", label="train")
    axes[1].plot(epochs, history["val_acc"], color="#c45c26", label="validation")
    axes[1].set_title("Chen-inspired BERT+CNN — accuracy")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].legend(frameon=False)
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


@torch.no_grad()
def _eval_epoch(
    model: ChenBertCNN,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float, np.ndarray, np.ndarray]:
    model.eval()
    total_loss = correct = n = 0
    preds, labels = [], []
    for batch in loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        yb = batch["labels"].to(device)
        logits = model(input_ids, attention_mask)
        loss = criterion(logits, yb)
        total_loss += loss.item() * len(yb)
        pred = logits.argmax(1)
        correct += (pred == yb).sum().item()
        n += len(yb)
        preds.append(pred.cpu().numpy())
        labels.append(yb.cpu().numpy())
    return total_loss / n, correct / n, np.concatenate(labels), np.concatenate(preds)


def train_chen_bert_cnn(
    root: Path | None = None,
    model_name: str = DEFAULT_MODEL_NAME,
    max_length: int = 96,
    epochs: int = 4,
    batch_size: int = 24,
    lr: float = 1e-3,
    dropout: float = 0.2,
    seed: int = 42,
) -> dict[str, Any]:
    root = root or project_root()
    processed = root / "data" / "processed"
    out_dir = root / "artifacts" / "models" / "chen_bert_cnn"
    fig_dir = root / "results" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device("cpu")

    train_df = pd.read_parquet(processed / "train_rows.parquet")
    val_df = pd.read_parquet(processed / "validation_rows.parquet")
    y_train, y_val, class_names, val_df = _encode_labels(train_df, val_df)
    n_classes = len(class_names)

    train_texts = _texts_from_frame(train_df)
    val_texts = _texts_from_frame(val_df)

    print(f"Loading tokenizer/model: {model_name}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    bert = AutoModel.from_pretrained(model_name)
    model = ChenBertCNN(bert, n_classes=n_classes, freeze_bert=True, dropout=dropout).to(device)

    train_loader = DataLoader(
        TextLabelDataset(train_texts, y_train, tokenizer, max_length),
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
    )
    val_loader = DataLoader(
        TextLabelDataset(val_texts, y_val, tokenizer, max_length),
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )

    weights = _class_weights(y_train, n_classes).to(device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.Adam(model.head.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=1
    )

    history: dict[str, list[float]] = {
        "train_loss": [],
        "val_loss": [],
        "train_acc": [],
        "val_acc": [],
    }
    best_val_acc = -1.0
    best_state = None
    n_train_batches = len(train_loader)

    for epoch in range(1, epochs + 1):
        model.train()
        # Keep BERT frozen/eval for BatchNorm/Dropout stability in encoder
        model.bert.eval()
        running_loss = running_correct = running_n = 0
        for i, batch in enumerate(train_loader, start=1):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            yb = batch["labels"].to(device)
            optimizer.zero_grad()
            logits = model(input_ids, attention_mask)
            loss = criterion(logits, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.head.parameters(), 1.0)
            optimizer.step()
            running_loss += loss.item() * len(yb)
            running_correct += (logits.argmax(1) == yb).sum().item()
            running_n += len(yb)
            if i == 1 or i % 100 == 0 or i == n_train_batches:
                print(
                    f"  epoch {epoch} batch {i}/{n_train_batches} "
                    f"loss={loss.item():.4f}",
                    flush=True,
                )

        tr_loss = running_loss / running_n
        tr_acc = running_correct / running_n
        va_loss, va_acc, _, _ = _eval_epoch(model, val_loader, criterion, device)
        history["train_loss"].append(tr_loss)
        history["val_loss"].append(va_loss)
        history["train_acc"].append(tr_acc)
        history["val_acc"].append(va_acc)
        scheduler.step(va_acc)
        print(
            f"epoch {epoch}/{epochs}  train_loss={tr_loss:.4f} acc={tr_acc:.4f}  "
            f"val_loss={va_loss:.4f} acc={va_acc:.4f}",
            flush=True,
        )
        if va_acc >= best_val_acc:
            best_val_acc = va_acc
            best_state = {
                "head": {k: v.detach().cpu().clone() for k, v in model.head.state_dict().items()},
            }

    if best_state is not None:
        model.head.load_state_dict(best_state["head"])

    _, _, y_true, y_pred = _eval_epoch(model, val_loader, criterion, device)
    metrics = evaluate_multiclass(y_true, y_pred, class_names)

    n_params_head = sum(p.numel() for p in model.head.parameters())
    metrics["model"] = {
        "type": "ChenBertCNN_adapted",
        "inspired_by": "Chen et al. 2024 TCM-BERT-CNN (Integrative Medicine Research)",
        "exact_reproduction": False,
        "backbone": model_name,
        "bert_finetuned": False,
        "bert_frozen_online": True,
        "task_type": "multiclass",
        "n_train": int(len(y_train)),
        "n_validation": int(len(y_val)),
        "n_features": int(max_length),
        "n_classes": n_classes,
        "max_length": max_length,
        "epochs": epochs,
        "batch_size": batch_size,
        "lr": lr,
        "dropout": dropout,
        "n_parameters_trainable": n_params_head,
        "best_val_accuracy_during_train": float(best_val_acc),
    }
    metrics["holdout_policy"] = {
        "validation_used_for": "epoch checkpointing and reported metrics",
        "test_used": False,
        "note": "Same train/validation partitions as RF / LR / SVM / Huang CNN.",
    }
    metrics["chen_mapping"] = {
        "from_paper": [
            "Clinical symptom text as model input",
            "BERT contextual token representations",
            "TextCNN over BERT sequence features",
            "Precision / recall / F1 emphasized under imbalance",
        ],
        "adaptations": [
            "Frozen compact Chinese BERT-family encoder (hfl/rbt3) with online forwards "
            "(full embedding cache OOMs on CPU; not end-to-end bert-base-chinese finetune)",
            "148-way Softmax multiclass head (not Softmax exterior/interior & deficiency/excess "
            "pairs + Sigmoid 17-label group)",
            "TCM-SD clinical records instead of guideline/textbook expert-knowledge corpus",
            "Project 70/10/20 validation protocol instead of 10-fold CV",
            "Class-weighted cross-entropy",
        ],
        "why_not_gong": (
            "Gong et al. 2023 ML-PRDF requires multi-label syndrome targets and a binary "
            "symptom matrix; TCM-SD is single-label multiclass free text, so multi-label "
            "deep forest cannot be implemented faithfully here."
        ),
        "not_claimed": "Exact numerical reproduction of Chen et al. TCM-BERT-CNN results",
    }

    torch.save(
        {
            "head_state": model.head.state_dict(),
            "class_names": class_names,
            "config": {
                "model_name": model_name,
                "max_length": max_length,
                "hidden_size": int(model.bert.config.hidden_size),
                "n_classes": n_classes,
                "dropout": dropout,
                "freeze_bert": True,
            },
        },
        out_dir / "chen_bert_cnn.pt",
    )

    summary = {k: v for k, v in metrics.items() if k != "classification_report"}
    (out_dir / "validation_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "training_history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    _plot_curves(history, fig_dir / "chen_bert_cnn_training_curves.png")
    pd.DataFrame(
        {
            "y_true_index": y_true[:50],
            "y_pred_index": y_pred[:50],
            "y_true_label": [class_names[i] for i in y_true[:50]],
            "y_pred_label": [class_names[i] for i in y_pred[:50]],
        }
    ).to_csv(out_dir / "validation_preview.csv", index=False)

    try:
        write_model_comparison(root)
    except Exception as exc:  # noqa: BLE001
        print(f"Warning: comparison refresh failed: {exc}", flush=True)

    return {"artifacts": str(out_dir), "validation_summary": summary, "history": history}
