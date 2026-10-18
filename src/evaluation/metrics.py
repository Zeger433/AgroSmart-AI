"""Metric helpers for training and evaluation."""

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)


def classification_scores(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: Optional[np.ndarray],
    labels: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """Compute standard multiclass classification metrics.

    Args:
        y_true: Ground-truth integer labels.
        y_pred: Predicted integer labels.
        y_proba: Predicted class probabilities, if available.
        labels: Optional explicit label index array for ROC-AUC.

    Returns:
        Dictionary of scalar metric values.
    """
    out: Dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_weighted": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
    }
    if y_proba is not None and y_proba.ndim == 2:
        try:
            out["roc_auc_macro"] = float(
                roc_auc_score(
                    y_true,
                    y_proba,
                    multi_class="ovr",
                    average="macro",
                    labels=labels,
                )
            )
        except ValueError:
            out["roc_auc_macro"] = None
    else:
        out["roc_auc_macro"] = None
    return out


def regression_scores(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute regression metrics including MAPE (safe for zeros)."""
    mape = float(mean_absolute_percentage_error(y_true, y_pred))
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error_safe(y_true, y_pred))),
        "mape": mape,
    }


def mean_squared_error_safe(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean squared error without extra sklearn import."""
    diff = y_true.astype(float) - y_pred.astype(float)
    return float(np.mean(diff**2))


def confusion_matrix_png(y_true, y_pred, class_names, out_path) -> None:
    """Render and save a confusion matrix figure."""
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay

    fig, ax = plt.subplots(figsize=(12, 10))
    cm = confusion_matrix(y_true, y_pred, labels=np.arange(len(class_names)))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(ax=ax, xticks_rotation=45, cmap="Greens", colorbar=False)
    ax.set_title("Confusion Matrix — Best Crop Classifier")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def model_comparison_bar(
    labels: list,
    values: list,
    y_label: str,
    title: str,
    out_path,
) -> None:
    """Save a simple bar chart comparing models."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(labels))
    ax.bar(x, values, color="#1a3c2e")
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
