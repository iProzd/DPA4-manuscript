"""
Draw the cumulative ablation of the DPA4 architectural components.

The left matrix states which components each configuration retains: a filled marker
denotes a component that is present and an open marker one that has been removed.
Reading downwards, one further component is switched off at every row, so each row
accumulates the removals above it. The three bar panels give the resulting test error
and inference time relative to the complete architecture. Each segment is the
increment contributed by one removal, normalized by the complete-architecture value,
so the segments sum to the cumulative label at every rung.

Segment colours follow the sequential ``Blues`` ramp of the inference-throughput
figure, ordered so that later removals appear darker.

Usage
-----
python scripts/plot_ablation_ladder.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

GRID_COLOR = "#bdbdbd"
ZERO_COLOR = "#3f3f3f"
PRESENT_COLOR = "#3f3f3f"
ABSENT_COLOR = "#ffffff"
BAR_HEIGHT = 0.56


@dataclass(frozen=True)
class Rung:
    """One configuration of the cumulative ablation."""

    removed: str
    short: str
    energy_mae: float
    force_mae: float
    test_seconds: float


# Ordered from the complete architecture downwards; `removed` names the component
# switched off at that row, on top of every removal above it. Accuracy metrics are
# the t-1 entries in section 2.2 of X.0 Ablation.ipynb; inference times are the
# corresponding three-checkpoint averages.
LADDER = (
    Rung("", "", 31.00681, 39.16882, 20.2),
    Rung("Message node WBN", "MN", 31.58496, 38.95662, 19.8),
    Rung("WBN in FFN", "WBN", 33.22586, 39.91841, 18.7),
    Rung("Low-rank edge\u2013node product", "EC", 34.52942, 42.00412, 18.1),
    Rung("Envelope-gated attention", "Attn", 39.67069, 44.58118, 17.7),
)

PANELS = (
    ("energy_mae", "Change in per-atom\nenergy MAE (%)", (-2.2, 34.0), (0, 10, 20, 30)),
    ("force_mae", "Change in\nforce MAE (%)", (-2.2, 18.0), (0, 5, 10, 15)),
    ("test_seconds", "Change in\ninference time (%)", (-15.6, 2.6), (-15, -10, -5, 0)),
)


def segment_palette() -> list[tuple[float, float, float]]:
    """
    Build the colour ramp used for the removal segments.

    Returns
    -------
    list[tuple[float, float, float]]
        One colour per removal step, following the convention of the
        inference-throughput figure.
    """
    n_steps = len(LADDER) - 1
    return sns.color_palette("Blues", n_steps + 4)[3:-1]


def cumulative_change(field: str) -> list[float]:
    """
    Calculate the cumulative change from the complete architecture.

    Parameters
    ----------
    field : str
        Attribute of :class:`Rung` holding the metric.

    Returns
    -------
    list[float]
        Relative change of every configuration from the complete architecture,
        in percent.
    """
    values = [getattr(rung, field) for rung in LADDER]
    return [100 * (value / values[0] - 1) for value in values]


def style_row_axis(ax: plt.Axes) -> None:
    """
    Apply the shared row geometry to one panel.

    Parameters
    ----------
    ax : plt.Axes
        Target axes.
    """
    ax.set_ylim(len(LADDER) - 0.45, -0.55)
    ax.set_yticks(range(len(LADDER)))
    ax.tick_params(axis="y", length=0)


def draw_matrix(ax: plt.Axes) -> None:
    """
    Draw the presence matrix of the ablated components.

    Parameters
    ----------
    ax : plt.Axes
        Target axes.
    """
    n_steps = len(LADDER) - 1
    for column in range(n_steps):
        ax.plot([column, column], [-0.2, len(LADDER) - 0.8], color="#e8e8e8",
                linewidth=1.0, zorder=1)

    # Row `i` has switched off the components of columns 0 to i-1.
    for row in range(len(LADDER)):
        if row < n_steps - 1:
            ax.plot([row, n_steps - 1], [row, row], color=PRESENT_COLOR,
                    linewidth=1.1, zorder=2)
        for column in range(n_steps):
            present = column >= row
            ax.plot(column, row, marker="o", markersize=7.2,
                    markerfacecolor=PRESENT_COLOR if present else ABSENT_COLOR,
                    markeredgecolor=PRESENT_COLOR if present else "#c0c0c0",
                    markeredgewidth=1.0, zorder=3)

    ax.set_xlim(-0.55, n_steps - 0.45)
    ax.set_xticks(range(n_steps))
    ax.set_xticklabels([rung.short for rung in LADDER[1:]], fontsize=9.2)
    ax.xaxis.set_ticks_position("top")
    ax.tick_params(axis="x", length=0, pad=3)
    style_row_axis(ax)
    ax.set_yticklabels([])
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)


def draw_panel(
    ax: plt.Axes,
    field: str,
    xlabel: str,
    xlim: tuple[float, float],
    xticks: tuple[int, ...],
    colors: list[tuple[float, float, float]],
) -> None:
    """
    Draw one metric panel as a stack that grows with every removal.

    Parameters
    ----------
    ax : plt.Axes
        Target axes.
    field : str
        Attribute of :class:`Rung` holding the metric.
    xlabel : str
        Axis label.
    xlim : tuple[float, float]
        Horizontal limits, sized to leave room for the running totals.
    xticks : tuple[int, ...]
        Tick positions in percent.
    colors : list[tuple[float, float, float]]
        One colour per removal step.
    """
    cumulative = cumulative_change(field)
    span = xlim[1] - xlim[0]

    for row, total in enumerate(cumulative):
        for step in range(row):
            ax.barh(row, cumulative[step + 1] - cumulative[step],
                    left=cumulative[step], height=BAR_HEIGHT, color=colors[step],
                    edgecolor="white", linewidth=0.6, zorder=2)
        if row == 0:
            if field == PANELS[0][0]:
                ax.text(0.016 * span, row, "reference", va="center", ha="left",
                        fontsize=8.8, color="#6E6E6E", style="italic", zorder=3)
            continue
        pad = 0.014 * span * (1 if total >= 0 else -1)
        ax.text(total + pad, row, f"{total:+.1f}", va="center",
                ha="left" if total >= 0 else "right", fontsize=9.2, color="#2B2B2B",
                fontweight="bold" if row == len(cumulative) - 1 else "normal", zorder=3)

    ax.axvline(0, color=ZERO_COLOR, linewidth=1.0, zorder=4)
    ax.set_xlim(*xlim)
    ax.set_xticks(list(xticks))
    ax.set_xlabel(xlabel, fontsize=10.2, labelpad=5)
    ax.tick_params(axis="x", labelsize=9.5, length=3.5, width=0.9)
    ax.grid(axis="x", color=GRID_COLOR, linestyle="--", linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    style_row_axis(ax)
    ax.set_yticklabels([])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_linewidth(0.9)


def main() -> None:
    """Render the ablation figure into the manuscript figure directory."""
    mpl.rcParams["font.family"] = "Times New Roman"
    mpl.rcParams["font.serif"] = ["Times New Roman"]
    mpl.rcParams["mathtext.fontset"] = "custom"
    mpl.rcParams["mathtext.rm"] = "Times New Roman"

    colors = segment_palette()
    fig, axes = plt.subplots(
        1, 4, figsize=(7.7, 2.5), sharey=True,
        gridspec_kw={"width_ratios": [0.86, 1.14, 1.14, 1.14], "wspace": 0.17},
    )
    draw_matrix(axes[0])
    for ax, panel in zip(axes[1:], PANELS):
        draw_panel(ax, *panel, colors)

    for ax, tag in zip(axes[1:], ("a", "b", "c")):
        ax.set_title(tag, loc="left", fontsize=12, fontweight="bold", pad=4)

    fig.subplots_adjust(left=0.02, right=0.99, bottom=0.19, top=0.84)
    output_path = Path(__file__).resolve().parents[1] / "fig" / "ablation_ladder.pdf"
    fig.savefig(output_path, bbox_inches="tight")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
