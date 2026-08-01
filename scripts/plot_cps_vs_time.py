from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerBase
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.ticker import NullFormatter
import numpy as np

try:
    import seaborn as sns
except ImportError:
    sns = None


RMSD_BASELINE = 0.15
PARAM_SIZE_SCALE = 16

# DPA4 is drawn in the deep red that marks DPA4-Pro in the inference-throughput
# figure, keeping the family identity consistent across figures. The remaining
# families follow the same convention: DPA3 the Blues ramp, MACE the Greens ramp
# and the Equiformer family neutral grays. Other baselines take muted accents.
DPA4_COLOR = "#C91D13"
if sns is not None:
    MUTED = sns.color_palette("muted", 10).as_hex()
    def _family(name, index=5):
        return sns.color_palette(name, 8).as_hex()[index]
    DPA3_COLOR = _family("Blues")
    MACE_COLOR = _family("Greens")
else:
    MUTED = [
        "#4878D0", "#EE854A", "#6ACC64", "#D65F5F", "#956CB4",
        "#8C613C", "#DC7EC0", "#797979", "#D5BB67", "#82C6E2",
    ]
    DPA3_COLOR, MACE_COLOR = "#2b7bba", "#41a45c"

EQV3_COLOR = "#3f3f3f"
EQV2_COLOR = "#9a9a9a"
COLORS = {
    "orange": MUTED[1],
    "purple": MUTED[4],
    "brown": MUTED[5],
    "pink": MUTED[6],
    "yellow": MUTED[8],
    "cyan": MUTED[9],
}
MATRIS_COLOR = COLORS["brown"]
EXTRA_TRAINING_MODELS = {"eSEN-30M-MP", "EqV2 S DeNS", "EqV3+DeNS-MP"}


def calculate_cps(f1, ksrme, rmsd):
    f1_norm = np.clip(f1, 0, 1)
    ksrme_norm = np.clip(1 - ksrme / 2, 0, 1)
    rmsd_norm = np.clip(1 - rmsd / RMSD_BASELINE, 0, 1)
    return 0.5 * f1_norm + 0.4 * ksrme_norm + 0.1 * rmsd_norm


def marker_size(params_m):
    return params_m * PARAM_SIZE_SCALE


class DashedCircleLegend:
    def __init__(self, color, label, marker="o"):
        self.color = color
        self.marker = marker
        self._label = label

    def get_label(self):
        return self._label


class DashedCircleHandler(HandlerBase):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        radius = min(width, height) * 0.58
        circle = Circle(
            (xdescent + width / 2, ydescent + height / 2),
            radius,
            facecolor=orig_handle.color,
            edgecolor="black",
            linewidth=0.9,
            linestyle=(0, (2.2, 1.5)),
        )
        circle.set_transform(trans)
        return [circle]


