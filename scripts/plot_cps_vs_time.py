from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerBase
from matplotlib.patches import Circle
import numpy as np

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

try:
    import seaborn as sns
except ImportError:
    sns = None


RMSD_BASELINE = 0.15

# DPA4 uses the same variant-specific gradient as the inference figures. The
# remaining families follow the same convention: DPA3 the Blues ramp, MACE the
# Greens ramp and the Equiformer family neutral grays. Other baselines take
# muted accents.
if sns is not None:
    MUTED = sns.color_palette("muted", 10).as_hex()

    def _family(name, index=5):
        return sns.color_palette(name, 8).as_hex()[index]

    DPA3_COLOR = _family("Blues")
    MACE_COLOR = _family("Greens")
else:
    MUTED = [
        "#4878D0",
        "#EE854A",
        "#6ACC64",
        "#D65F5F",
        "#956CB4",
        "#8C613C",
        "#DC7EC0",
        "#797979",
        "#D5BB67",
        "#82C6E2",
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
NEQUIX_COLOR = COLORS["cyan"]
NEQUIX_PFT_COLOR = "#3C8DAB"
EXTRA_TRAINING_MODELS = {"eSEN-30M-MP", "EqV2 S DeNS", "EqV3+DeNS-MP"}


def calculate_cps(f1, ksrme, rmsd):
    f1_norm = np.clip(f1, 0, 1)
    ksrme_norm = np.clip(1 - ksrme / 2, 0, 1)
    rmsd_norm = np.clip(1 - rmsd / RMSD_BASELINE, 0, 1)
    return 0.5 * f1_norm + 0.4 * ksrme_norm + 0.1 * rmsd_norm


class DashedCircleLegend:
    def __init__(self, color, label, marker="o"):
        self.color = color
        self.marker = marker
        self._label = label

    def get_label(self):
        return self._label


class DashedCircleHandler(HandlerBase):
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ):
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


# x = A100 GPU-days, y = CPS score, params_m = model parameters in millions.
models = {
    "Nequix MP": dict(x=21, y=0.729, params_m=0.708, color=NEQUIX_COLOR, marker="o"),
    "Nequix MP PFT": dict(
        x=27, y=0.755, params_m=0.708, color=NEQUIX_PFT_COLOR, marker="o"
    ),
    "eSEN-30M-MP": dict(
        x=335, y=0.797, params_m=30.1, color=COLORS["purple"], marker="o"
    ),
    "EqV2 S DeNS": dict(x=228, y=0.522, params_m=31.2, color=EQV2_COLOR, marker="o"),
    "Eqnorm-MP": dict(x=83, y=0.756, params_m=1.31, color=COLORS["pink"], marker="o"),
    "MACE-MP-0": dict(x=108, y=0.637, params_m=4.69, color=MACE_COLOR, marker="o"),
    "HIENet": dict(x=120, y=0.707, params_m=7.51, color=COLORS["orange"], marker="o"),
    "SevenNet-l3i5": dict(
        x=381, y=0.714, params_m=1.17, color=COLORS["yellow"], marker="o"
    ),
    "DPA3": dict(x=104, y=0.718, params_m=4.81, color=DPA3_COLOR, marker="o"),
    "EqV3+DeNS-MP": dict(x=157, y=0.830, params_m=30.3, color=EQV3_COLOR, marker="o"),
    "DPA4-mini": dict(
        x=5.8, y=0.733, params_m=0.660, color=DPA4_COLORS["Mini"], marker="o"
    ),
    "DPA4-neo": dict(
        x=8.6, y=0.782, params_m=1.125, color=DPA4_COLORS["Neo"], marker="o"
    ),
    "DPA4-air": dict(
        x=16, y=0.811, params_m=5.148, color=DPA4_COLORS["Air"], marker="o"
    ),
    "DPA4-plus": dict(
        x=31, y=0.829, params_m=8.796, color=DPA4_COLORS["Plus"], marker="o"
    ),
    "DPA4-pro": dict(
        x=233, y=0.842, params_m=25.211, color=DPA4_COLORS["Pro"], marker="o"
    ),
}

matris = {
    "L": dict(x=224, y=0.778, params_m=10.4),
}


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


def draw_dpa4_trend(ax):
    dpa4_xy = [
        (models["DPA4-mini"]["x"], models["DPA4-mini"]["y"]),
        (models["DPA4-neo"]["x"], models["DPA4-neo"]["y"]),
        (models["DPA4-air"]["x"], models["DPA4-air"]["y"]),
        (models["DPA4-plus"]["x"], models["DPA4-plus"]["y"]),
        (models["DPA4-pro"]["x"], models["DPA4-pro"]["y"]),
    ]
    ax.plot(
        [p[0] for p in dpa4_xy],
        [p[1] for p in dpa4_xy],
        linestyle=PARETO_LINE_STYLE,
        color=DPA4_COLOR,
        linewidth=PARETO_LINE_WIDTH,
        alpha=0.88,
        zorder=2,
    )


