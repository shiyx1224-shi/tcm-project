"""Train / evaluate the Huang-inspired AdaptedCrossFGCNN on TCM-SD partitions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import log_loss
from torch.utils.data import DataLoader, TensorDataset

from ..compare_models import write_model_comparison
from ..evaluation import evaluate_multiclass
from ..load import project_root
from .fields import (
    N_VIRTUAL_FIELDS,
    build_train_vocab,
    encode_labels,
    frame_to_field_ids,
)
from .model import AdaptedCrossFGCNN, count_parameters


def _class_weights(y: np.ndarray, n_classes: int) -> torch.Tensor:
    counts = np.bincount(y, minlength=n_classes).astype(np.float64)
    counts[counts == 0] = 1.0
    weights = counts.sum() / (n_classes * counts)
    return torch.tensor(weights, dtype=torch.float32)


@torch.no_grad()
def _predict(model: AdaptedCrossFGCNN, loader: DataLoader, device: torch.device) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    preds, probs = [], []
    for xb, _ in loader:
        xb = xb.to(device)
        logits = model(xb)
        p = torch.softmax(logits, dim=1)
        preds.append(logits.argmax(dim=1).cpu().numpy())
        probs.append(p.cpu().numpy())
    return np.concatenate(preds), np.concatenate(probs)


def _plot_curves(history: dict[str, list[float]], out_path: Path) -> None:
    epochs = range(1, len(history["train_loss"]) + 1)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(epochs, history["train_loss"], label="train", color="#1f4e79")
    axes[0].plot(epochs, history["val_loss"], label="validation", color="#c45c26")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Cross-entropy loss")
    axes[0].set_title("Huang-inspired CNN — loss")
    axes[0].legend(frameon=False)
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)

    axes[1].plot(epochs, history["train_acc"], label="train", color="#1f4e79")
    axes[1].plot(epochs, history["val_acc"], label="validation", color="#c45c26")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].set_title("Huang-inspired CNN — accuracy")
    axes[1].legend(frameon=False)
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def train_huang_cnn(
    root: Path | None = None,
    epochs: int = 8,
    batch_size: int = 256,
    lr: float = 1e-3,
    embed_dim: int = 16,
    n_cross_layers: int = 6,
    dropout: float = 0.2,
    seed: int = 42,
) -> dict[str, Any]:
    root = root or project_root()
    processed = root / "data" / "processed"
    out_dir = root / "artifacts" / "models" / "huang_cnn"
    fig_dir = root / "results" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device("cpu")

    train_df = pd.read_parquet(processed / "train_rows.parquet")
    val_df = pd.read_parquet(processed / "validation_rows.parquet")

    # Vocab + field ids from TRAIN text only (no val/test leakage into vocab)
    vocab = build_train_vocab(train_df)
    y_train, y_val, class_names = encode_labels(train_df, val_df)
    # Re-filter val_df to match encode_labels mask
    known = set(class_names)
    val_df = val_df.loc[val_df["norm_syndrome"].astype(str).isin(known)].copy()

    X_train = frame_to_field_ids(train_df, vocab)
    X_val = frame_to_field_ids(val_df, vocab)
    assert X_train.shape[1] == N_VIRTUAL_FIELDS

    n_classes = len(class_names)
    train_ds = TensorDataset(
        torch.from_numpy(X_train),
        torch.from_numpy(y_train),
    )
    val_ds = TensorDataset(
        torch.from_numpy(X_val),
        torch.from_numpy(y_val),
    )
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    # Loader yielding (x, y) for predict helper that ignores y
    val_pred_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    model = AdaptedCrossFGCNN(
        vocab_size=vocab.size,
        n_fields=N_VIRTUAL_FIELDS,
        embed_dim=embed_dim,
        n_classes=n_classes,
        n_cross_layers=n_cross_layers,
        dropout=dropout,
    ).to(device)

    weights = _class_weights(y_train, n_classes).to(device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=2
    )

    history: dict[str, list[float]] = {
        "train_loss": [],
        "val_loss": [],
        "train_acc": [],
        "val_acc": [],
    }
    best_val_acc = -1.0
    best_state = None

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        running_correct = 0
        running_n = 0
        for xb, yb in train_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            optimizer.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            running_loss += loss.item() * len(yb)
            running_correct += (logits.argmax(1) == yb).sum().item()
            running_n += len(yb)

        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_n = 0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb = xb.to(device)
                yb = yb.to(device)
                logits = model(xb)
                loss = criterion(logits, yb)
                val_loss += loss.item() * len(yb)
                val_correct += (logits.argmax(1) == yb).sum().item()
                val_n += len(yb)

        tr_loss = running_loss / running_n
        va_loss = val_loss / val_n
        tr_acc = running_correct / running_n
        va_acc = val_correct / val_n
        history["train_loss"].append(tr_loss)
        history["val_loss"].append(va_loss)
        history["train_acc"].append(tr_acc)
        history["val_acc"].append(va_acc)
        scheduler.step(va_acc)
        print(
            f"epoch {epoch}/{epochs}  "
            f"train_loss={tr_loss:.4f} acc={tr_acc:.4f}  "
            f"val_loss={va_loss:.4f} acc={va_acc:.4f}",
            flush=True,
        )
        if va_acc >= best_val_acc:
            best_val_acc = va_acc
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)

    y_pred, y_prob = _predict(model, val_pred_loader, device)
    metrics = evaluate_multiclass(y_val, y_pred, class_names)
    # Huang also reports log-loss
    try:
        metrics["log_loss"] = float(log_loss(y_val, y_prob, labels=list(range(n_classes))))
    except Exception as exc:  # noqa: BLE001
        metrics["log_loss"] = None
        metrics["log_loss_error"] = str(exc)

    metrics["model"] = {
        "type": "AdaptedCrossFGCNN",
        "inspired_by": "Huang et al. 2022 Cross-FGCNN (JMIR Med Inform)",
        "exact_reproduction": False,
        "task_type": "multiclass",
        "n_train": int(len(y_train)),
        "n_validation": int(len(y_val)),
        "n_features": int(N_VIRTUAL_FIELDS),
        "n_classes": n_classes,
        "embed_dim": embed_dim,
        "n_cross_layers": n_cross_layers,
        "dropout": dropout,
        "epochs": epochs,
        "batch_size": batch_size,
        "lr": lr,
        "n_parameters": count_parameters(model),
        "vocab_size": vocab.size,
        "best_val_accuracy_during_train": float(best_val_acc),
    }
    metrics["holdout_policy"] = {
        "validation_used_for": "epoch model selection (best val accuracy) and reported metrics",
        "test_used": False,
        "note": "Same train/validation row partitions as RF / LR / SVM.",
    }
    metrics["huang_mapping"] = {
        "from_paper": [
            "Field-style embeddings",
            "Deep & Cross–style cross network (6 layers in paper; used here too)",
            "FGCNN-style conv → pool → tanh recombination (3 stages)",
            "Concatenate cross vector C with nonlinear vector F",
            "MLP classifier + dropout 0.2 + Adam lr 0.001 + cross-entropy",
        ],
        "adaptations": [
            "TCM-SD free text → 60 virtual character-position slots (not 60 TCM diagnostic fields)",
            "148 multiclass syndromes (not 9 dysmenorrhea labels)",
            "MLP widths 512/256/128 (paper 1024/512/128) for CPU tractability",
            "Class-weighted cross-entropy for long-tailed TCM-SD labels",
            "Epoch-based training with best-validation checkpoint (paper reported 1000 iterations)",
            "LayerNorm inside cross layers + grad clipping for stability (not specified by Huang)",
            "Character/bigram virtual field codes instead of clinician-coded symptom fields",
        ],
        "not_claimed": "Exact numerical reproduction of Huang et al. dysmenorrhea results",
    }

    # Persist artifacts
    torch.save(
        {
            "model_state": model.state_dict(),
            "vocab": vocab.char2id,
            "class_names": class_names,
            "config": {
                "n_fields": N_VIRTUAL_FIELDS,
                "embed_dim": embed_dim,
                "n_cross_layers": n_cross_layers,
                "dropout": dropout,
                "n_classes": n_classes,
                "vocab_size": vocab.size,
            },
        },
        out_dir / "huang_cnn.pt",
    )
    joblib.dump(
        {"vocab": vocab, "class_names": class_names},
        out_dir / "huang_cnn_meta.joblib",
    )

    summary = {k: v for k, v in metrics.items() if k != "classification_report"}
    (out_dir / "validation_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "training_history.json").write_text(
        json.dumps(history, indent=2),
        encoding="utf-8",
    )
    _plot_curves(history, fig_dir / "huang_cnn_training_curves.png")
    pd.DataFrame(
        {
            "y_true_index": y_val[:50],
            "y_pred_index": y_pred[:50],
            "y_true_label": [class_names[i] for i in y_val[:50]],
            "y_pred_label": [class_names[i] for i in y_pred[:50]],
        }
    ).to_csv(out_dir / "validation_preview.csv", index=False)

    # Refresh comparison table/figure including this CNN
    try:
        write_model_comparison(root)
    except Exception as exc:  # noqa: BLE001
        print(f"Warning: could not refresh model comparison: {exc}", flush=True)

    return {
        "artifacts": str(out_dir),
        "validation_summary": summary,
        "history": history,
    }
