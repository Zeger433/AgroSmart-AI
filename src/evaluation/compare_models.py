"""High-level plotting helpers for evaluation reports.

``crop_metadata.json`` (model names, hold-out accuracy, F1, CV scores) is
written only from ``src/training/train_crop.py``. That script fits a single
``LabelEncoder`` on string labels, uses the resulting integer codes for every
split, fit, and metric call, and passes ``labels=np.arange(len(le.classes_))``
into shared helpers such as ``classification_scores``. Do **not** re-encode
hold-out or predicted labels with a new ``LabelEncoder`` in plotting or ad-hoc
comparison scripts; doing so would desynchronize class indices from the trained
``Pipeline`` and produce misleading accuracy or F1. On merged / imbalanced data,
``accuracy`` and ``f1_macro`` can diverge strongly even when labels are correct;
compare ``accuracy`` to ``f1_weighted`` from the same helper for a support-weighted sanity check.
"""

from __future__ import annotations

from typing import Iterable, Sequence

import matplotlib.pyplot as plt


def plot_horizontal_bar(
    labels: Sequence[str],
    values: Sequence[float],
    title: str,
    xlabel: str,
    out_path: str,
    color: str = "#1a3c2e",
) -> None:
    """Save a horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(list(labels), list(values), color=color)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