def main() -> None:
    apply_publication_style()
    fig, (ax_top, ax_bottom) = create_broken_axis_figure()

    for ax in (ax_top, ax_bottom):
        style_log_axis(
            ax,
            x_limits=(4.6, 470),
            ticks=(5, 10, 30, 60, 100, 200, 400),
            tick_labels=("5", "10", "30", "60", "100", "200", "400"),
        )
        plot_model_points(ax)

    ax_top.set_ylim(0.695, 0.862)
    ax_top.set_yticks([0.70, 0.72, 0.74, 0.76, 0.78, 0.80, 0.82, 0.84, 0.86])
    ax_bottom.set_ylim(0.50, 0.665)
    ax_bottom.set_yticks([0.50, 0.55, 0.60, 0.65])
    draw_axis_break(ax_top, ax_bottom)
    draw_dpa4_trend(ax_top)

    ax_top.annotate(
        "Mini",
        xy=(models["DPA4-mini"]["x"], models["DPA4-mini"]["y"]),
        xytext=(3, -15),
        textcoords="offset points",
        fontsize=ANNOTATION_FONT_SIZE,
        fontweight="bold",
        color=DPA4_COLOR,
    )
    ax_top.annotate(
        "Neo",
        xy=(models["DPA4-neo"]["x"], models["DPA4-neo"]["y"]),
        xytext=(4, -15),
        textcoords="offset points",
        fontsize=ANNOTATION_FONT_SIZE,
        fontweight="bold",
        color=DPA4_COLOR,
    )
    ax_top.annotate(
        "Air",
        xy=(models["DPA4-air"]["x"], models["DPA4-air"]["y"]),
        xytext=(-17, 8),
        textcoords="offset points",
        fontsize=ANNOTATION_FONT_SIZE,
        fontweight="bold",
        color=DPA4_COLOR,
    )
    ax_top.annotate(
        "Plus",
        xy=(models["DPA4-plus"]["x"], models["DPA4-plus"]["y"]),
        xytext=(-22, 10),
        textcoords="offset points",
        fontsize=ANNOTATION_FONT_SIZE,
        fontweight="bold",
        color=DPA4_COLOR,
    )
    ax_top.annotate(
        "Pro",
        xy=(models["DPA4-pro"]["x"], models["DPA4-pro"]["y"]),
        xytext=(-22, 10),
        textcoords="offset points",
        fontsize=ANNOTATION_FONT_SIZE,
        fontweight="bold",
        color=DPA4_COLOR,
    )

    eqv3 = models["EqV3+DeNS-MP"]
    plus_cost = models["DPA4-plus"]["x"]
    draw_ratio_arrow(
        ax_top,
        source_x=eqv3["x"],
        target_x=plus_cost,
        y=eqv3["y"],
        ratio=eqv3["x"] / plus_cost,
        label_x=62,
        shrink_source=15,
        shrink_target=11,
    )
    esen = models["eSEN-30M-MP"]
    esen_target_cost = trend_cost_at_cps(esen["y"], "DPA4-neo", "DPA4-air")
    draw_ratio_arrow(
        ax_top,
        source_x=esen["x"],
        target_x=esen_target_cost,
        y=esen["y"],
        ratio=esen["x"] / esen_target_cost,
        label_x=42,
        shrink_source=15,
        shrink_target=3,
    )

    legend_entries = [
        ("Nequix MP", models["Nequix MP"]),
        ("Nequix MP PFT", models["Nequix MP PFT"]),
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
    legend_bbox = (
        leg.get_frame()
        .get_window_extent(fig.canvas.get_renderer())
        .transformed(ax_bottom.transAxes.inverted())
    )
    param_box_x = legend_bbox.x1 - 0.032
    param_box_y = legend_bbox.y0
    param_box_w = 0.135
    param_box_h = legend_bbox.height * 0.90
    draw_param_scale(
        ax_bottom,
        param_box_x,
        param_box_y,
        param_box_w,
        param_box_h,
    )
    draw_pareto_legend(
        ax_bottom,
        anchor_x=param_box_x + param_box_w + 0.02,
        anchor_y=param_box_y + param_box_h / 2,
    )

    finalize_figure(fig, ax_bottom, "Training cost (A100 GPU-days)")
    output_path = (
        Path(__file__).resolve().parents[1] / "fig" / "cps-training-cost-pareto.pdf"
    )
    fig.savefig(output_path)
    plt.close(fig)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
