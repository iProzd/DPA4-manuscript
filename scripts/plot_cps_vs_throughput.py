"""Plot Matbench Discovery CPS against saturated inference throughput."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pareto_plot_style import (
    ANNOTATION_FONT_SIZE,
    DPA4_COLOR,
    DPA4_COLORS,
    PARETO_LINE_STYLE,
    PARETO_LINE_WIDTH,
    apply_publication_style,
    create_broken_axis_figure,
    draw_axis_break,
    draw_param_scale,
    draw_pareto_legend,
    draw_ratio_arrow,
    finalize_figure,
    marker_size,
    style_log_axis,
)

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
DATA_DIR: Final = REPO_ROOT / "data" / "saturated_throughput"
OUTPUT_PDF: Final = REPO_ROOT / "fig" / "cps-throughput-pareto.pdf"

CSV_COLUMNS: Final = (
    "model",
    "system",
    "target_natoms",
    "n_atoms",
    "n_frames",
    "success_rate",
    "mean_s",
    "us_per_atom",
    "atoms_per_ms",
)


@dataclass(frozen=True)
class ModelSpec:
    """Describe one compliant model included in the Pareto comparison.

    Parameters
    ----------
    label : str
        Display label matching the Matbench Discovery table.
    csv_name : str
        Raw throughput CSV filename.
    cps : float
        Matbench Discovery combined performance score.
    params_m : float
        Number of model parameters in millions.
    color : str
        Matplotlib-compatible point colour.
    annotation_offset : tuple of int
        Label offset in points as ``(x, y)``.
    """

    label: str
    csv_name: str
    cps: float
    params_m: float
    color: str
    annotation_offset: tuple[int, int]


MODELS: Final = (
    ModelSpec("DPA4-Pro", "DPA4-Pro.csv", 0.842, 25.211, DPA4_COLORS["Pro"], (0, 11)),
    ModelSpec("DPA4-Plus", "DPA4-Plus.csv", 0.829, 8.796, DPA4_COLORS["Plus"], (0, 16)),
    ModelSpec("DPA4-Air", "DPA4-Air.csv", 0.816, 5.148, DPA4_COLORS["Air"], (0, 14)),
    ModelSpec("DPA4-Neo", "DPA4-Neo.csv", 0.782, 1.125, DPA4_COLORS["Neo"], (0, 22)),
    ModelSpec("DPA4-Mini", "DPA4-Mini.csv", 0.733, 0.660, DPA4_COLORS["Mini"], (0, 34)),
    ModelSpec(
        "EquiformerV3+DeNS-MP",
        "EquiformerV3+DeNS-MP.csv",
        0.830,
        30.3,
        "#3F3F3F",
        (-10, -8),
    ),
    ModelSpec("MatRIS-10M-MP", "MatRIS-10M-MP.csv", 0.778, 10.4, "#8C613C", (8, -2)),
    ModelSpec("Nequip-MP-L", "Nequip-MP-L.csv", 0.730, 9.6, "#4C78A8", (8, 5)),
    ModelSpec("Allegro-MP-L", "Allegro-MP-L.csv", 0.720, 18.7, "#72B7B2", (-8, 10)),
    ModelSpec("Nequix MP PFT", "Nequix-MP-PFT.csv", 0.755, 0.708, "#3C8DAB", (-8, 9)),
    ModelSpec(
        "DPA-3.1-MPtrj",
        "DPA-3.1-MPtrj.csv",
        0.718,
        4.81,
        "#2B7BBA",
        (-8, -12),
    ),
    ModelSpec("SevenNet-l3i5", "SevenNet-l3i5.csv", 0.714, 1.17, "#D5A928", (-10, -8)),
    ModelSpec("MACE-MP-0", "MACE-MP-0.csv", 0.637, 4.69, "#41A45C", (-10, -8)),
    ModelSpec("ORB v2 MPtrj", "ORB-v2-MPtrj.csv", 0.470, 25.2, "#956CB4", (-8, -12)),
    ModelSpec("CHGNet", "CHGNet.csv", 0.400, 0.413, "#EE854A", (8, 6)),
)


def _validated_successful_measurements(
    frame: pd.DataFrame, path: Path
) -> tuple[pd.DataFrame, int | None]:
    """Validate one benchmark table and return its successful measurements."""
    if tuple(frame.columns) != CSV_COLUMNS:
        raise ValueError(
            f"{path.name} columns differ from the nine-column benchmark schema: "
            f"{frame.columns.tolist()}"
        )
    if frame.empty:
        raise ValueError(f"{path.name} contains no benchmark measurements")
    if frame["model"].nunique() != 1:
        raise ValueError(f"{path.name} contains more than one model label")
    if not frame["system"].eq("diamond").all():
        raise ValueError(f"{path.name} contains a non-diamond benchmark system")

    targets = pd.to_numeric(frame["target_natoms"], errors="coerce")
    atom_counts = pd.to_numeric(frame["n_atoms"], errors="coerce")
    frame_counts = pd.to_numeric(frame["n_frames"], errors="coerce")
    if targets.isna().any() or (targets <= 0).any() or targets.duplicated().any():
        raise ValueError(f"{path.name} has invalid or repeated target atom counts")
    if atom_counts.isna().any() or (atom_counts <= 0).any():
        raise ValueError(f"{path.name} has invalid realized atom counts")
    if (
        frame_counts.isna().any()
        or (frame_counts <= 0).any()
        or frame_counts.nunique() != 1
    ):
        raise ValueError(f"{path.name} has inconsistent timed-evaluation counts")

    success_rates = pd.to_numeric(frame["success_rate"], errors="coerce").to_numpy()
    success = np.isclose(success_rates, 100.0)
    failed = np.isclose(success_rates, 0.0)
    if not np.all(success | failed):
        raise ValueError(f"{path.name} has a partial or invalid success rate")
    failure_indices = np.flatnonzero(~success)
    successful = frame.loc[success].copy()
    if successful.empty:
        raise ValueError(f"{path.name} has no successful measurements")

    for column in ("mean_s", "us_per_atom", "atoms_per_ms"):
        values = pd.to_numeric(frame[column], errors="coerce")
        successful_values = values.loc[success]
        if not np.isfinite(successful_values).all() or not (
            successful_values > 0
        ).all():
            raise ValueError(f"{path.name} has invalid successful {column} values")
        if values.loc[failed].notna().any():
            raise ValueError(f"{path.name} has finite {column} values for an OOM trial")
        successful[column] = successful_values

    first_failed_target = (
        int(targets.iloc[int(failure_indices[0])])
        if len(failure_indices)
        else None
    )
    return successful, first_failed_target


def build_summary(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """Build and validate the CPS--throughput summary table.

    Saturated throughput is defined as the largest mean throughput among all
    successful measured target sizes. Failed OOM trials are excluded.

    Parameters
    ----------
    data_dir : pathlib.Path, optional
        Directory containing the raw per-model CSV files.

    Returns
    -------
    pandas.DataFrame
        One row per model with CPS, saturated throughput and peak system size.

    Raises
    ------
    FileNotFoundError
        If an expected raw CSV is missing.
    ValueError
        If a CSV violates the benchmark-table invariants.
    """
    records: list[dict[str, object]] = []
    for model in MODELS:
        path = data_dir / model.csv_name
        if not path.is_file():
            raise FileNotFoundError(f"missing benchmark CSV: {path}")
        successful, first_failed_target = _validated_successful_measurements(
            pd.read_csv(path), path
        )
        peak = successful.loc[successful["atoms_per_ms"].idxmax()]
        largest = successful.loc[successful["n_atoms"].idxmax()]
        records.append(
            {
                "model": model.label,
                "cps": model.cps,
                "saturated_throughput_atoms_per_ms": float(peak["atoms_per_ms"]),
                "peak_target_natoms": int(peak["target_natoms"]),
                "peak_n_atoms": int(peak["n_atoms"]),
                "largest_success_target_natoms": int(largest["target_natoms"]),
                "largest_success_n_atoms": int(largest["n_atoms"]),
                "first_failed_target_natoms": first_failed_target,
                "source_csv": model.csv_name,
            }
        )
    return pd.DataFrame.from_records(records)


def pareto_front(summary: pd.DataFrame) -> pd.DataFrame:
    """Return non-dominated models when both CPS and throughput are maximized.

    Parameters
    ----------
    summary : pandas.DataFrame
        Table returned by :func:`build_summary`.

    Returns
    -------
    pandas.DataFrame
        Non-dominated rows sorted by increasing throughput.
    """
    throughput = summary["saturated_throughput_atoms_per_ms"].to_numpy(float)
    cps = summary["cps"].to_numpy(float)
    is_front = np.ones(len(summary), dtype=bool)
    for index in range(len(summary)):
        weakly_better = (throughput >= throughput[index]) & (cps >= cps[index])
        strictly_better = (throughput > throughput[index]) | (cps > cps[index])
        is_front[index] = not np.any(weakly_better & strictly_better)
    return summary.loc[is_front].sort_values("saturated_throughput_atoms_per_ms")


def plot_summary(summary: pd.DataFrame) -> tuple[Figure, tuple[Axes, Axes]]:
    """Draw model points and the higher-is-better Pareto frontier.

    Parameters
    ----------
    summary : pandas.DataFrame
        Table returned by :func:`build_summary`.

    Returns
    -------
    matplotlib.figure.Figure
        Created figure.
    tuple of matplotlib.axes.Axes
        Top and bottom axes forming the broken CPS scale.
    """
    apply_publication_style()
    figure, (ax_top, ax_bottom) = create_broken_axis_figure()
    for ax in (ax_top, ax_bottom):
        style_log_axis(
            ax,
            x_limits=(0.04, 150),
            ticks=(0.05, 0.1, 0.3, 1, 3, 10, 30, 100),
            tick_labels=("0.05", "0.1", "0.3", "1", "3", "10", "30", "100"),
        )
    ax_top.set_ylim(0.695, 0.865)
    ax_top.set_yticks([0.70, 0.72, 0.74, 0.76, 0.78, 0.80, 0.82, 0.84, 0.86])
    ax_bottom.set_ylim(0.38, 0.66)
    ax_bottom.set_yticks([0.40, 0.50, 0.60, 0.65])
    draw_axis_break(ax_top, ax_bottom)

    frontier = pareto_front(summary)
    ax_top.plot(
        frontier["saturated_throughput_atoms_per_ms"],
        frontier["cps"],
        color=DPA4_COLOR,
        linewidth=PARETO_LINE_WIDTH,
        linestyle=PARETO_LINE_STYLE,
        alpha=0.88,
        zorder=2,
    )

    indexed = summary.set_index("model")
    equiformer = indexed.loc["EquiformerV3+DeNS-MP"]
    dpa4_plus = indexed.loc["DPA4-Plus"]
    equiformer_throughput = float(equiformer["saturated_throughput_atoms_per_ms"])
    dpa4_plus_throughput = float(dpa4_plus["saturated_throughput_atoms_per_ms"])
    draw_ratio_arrow(
        ax_top,
        source_x=equiformer_throughput,
        target_x=dpa4_plus_throughput,
        y=float(equiformer["cps"]),
        ratio=dpa4_plus_throughput / equiformer_throughput,
        label_x=1.15,
        shrink_source=15,
        shrink_target=11,
    )

    for model in MODELS:
        row = indexed.loc[model.label]
        is_dpa4 = model.label.startswith("DPA4-")
        cps = float(row["cps"])
        if cps >= 0.69:
            ax = ax_top
        elif cps <= 0.66:
            ax = ax_bottom
        else:
            raise ValueError(f"{model.label} falls inside the omitted CPS interval")
        ax.scatter(
            row["saturated_throughput_atoms_per_ms"],
            cps,
            s=marker_size(model.params_m),
            marker="o",
            color=model.color,
            edgecolor="black",
            linewidth=0.7 if is_dpa4 else 0.5,
            linestyles="solid",
            zorder=5 if is_dpa4 else 4,
        )
        ax.annotate(
            model.label,
            (row["saturated_throughput_atoms_per_ms"], cps),
            xytext=model.annotation_offset,
            textcoords="offset points",
            ha=(
                "center"
                if model.annotation_offset[0] == 0
                else "left"
                if model.annotation_offset[0] > 0
                else "right"
            ),
            va="bottom" if model.annotation_offset[1] >= 0 else "top",
            fontsize=ANNOTATION_FONT_SIZE,
            color=DPA4_COLOR if is_dpa4 else "#303030",
            fontweight="bold" if is_dpa4 else "normal",
            arrowprops={
                "arrowstyle": "-",
                "color": model.color,
                "linewidth": 0.65,
                "alpha": 0.8,
                "shrinkA": 1.5,
                "shrinkB": max(4.5, 0.55 * marker_size(model.params_m) ** 0.5),
            },
            zorder=6,
        )

    param_box_x = 0.018
    param_box_y = 0.06
    param_box_w = 0.14
    param_box_h = 0.78
    draw_param_scale(
        ax_bottom,
        box_x=param_box_x,
        box_y=param_box_y,
        box_w=param_box_w,
        box_h=param_box_h,
    )
    draw_pareto_legend(
        ax_bottom,
        anchor_x=param_box_x + param_box_w + 0.03,
        anchor_y=param_box_y + param_box_h / 2,
    )
    finalize_figure(figure, ax_bottom, "Saturated inference throughput (atoms/ms)")
    return figure, (ax_top, ax_bottom)


def main() -> None:
    """Validate raw data and render the Pareto figure as PDF."""
    summary = build_summary()
    figure, _ = plot_summary(summary)
    figure.savefig(OUTPUT_PDF)
    plt.close(figure)


if __name__ == "__main__":
    main()
