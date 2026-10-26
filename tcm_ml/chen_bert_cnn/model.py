"""BERT + TextCNN classifier adapted from Chen et al. 2024 TCM-BERT-CNN.

Paper elements retained: BERT token sequence features + multi-kernel TextCNN
+ classification head.

Adaptation: encoder may be frozen; head is multiclass Softmax over TCM-SD
labels (not Chen's Softmax pairs + Sigmoid multi-label group).
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class TextCNNHead(nn.Module):
    """TextCNN over a token embedding sequence (B, T, H)."""

    def __init__(
        self,
        hidden_size: int,
        n_classes: int,
        channels: int = 128,
        kernel_sizes: tuple[int, ...] = (2, 3, 4, 5),
        dropout: float = 0.2,
    ):
        super().__init__()
        self.convs = nn.ModuleList(
            [nn.Conv1d(hidden_size, channels, kernel_size=k, padding=0) for k in kernel_sizes]
        )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(channels * len(kernel_sizes), n_classes)

    def forward(self, sequence: torch.Tensor, attention_mask: torch.Tensor | None = None) -> torch.Tensor:
        # sequence: (B, T, H) → (B, H, T) for Conv1d
        x = sequence.transpose(1, 2)
        if attention_mask is not None:
            # zero out padded positions before conv
            mask = attention_mask.unsqueeze(1).to(x.dtype)
            x = x * mask
        pooled = []
        for conv in self.convs:
            h = F.relu(conv(x))
            h = F.max_pool1d(h, kernel_size=h.shape[-1]).squeeze(-1)
            pooled.append(h)
        cat = self.dropout(torch.cat(pooled, dim=1))
        return self.classifier(cat)


class ChenBertCNN(nn.Module):
    """Frozen (or trainable) BERT encoder + TextCNN multiclass head."""

    def __init__(self, bert: nn.Module, n_classes: int, freeze_bert: bool = True, dropout: float = 0.2):
        super().__init__()
        self.bert = bert
        hidden = bert.config.hidden_size
        if freeze_bert:
            for p in self.bert.parameters():
                p.requires_grad = False
        self.head = TextCNNHead(hidden, n_classes, dropout=dropout)
        self.freeze_bert = freeze_bert

    def encode(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        if self.freeze_bert:
            with torch.no_grad():
                out = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        else:
            out = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        return out.last_hidden_state

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        seq = self.encode(input_ids, attention_mask)
        return self.head(seq, attention_mask=attention_mask)
