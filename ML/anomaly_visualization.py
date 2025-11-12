"""
Rich anomaly-visualization module for the monthly X dataset.

Usage:
    - Run as a script to use the built-in sample dataset.
    - Import from a notebook and call `render_dashboard(...)`, passing your own
      matrix/DataFrame and (optionally) precomputed anomalies to reuse the
      stylized plots only.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec

from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler, minmax_scale
from sklearn.svm import OneClassSVM

try:
    import seaborn as sns

    sns.set_theme(style="whitegrid", context="talk")
except ImportError:
    sns = None
    plt.style.use("seaborn-whitegrid")


DEFAULT_MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def load_dataset() -> pd.DataFrame:
    """Return the canonical monthly dataset as a DataFrame."""
    series_labels = [f"Object_{idx + 1}" for idx in range(10)]
    data = np.array(
        [
            [5.8, 5.9, 5.8, 5.7, 5.8, 5.9, 5.7, 5.5, 5.8, 5.8, 5.7, 5.8],
            [5.6, 5.8, 5.7, 5.6, 5.7, 5.9, 5.6, 5.5, 5.7, 5.6, 5.5, 5.9],
            [5.9, 5.8, 5.8, 5.8, 5.7, 5.8, 5.4, 5.0, 5.9, 5.9, 5.8, 5.8],
            [6.0, 6.0, 5.8, 5.7, 5.8, 5.9, 5.9, 5.9, 5.7, 5.9, 5.6, 5.7],
            [5.9, 6.0, 5.8, 5.9, 5.8, 5.8, 5.9, 5.6, 5.9, 5.9, 5.9, 5.9],
            [5.8, 5.9, 5.6, 5.9, 6.0, 5.9, 5.8, 5.8, 5.6, 5.9, 5.9, 5.8],
            [6.0, 6.0, 6.0, 5.7, 6.0, 5.9, 5.9, 5.7, 6.0, 5.9, 5.9, 6.0],
            [5.5, 5.8, 5.8, 5.8, 5.9, 5.8, 5.9, 5.7, 5.9, 6.0, 5.9, 5.9],
            [5.3, 5.4, 5.8, 5.8, 5.5, 5.4, 5.9, 5.7, 5.7, 5.9, 5.8, 5.6],
            [4.6, 5.5, 5.8, 5.6, 5.5, 5.4, 5.9, 5.5, 5.5, 5.9, 5.9, 5.3],
        ],
        dtype=float,
    )
    return pd.DataFrame(data, index=series_labels, columns=DEFAULT_MONTHS)


def dataframe_from_matrix(
    X: np.ndarray,
    *,
    labels: Optional[List[str]] = None,
    months: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Convert a numpy matrix to a DataFrame with optional labels."""
    arr = np.asarray(X, dtype=float)
    n_rows, n_cols = arr.shape

    if labels is None:
        labels = [f"Object_{idx + 1}" for idx in range(n_rows)]
    if months is None:
        months = DEFAULT_MONTHS[:n_cols]
        if len(months) < n_cols:
            months = [f"Month_{idx + 1}" for idx in range(n_cols)]

    if len(labels) != n_rows or len(months) != n_cols:
        raise ValueError("labels/months must match X dimensions.")

    return pd.DataFrame(arr, index=labels, columns=months)