def draw_param_scale(ax, box_x, box_y, box_w, box_h):
    frame = FancyBboxPatch(
        (box_x, box_y),
        box_w,
        box_h,
        transform=ax.transAxes,
        boxstyle="round,pad=0,rounding_size=0.004",
        facecolor="white",
        edgecolor="#bbbbbb",
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

    # Centers are not equally spaced: larger bubbles need more center distance
    # to keep the visible edge gaps balanced.
    entries = [(1, "1M", 0.73), (10, "10M", 0.48), (25, "25M", 0.22)]
    for params_m, label, rel_y in entries:
        y = box_y + box_h * rel_y
        ax.scatter(
            [box_x + 0.032],
            [y],
            s=marker_size(params_m),
            transform=ax.transAxes,
            facecolors="none",
            edgecolors="#444444",
            linewidths=0.8,
            clip_on=False,
            zorder=9,
        )
        ax.text(
            box_x + 0.078,
            y,
            label,
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=8.4,
            zorder=9,
        )


# x = A100 GPU-days, y = CPS score, params_m = model parameters in millions.
models = {
    "Nequix MP": dict(x=15, y=0.755, params_m=0.708, color=COLORS["cyan"], marker="o"),
    "eSEN-30M-MP": dict(x=335, y=0.797, params_m=30.1, color=COLORS["purple"], marker="o"),
    "EqV2 S DeNS": dict(x=228, y=0.522, params_m=31.2, color=EQV2_COLOR, marker="o"),
    "Eqnorm-MP": dict(x=83, y=0.756, params_m=1.31, color=COLORS["pink"], marker="o"),
    "MACE-MP-0": dict(x=108, y=0.637, params_m=4.69, color=MACE_COLOR, marker="o"),
    "HIENet": dict(x=120, y=0.707, params_m=7.51, color=COLORS["orange"], marker="o"),
    "SevenNet-l3i5": dict(x=381, y=0.714, params_m=1.17, color=COLORS["yellow"], marker="o"),
    "DPA3": dict(x=104, y=0.718, params_m=4.81, color=DPA3_COLOR, marker="o"),
    "EqV3+DeNS-MP": dict(x=157, y=0.830, params_m=30.3, color=EQV3_COLOR, marker="o"),
    "DPA4-neo": dict(x=8.6, y=0.782, params_m=1.125, color=DPA4_COLOR, marker="o"),
    "DPA4-air": dict(x=16, y=0.811, params_m=5.148, color=DPA4_COLOR, marker="o"),
    "DPA4-plus": dict(x=31, y=0.829, params_m=8.796, color=DPA4_COLOR, marker="o"),
    "DPA4-pro": dict(x=233, y=0.842, params_m=25.211, color=DPA4_COLOR, marker="o"),
}

matris = {
    "L": dict(x=224, y=0.778, params_m=10.4),
}


def style_axis(ax):
    ax.set_xscale("log")
    ax.set_xlim(7, 470)
    ax.set_xticks([10, 30, 60, 100, 200, 400])
    ax.set_xticklabels(["10", "30", "60", "100", "200", "400"])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.grid(True, which="major", linestyle="--", linewidth=0.6, color="#cccccc", alpha=0.7)
    ax.grid(True, which="minor", axis="x", linestyle=":", linewidth=0.35, color="#dddddd", alpha=0.45)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_linewidth(1.2)
    ax.tick_params(axis="both", width=1.1, length=4)


def plot_model_points(ax):
    for name, m in models.items():
        is_dpa4 = name.startswith("DPA4")
        uses_extra_training = name in EXTRA_TRAINING_MODELS
        ax.scatter(
            m["x"],
            m["y"],
            s=marker_size(m["params_m"]),
            c=m["color"],
            marker=m["marker"],
            edgecolors="black",
            linewidth=1.0 if uses_extra_training else 0.7 if is_dpa4 else 0.5,
            linestyles="--" if uses_extra_training else "solid",
            alpha=0.96,
            zorder=5 if is_dpa4 else 3,
        )

    for p in matris.values():
        ax.scatter(
            p["x"],
            p["y"],
            s=marker_size(p["params_m"]),
            c=MATRIS_COLOR,
            marker="o",
            edgecolors="black",
            linewidth=1.0,
            linestyles="--",
            alpha=0.94,
            zorder=4,
        )


def trend_cost_at_cps(cps, lower, upper):
    """
    Locate where the DPA4 trend line reaches a given CPS.

    The trend is drawn as a straight segment in the plotted coordinates, that is
    linear in log10 of the training cost, so the interpolation is performed there.

    Parameters
    ----------
    cps : float
        Combined performance score to match.
    lower, upper : str
        Keys of the two DPA4 variants bracketing the requested score.

    Returns
    -------
    float
        Training cost in A100 GPU-days at which the trend line attains ``cps``.
    """
    x0, y0 = models[lower]["x"], models[lower]["y"]
    x1, y1 = models[upper]["x"], models[upper]["y"]
    frac = (cps - y0) / (y1 - y0)
    return 10 ** (np.log10(x0) + frac * (np.log10(x1) - np.log10(x0)))


def draw_speedup_arrow(ax, source, target_x, label_x, shrink_target):
    """
    Draw a horizontal arrow from a baseline to the DPA4 frontier at equal CPS.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes.
    source : dict
        Entry of ``models`` from which the arrow starts.
    target_x : float
        Training cost at which the arrow ends, in A100 GPU-days.
    label_x : float
        Horizontal position of the speedup annotation.
    shrink_target : float
        Padding at the arrow head, in points.
    """
    y = source["y"]
    ax.annotate(
        "",
        xy=(target_x, y),
        xytext=(source["x"], y),
        arrowprops=dict(arrowstyle="->", color="#6E6E6E", lw=1.0,
                        shrinkA=15, shrinkB=shrink_target, zorder=1),
        zorder=1,
    )
    ax.text(
        label_x,
        y - 0.004,
        f"{source['x'] / target_x:.0f}x" if source["x"] / target_x >= 10
        else f"{source['x'] / target_x:.1f}x",
        fontsize=10.5,
        color="#6E6E6E",
        fontweight="bold",
        va="top",
        zorder=6,
    )


def draw_dpa4_trend(ax):
    dpa4_xy = [
        (models["DPA4-neo"]["x"], models["DPA4-neo"]["y"]),
        (models["DPA4-air"]["x"], models["DPA4-air"]["y"]),
        (models["DPA4-plus"]["x"], models["DPA4-plus"]["y"]),
        (models["DPA4-pro"]["x"], models["DPA4-pro"]["y"]),
    ]
    ax.plot(
        [p[0] for p in dpa4_xy],
        [p[1] for p in dpa4_xy],
        linestyle="--",
        color=DPA4_COLOR,
        linewidth=1.3,
        alpha=0.85,
        zorder=2,
    )


def draw_axis_break(ax_top, ax_bottom):
    ax_top.spines["bottom"].set_visible(False)
    ax_bottom.spines["top"].set_visible(False)
    ax_top.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    ax_bottom.tick_params(axis="x", which="both", top=False)

    d = 0.008
    kwargs = dict(color="black", clip_on=False, linewidth=1.0)
    ax_top.plot((-d, +d), (-d, +d), transform=ax_top.transAxes, **kwargs)
    ax_top.plot((1 - d, 1 + d), (-d, +d), transform=ax_top.transAxes, **kwargs)
    ax_bottom.plot((-d, +d), (1 - d, 1 + d), transform=ax_bottom.transAxes, **kwargs)
    ax_bottom.plot((1 - d, 1 + d), (1 - d, 1 + d), transform=ax_bottom.transAxes, **kwargs)


def main():
    mpl.rcParams["font.family"] = "Times New Roman"
    mpl.rcParams["font.serif"] = ["Times New Roman"]
    mpl.rcParams["font.size"] = 12

    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=(6.4, 5.05),
        gridspec_kw={"height_ratios": [1.05, 1.0], "hspace": 0.04},
    )

    for ax in (ax_top, ax_bottom):
        style_axis(ax)
        plot_model_points(ax)

    ax_top.set_ylim(0.748, 0.862)
    ax_top.set_yticks([0.76, 0.78, 0.80, 0.82, 0.84, 0.86])
    ax_bottom.set_ylim(0.50, 0.735)
    ax_bottom.set_yticks([0.50, 0.55, 0.60, 0.65, 0.70])
    draw_axis_break(ax_top, ax_bottom)
    draw_dpa4_trend(ax_top)

    ax_top.annotate(
        "Neo",
        xy=(models["DPA4-neo"]["x"], models["DPA4-neo"]["y"]),
        xytext=(4, -15),
        textcoords="offset points",
        fontsize=10.5,
        fontweight="bold",
        color=DPA4_COLOR,
    )
    ax_top.annotate(
        "Air",
        xy=(models["DPA4-air"]["x"], models["DPA4-air"]["y"]),
        xytext=(-17, 8),
        textcoords="offset points",
        fontsize=10.5,
        fontweight="bold",
        color=DPA4_COLOR,
    )
    ax_top.annotate(
        "Plus",
        xy=(models["DPA4-plus"]["x"], models["DPA4-plus"]["y"]),
        xytext=(-22, 10),
        textcoords="offset points",
        fontsize=10.5,
        fontweight="bold",
        color=DPA4_COLOR,
    )
    ax_top.annotate(
        "Pro",
        xy=(models["DPA4-pro"]["x"], models["DPA4-pro"]["y"]),
        xytext=(-22, 10),
        textcoords="offset points",
        fontsize=10.5,
        fontweight="bold",
        color=DPA4_COLOR,
    )

    draw_speedup_arrow(
        ax_top,
        source=models["EqV3+DeNS-MP"],
        target_x=models["DPA4-plus"]["x"],
        label_x=62,
        shrink_target=11,
    )
    draw_speedup_arrow(
        ax_top,
        source=models["eSEN-30M-MP"],
        target_x=trend_cost_at_cps(models["eSEN-30M-MP"]["y"], "DPA4-neo", "DPA4-air"),
        label_x=42,
        shrink_target=3,
    )

    legend_entries = [
        ("Nequix MP", models["Nequix MP"]),
        ("eSEN-30M-MP", models["eSEN-30M-MP"]),
        ("EqV2 S DeNS", models["EqV2 S DeNS"]),
        ("Eqnorm-MP", models["Eqnorm-MP"]),
        ("MatRIS", dict(color=MATRIS_COLOR, marker="o")),
        ("MACE-MP-0", models["MACE-MP-0"]),
        ("HIENet", models["HIENet"]),
        ("SevenNet-l3i5", models["SevenNet-l3i5"]),
        ("DPA3", models["DPA3"]),
        ("EqV3+DeNS-MP", models["EqV3+DeNS-MP"]),
        ("DPA4", dict(color=DPA4_COLOR, marker="o")),
    ]

    handles = []
    for name, entry in legend_entries:
        if name in EXTRA_TRAINING_MODELS or name == "MatRIS":
            handles.append(DashedCircleLegend(entry["color"], name, entry["marker"]))
        else:
            handles.append(
                plt.Line2D(
                    [0],
                    [0],
                    marker=entry["marker"],
                    linestyle="None",
                    markersize=7.5,
                    markerfacecolor=entry["color"],
                    markeredgecolor="black",
                    markeredgewidth=0.5,
                    label=name,
                )
            )

    leg = ax_bottom.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.02, 0.005),
        ncol=2,
        fontsize=8.4,
        frameon=True,
        framealpha=0.95,
        handletextpad=0.45,
        columnspacing=0.75,
        borderpad=0.55,
        handler_map={DashedCircleLegend: DashedCircleHandler()},
    )
    leg.get_frame().set_edgecolor("#bbbbbb")
    ax_bottom.add_artist(leg)

    fig.canvas.draw()
    legend_bbox = leg.get_frame().get_window_extent(fig.canvas.get_renderer()).transformed(
        ax_bottom.transAxes.inverted()
    )
    draw_param_scale(
        ax_bottom,
        legend_bbox.x1 - 0.032,
        legend_bbox.y0,
        0.135,
        legend_bbox.height * 0.90,
    )

    ax_bottom.set_xlabel("Training cost (A100 GPU-days)", fontsize=14, labelpad=8)
    fig.text(0.028, 0.54, "CPS score (higher is better)", va="center", rotation="vertical", fontsize=14)

    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.13, top=0.96, hspace=0.04)
    output_path = Path(__file__).resolve().parents[1] / "fig" / "fig1_CPS.pdf"
    plt.savefig(output_path, bbox_inches="tight")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
