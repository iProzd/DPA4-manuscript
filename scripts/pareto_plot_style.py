"""Shared publication style for the Matbench Discovery Pareto figures."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import NullFormatter


FIGURE_SIZE: Final = (7.3, 5.05)
FIGURE_DPI: Final = 300
BASE_FONT_SIZE: Final = 12.0
AXIS_LABEL_SIZE: Final = 13.0
TICK_LABEL_SIZE: Final = 11.2
ANNOTATION_FONT_SIZE: Final = 10.5
PARAM_SIZE_SCALE: Final = 16.0
PARETO_LINE_WIDTH: Final = 1.6
PARETO_LINE_STYLE: Final = (0, (4, 2))
RATIO_ARROW_COLOR: Final = "#6E6E6E"
RATIO_ARROW_FONT_SIZE: Final = 10.5

DPA4_COLOR: Final = "#C91D13"
DPA4_COLORS: Final = {
    "Mini": "#FDB27B",
    "Neo": "#FC8C59",
    "Air": "#F26D4B",
    "Plus": "#E0442F",
    "Pro": DPA4_COLOR,
}


def apply_publication_style() -> None:
    """Set the typography shared by both Pareto figures."""
    mpl.rcParams.update(
        {
            "font.family": "Times New Roman",
            "font.serif": ["Times New Roman"],
            "font.size": BASE_FONT_SIZE,
            "axes.labelsize": AXIS_LABEL_SIZE,
            "xtick.labelsize": TICK_LABEL_SIZE,
            "ytick.labelsize": TICK_LABEL_SIZE,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def create_broken_axis_figure() -> tuple[Figure, tuple[Axes, Axes]]:
    """Create the common two-panel canvas used for a broken CPS axis.

    Returns
    -------
    matplotlib.figure.Figure
        Figure with the shared publication dimensions.
    tuple of matplotlib.axes.Axes
        Upper and lower axes that share the horizontal scale.
    """
    figure, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=FIGURE_SIZE,
        dpi=FIGURE_DPI,
        gridspec_kw={"height_ratios": (2.0, 1.0), "hspace": 0.04},
    )
    return figure, (ax_top, ax_bottom)


def style_log_axis(
    ax: Axes,
    x_limits: tuple[float, float],
    ticks: Sequence[float],
    tick_labels: Sequence[str],
) -> None:
    """Apply the shared log-axis, grid and spine style.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis to style.
    x_limits : tuple of float
        Lower and upper horizontal limits.
    ticks : sequence of float
        Major tick positions.
    tick_labels : sequence of str
        Text shown at the major tick positions.

    Raises
    ------
    ValueError
        If the tick positions and labels have different lengths.
    """
    if len(ticks) != len(tick_labels):
        raise ValueError("ticks and tick_labels must have equal lengths")

    ax.set_xscale("log")
    ax.set_xlim(*x_limits)
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels)
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.grid(
        True,
        which="major",
        color="#D2D2D2",
        linestyle="--",
        linewidth=0.55,
    )
    ax.grid(False, which="minor")
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)
    ax.tick_params(
        axis="both",
        which="major",
        width=1.0,
        length=4,
        direction="in",
    )
    ax.tick_params(
        axis="both",
        which="minor",
        width=0.7,
        length=2.5,
        direction="in",
    )


def draw_axis_break(ax_top: Axes, ax_bottom: Axes) -> None:
    """Draw matching break marks between the upper and lower CPS panels.

    Parameters
    ----------
    ax_top : matplotlib.axes.Axes
        Upper CPS panel.
    ax_bottom : matplotlib.axes.Axes
        Lower CPS panel.
    """
    ax_top.spines["bottom"].set_visible(False)
    ax_bottom.spines["top"].set_visible(False)
    ax_top.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    ax_bottom.tick_params(axis="x", which="both", top=False)

    diagonal = 0.008
    line_style = {"color": "black", "clip_on": False, "linewidth": 1.0}
    ax_top.plot(
        (-diagonal, diagonal),
        (-diagonal, diagonal),
        transform=ax_top.transAxes,
        **line_style,
    )
    ax_top.plot(
        (1 - diagonal, 1 + diagonal),
        (-diagonal, diagonal),
        transform=ax_top.transAxes,
        **line_style,
    )
    ax_bottom.plot(
        (-diagonal, diagonal),
        (1 - diagonal, 1 + diagonal),
        transform=ax_bottom.transAxes,
        **line_style,
    )
    ax_bottom.plot(
        (1 - diagonal, 1 + diagonal),
        (1 - diagonal, 1 + diagonal),
        transform=ax_bottom.transAxes,
        **line_style,
    )


def marker_size(params_m: float) -> float:
    """Convert a parameter count to marker area.

    Parameters
    ----------
    params_m : float
        Number of model parameters in millions.

    Returns
    -------
    float
        Matplotlib scatter area in points squared.

    Raises
    ------
    ValueError
        If the parameter count is not positive.
    """
    if params_m <= 0:
        raise ValueError("params_m must be positive")
    return params_m * PARAM_SIZE_SCALE


def draw_ratio_arrow(
    ax: Axes,
    source_x: float,
    target_x: float,
    y: float,
    ratio: float,
    label_x: float,
    shrink_source: float,
    shrink_target: float,
    label_y_offset: float = -0.004,
) -> None:
    """Draw a horizontal ratio arrow shared by the two Pareto figures.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis on which the arrow is drawn.
    source_x : float
        Horizontal coordinate of the baseline model.
    target_x : float
        Horizontal coordinate of the compared DPA4 model or frontier.
    y : float
        Vertical coordinate shared by the arrow endpoints.
    ratio : float
        Positive comparison ratio shown next to the arrow.
    label_x : float
        Horizontal coordinate of the ratio label.
    shrink_source : float
        Padding at the source end in points.
    shrink_target : float
        Padding at the arrowhead in points.
    label_y_offset : float, optional
        Vertical offset of the ratio label in CPS units.

    Raises
    ------
    ValueError
        If a log-axis coordinate or ratio is not positive, or if padding is
        negative.
    """
    if min(source_x, target_x, label_x) <= 0:
        raise ValueError("ratio-arrow x coordinates must be positive")
    if ratio <= 0:
        raise ValueError("ratio must be positive")
    if min(shrink_source, shrink_target) < 0:
        raise ValueError("ratio-arrow padding must be non-negative")

    ax.annotate(
        "",
        xy=(target_x, y),
        xytext=(source_x, y),
        arrowprops={
            "arrowstyle": "->",
            "color": RATIO_ARROW_COLOR,
            "linewidth": 1.0,
            "shrinkA": shrink_source,
            "shrinkB": shrink_target,
            "zorder": 1,
        },
        zorder=1,
    )
    ratio_label = f"{ratio:.0f}x" if ratio >= 20 else f"{ratio:.1f}x"
    ax.text(
        label_x,
        y + label_y_offset,
        ratio_label,
        fontsize=RATIO_ARROW_FONT_SIZE,
        color=RATIO_ARROW_COLOR,
        fontweight="bold",
        va="top",
        zorder=6,
    )


def draw_param_scale(
    ax: Axes,
    box_x: float,
    box_y: float,
    box_w: float,
    box_h: float,
) -> None:
    """Draw the common 1M/10M/25M marker-area scale.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis that owns the scale box.
    box_x, box_y : float
        Lower-left position in axis coordinates.
    box_w, box_h : float
        Width and height in axis coordinates.
    """
    frame = FancyBboxPatch(
        (box_x, box_y),
        box_w,
        box_h,
        transform=ax.transAxes,
        boxstyle="round,pad=0,rounding_size=0.004",
        facecolor="white",
        edgecolor="#BBBBBB",
        linewidth=1.0,
        alpha=0.95,
        zorder=8,
    )
    ax.add_patch(frame)
    ax.text(
        box_x + box_w / 2,
        box_y + box_h - 0.025,
        "Params",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=8.8,
        zorder=9,
    )

    entries = ((1.0, "1M", 0.73), (10.0, "10M", 0.48), (25.0, "25M", 0.22))
    for params_m, label, relative_y in entries:
        y_position = box_y + box_h * relative_y
        ax.scatter(
            [box_x + 0.032],
            [y_position],
            s=marker_size(params_m),
            transform=ax.transAxes,
            facecolors="none",
            edgecolors="#444444",
            linewidths=0.8,
            linestyles="solid",
            clip_on=False,
            zorder=9,
        )
        ax.text(
            box_x + 0.078,
            y_position,
            label,
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=8.4,
            zorder=9,
        )


def draw_pareto_legend(ax: Axes, anchor_x: float, anchor_y: float) -> None:
    """Place the Pareto-frontier key beside the parameter scale.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis that owns the legend.
    anchor_x, anchor_y : float
        Left-centre anchor of the legend in axis coordinates.

    Raises
    ------
    ValueError
        If the anchor lies outside the axis coordinate range.
    """
    if not 0 <= anchor_x <= 1 or not 0 <= anchor_y <= 1:
        raise ValueError("Pareto legend anchor must lie within the axis")

    handle = Line2D(
        [0],
        [0],
        color=DPA4_COLOR,
        linewidth=PARETO_LINE_WIDTH,
        linestyle=PARETO_LINE_STYLE,
        label="Pareto frontier",
    )
    legend = ax.legend(
        handles=[handle],
        loc="center left",
        bbox_to_anchor=(anchor_x, anchor_y),
        frameon=False,
        fontsize=10,
        handlelength=2.4,
        handletextpad=0.55,
        borderaxespad=0,
    )
    legend.set_zorder(10)


def finalize_figure(
    figure: Figure,
    ax_bottom: Axes,
    x_label: str,
    y_label: str = "Matbench Discovery CPS",
) -> None:
    """Apply shared labels and fixed page margins.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        Figure to finalize.
    ax_bottom : matplotlib.axes.Axes
        Lower panel that owns the horizontal label.
    x_label : str
        Horizontal-axis label.
    y_label : str, optional
        Vertical-axis label shared by both panels.
    """
    ax_bottom.set_xlabel(x_label, labelpad=7)
    figure.text(
        0.022,
        0.55,
        y_label,
        va="center",
        rotation="vertical",
        fontsize=AXIS_LABEL_SIZE,
    )
    figure.subplots_adjust(
        left=0.12,
        right=0.985,
        bottom=0.13,
        top=0.97,
        hspace=0.04,
    )