def detect_anomalies(
    df: pd.DataFrame, contamination: float = 0.2, random_state: int = 42
) -> Tuple[pd.DataFrame, List[str]]:
    """Return the anomaly score table and detected labels (descending score)."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)

    iso = IsolationForest(contamination=contamination, random_state=random_state)
    iso_scores = minmax_scale(-iso.fit(X_scaled).score_samples(X_scaled))

    ocsvm = OneClassSVM(kernel="rbf", nu=contamination, gamma="scale")
    ocsvm_scores = minmax_scale(-ocsvm.fit(X_scaled).decision_function(X_scaled))

    elliptic = EllipticEnvelope(
        contamination=contamination, support_fraction=0.8, random_state=random_state
    )
    elliptic_scores = minmax_scale(-elliptic.fit(X_scaled).score_samples(X_scaled))

    lof = LocalOutlierFactor(
        n_neighbors=5, contamination=contamination, novelty=True
    ).fit(X_scaled)
    lof_scores = minmax_scale(-lof.decision_function(X_scaled))

    score_table = pd.DataFrame(
        {
            "isolation_forest": iso_scores,
            "one_class_svm": ocsvm_scores,
            "elliptic_envelope": elliptic_scores,
            "local_outlier_factor": lof_scores,
        },
        index=df.index,
    )
    score_table["ensemble_score"] = score_table.mean(axis=1)

    threshold = score_table["ensemble_score"].quantile(0.75)
    score_table["is_anomaly"] = score_table["ensemble_score"] >= threshold
    anomalies = score_table.index[score_table["is_anomaly"]].tolist()

    return score_table.sort_values("ensemble_score", ascending=False), anomalies


def _build_color_map(labels: List[str], anomalies: List[str]) -> dict:
    base_colors = plt.cm.viridis(np.linspace(0.1, 0.85, len(labels)))
    color_map = {label: base_colors[idx] for idx, label in enumerate(labels)}
    for label in anomalies:
        color_map[label] = "#ff4d6d"
    return color_map


def _format_tick_labels(ax, anomalies: List[str]) -> None:
    """Color y-axis labels inside the heatmap to highlight anomalies."""
    for tick in ax.get_yticklabels():
        tick.set_color("#ff4d6d" if tick.get_text() in anomalies else "#112A46")
        tick.set_fontweight("bold" if tick.get_text() in anomalies else "normal")


def _radar_profiles(
    df: pd.DataFrame, anomalies: List[str]
) -> Tuple[List[float], List[float]]:
    """Normalize monthly profiles and return anomaly vs normal averages."""
    normed = (df - df.min()) / (df.max() - df.min())
    if anomalies:
        anomaly_profile = normed.loc[anomalies].mean(axis=0)
        normal_pool = normed.drop(index=anomalies)
        if normal_pool.empty:
            normal_pool = normed
        normal_profile = normal_pool.mean(axis=0)
    else:
        anomaly_profile = normed.mean(axis=0)
        normal_profile = normed.mean(axis=0)

    anomaly_values = anomaly_profile.tolist()
    normal_values = normal_profile.tolist()
    anomaly_values.append(anomaly_values[0])
    normal_values.append(normal_values[0])
    return anomaly_values, normal_values


def plot_dashboard(
    df: pd.DataFrame, score_table: pd.DataFrame, anomalies: List[str]
) -> None:
    """Render a four-panel dashboard with stylized anomaly-focused plots."""
    if "ensemble_score" not in score_table.columns:
        raise ValueError("`score_table` must contain an `ensemble_score` column.")

    color_map = _build_color_map(df.index.tolist(), anomalies)
    months = df.columns.tolist()

    fig = plt.figure(figsize=(18, 12))
    grid = GridSpec(2, 2, height_ratios=[1, 1.05], figure=fig, hspace=0.25, wspace=0.18)

    # 1) Trend lines per object
    ax1 = fig.add_subplot(grid[0, 0])
    for label, values in df.iterrows():
        is_anomaly = label in anomalies
        ax1.plot(
            months,
            values.values,
            color=color_map[label],
            linewidth=2.8 if is_anomaly else 1.5,
            alpha=0.95 if is_anomaly else 0.45,
            marker="o" if is_anomaly else None,
            label=label if is_anomaly else None,
        )
    ax1.set_title("Помесячные профили (аномалии — яркие линии)")
    ax1.set_ylabel("Значение")
    if anomalies:
        ax1.legend(loc="upper left", frameon=False)

    # 2) Heatmap of monthly distribution
    ax2 = fig.add_subplot(grid[0, 1])
    heatmap_cmap = "viridis"
    if sns:
        sns.heatmap(
            df,
            cmap=heatmap_cmap,
            annot=False,
            cbar=True,
            linewidths=0.5,
            linecolor="white",
            ax=ax2,
        )
    else:
        mesh = ax2.imshow(df.values, aspect="auto", cmap=heatmap_cmap)
        fig.colorbar(mesh, ax=ax2, fraction=0.046, pad=0.04)
        ax2.set_xticks(range(len(months)))
        ax2.set_xticklabels(months)
        ax2.set_yticks(range(len(df.index)))
        ax2.set_yticklabels(df.index)
    ax2.set_title("Тепловая карта значений")
    _format_tick_labels(ax2, anomalies)

    # 3) Ensemble scores as stylized bar chart
    ax3 = fig.add_subplot(grid[1, 0])
    score_sorted = score_table.sort_values("ensemble_score")
    colors = [
        color_map[label] if label in anomalies else "#1f77b4"
        for label in score_sorted.index
    ]
    bars = ax3.barh(
        score_sorted.index,
        score_sorted["ensemble_score"],
        color=colors,
        alpha=0.9,
        edgecolor="white",
    )
    ax3.set_title("Ансамблевый скор аномалий")
    ax3.set_xlabel("Сила сигнала")
    for bar in bars:
        width = bar.get_width()
        ax3.text(width + 0.01, bar.get_y() + bar.get_height() / 2, f"{width:.2f}", va="center")

    # 4) Radar chart comparing anomaly vs normal profile
    ax4 = fig.add_subplot(grid[1, 1], polar=True)
    anomaly_values, normal_values = _radar_profiles(df, anomalies)
    angles = np.linspace(0, 2 * np.pi, len(months), endpoint=False).tolist()
    angles.append(angles[0])
    ax4.plot(angles, normal_values, color="#38618c", linewidth=2, label="Нормальное поведение")
    ax4.fill(angles, normal_values, color="#93b7be", alpha=0.25)
    ax4.plot(angles, anomaly_values, color="#ff4d6d", linewidth=3, label="Аномалии")
    ax4.fill(angles, anomaly_values, color="#ff4d6d", alpha=0.25)
    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels(months)
    ax4.set_title("Полярный профиль средних значений")
    ax4.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    fig.suptitle("Разносторонняя визуализация аномалий", fontsize=20, weight="bold")
    plt.show()


def render_dashboard(
    df: Optional[pd.DataFrame] = None,
    *,
    X: Optional[np.ndarray] = None,
    labels: Optional[List[str]] = None,
    months: Optional[List[str]] = None,
    score_table: Optional[pd.DataFrame] = None,
    anomalies: Optional[List[str]] = None,
    contamination: float = 0.2,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Unified entry-point used by both CLI and notebooks.

    Returns the dataframe, score table, and final list of anomaly labels.
    """

    if df is None:
        if X is not None:
            df = dataframe_from_matrix(X, labels=labels, months=months)
        else:
            df = load_dataset()

    if score_table is None:
        score_table, detected = detect_anomalies(
            df, contamination=contamination, random_state=random_state
        )
    else:
        detected = (
            score_table.index[score_table["is_anomaly"]].tolist()
            if "is_anomaly" in score_table.columns
            else []
        )

    final_anomalies = anomalies or detected
    plot_dashboard(df, score_table, final_anomalies)

    return df, score_table, final_anomalies


def main() -> None:
    render_dashboard()


if __name__ == "__main__":
    main()
