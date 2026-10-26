"""Adapted Cross-FGCNN (Huang et al., 2022) in PyTorch.

Faithful elements
-----------------
- Field embeddings feeding a Deep & Cross–style **cross network**
- Nonlinear **CNN + recombination** branch (FGCNN-inspired)
- Concatenate linear-cross vector C and nonlinear vector F
- MLP classifier + dropout + cross-entropy

Adaptations (not exact reproduction)
------------------------------------
- 60 *virtual character-position slots* from TCM-SD free text, not Huang's
  60 standardized TCM diagnostic fields / one-hot field values
- 148 TCM-SD syndromes, not 9 dysmenorrhea classes
- Slightly reduced MLP widths and CNN depths for CPU training
- Embed dim and iteration budget chosen for this repository's compute
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class CrossNetwork(nn.Module):
    """DCN-style cross layers: x_{l+1} = x0 ⊙ (W_l x_l + b_l) + x_l.

    LayerNorm after each step for numerical stability (adaptation; Huang does
    not detail this stabilization).
    """

    def __init__(self, input_dim: int, n_layers: int = 6):
        super().__init__()
        self.n_layers = n_layers
        self.kernels = nn.ModuleList([nn.Linear(input_dim, 1, bias=False) for _ in range(n_layers)])
        self.biases = nn.ParameterList(
            [nn.Parameter(torch.zeros(input_dim)) for _ in range(n_layers)]
        )
        self.norms = nn.ModuleList([nn.LayerNorm(input_dim) for _ in range(n_layers)])

    def forward(self, x0: torch.Tensor) -> torch.Tensor:
        x = x0
        for i in range(self.n_layers):
            xw = self.kernels[i](x)  # (B, 1)
            x = self.norms[i](x0 * xw + self.biases[i] + x)
        return x


class FGCNNBranch(nn.Module):
    """FGCNN-inspired nonlinear branch over the field-embedding matrix.

    Paper: 3 stages, conv depths 14/16/18, kernel width 4, max-pool,
    recombination (FC + tanh). We keep the structure with modest channels.
    """

    def __init__(self, n_fields: int, embed_dim: int, out_dim: int = 256):
        super().__init__()
        # Input as (B, embed_dim, n_fields) — conv along field axis
        self.conv1 = nn.Conv1d(embed_dim, 14, kernel_size=4, padding=1)
        self.conv2 = nn.Conv1d(14, 16, kernel_size=4, padding=1)
        self.conv3 = nn.Conv1d(16, 18, kernel_size=4, padding=1)
        self.pool = nn.MaxPool1d(kernel_size=2, stride=2)
        self.recomb1 = nn.Linear(14, 14)
        self.recomb2 = nn.Linear(16, 16)
        self.recomb3 = nn.Linear(18, 18)
        # Length after 3 pools depends on n_fields; compute lazily via AdaptiveAvgPool
        self.adapt = nn.AdaptiveAvgPool1d(4)
        self.proj = nn.Sequential(
            nn.Linear(18 * 4, out_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
        )

    def _stage(
        self,
        x: torch.Tensor,
        conv: nn.Conv1d,
        recomb: nn.Linear,
    ) -> torch.Tensor:
        h = F.relu(conv(x))
        h = self.pool(h)
        # recombination across channels at each position: (B, C, L) → apply FC on C
        b, c, length = h.shape
        h_t = h.transpose(1, 2)  # (B, L, C)
        h_t = torch.tanh(recomb(h_t))
        return h_t.transpose(1, 2)

    def forward(self, field_emb: torch.Tensor) -> torch.Tensor:
        # field_emb: (B, n_fields, embed_dim) → (B, embed_dim, n_fields)
        x = field_emb.transpose(1, 2)
        x = self._stage(x, self.conv1, self.recomb1)
        x = self._stage(x, self.conv2, self.recomb2)
        x = self._stage(x, self.conv3, self.recomb3)
        x = self.adapt(x)
        x = x.flatten(1)
        return self.proj(x)


class AdaptedCrossFGCNN(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        n_fields: int = 60,
        embed_dim: int = 16,
        n_classes: int = 148,
        n_cross_layers: int = 6,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.n_fields = n_fields
        self.embed_dim = embed_dim
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        cross_in = n_fields * embed_dim
        self.cross = CrossNetwork(cross_in, n_layers=n_cross_layers)
        self.fgcnn = FGCNNBranch(n_fields, embed_dim, out_dim=256)
        # Paper MLP: 1024/512/128 — reduced for 148-class CPU run
        fused = cross_in + 256
        self.classifier = nn.Sequential(
            nn.Linear(fused, 512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, n_classes),
        )

    def forward(self, field_ids: torch.Tensor) -> torch.Tensor:
        # field_ids: (B, n_fields)
        emb = self.embedding(field_ids)  # (B, n_fields, d)
        flat = emb.flatten(1)
        c_vec = self.cross(flat)
        f_vec = self.fgcnn(emb)
        return self.classifier(torch.cat([c_vec, f_vec], dim=1))


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
