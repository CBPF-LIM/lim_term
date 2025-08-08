"""
Matplotlib performance optimizations for Lim Terminal.
This module configures matplotlib for optimal performance by disabling
expensive rendering features while maintaining visual quality.
"""

import matplotlib


def configure_matplotlib_performance():
    """Configure matplotlib for optimal performance."""

    matplotlib.use("TkAgg")

    matplotlib.rcParams["lines.antialiased"] = False
    matplotlib.rcParams["patch.antialiased"] = False
    matplotlib.rcParams["text.antialiased"] = False

    matplotlib.rcParams["figure.max_open_warning"] = 0
    matplotlib.rcParams["axes.spines.left"] = True
    matplotlib.rcParams["axes.spines.bottom"] = True
    matplotlib.rcParams["axes.spines.top"] = False
    matplotlib.rcParams["axes.spines.right"] = False
    matplotlib.rcParams["xtick.top"] = False
    matplotlib.rcParams["ytick.right"] = False
    matplotlib.rcParams["legend.frameon"] = True
    matplotlib.rcParams["legend.fancybox"] = False
    matplotlib.rcParams["axes.linewidth"] = 0.8
    matplotlib.rcParams["grid.linewidth"] = 0.5
    matplotlib.rcParams["lines.linewidth"] = 1.0
    matplotlib.rcParams["patch.linewidth"] = 0.5
    matplotlib.rcParams["font.size"] = 10
    matplotlib.rcParams["axes.titlesize"] = 10
    matplotlib.rcParams["axes.labelsize"] = 10
    matplotlib.rcParams["xtick.labelsize"] = 10
    matplotlib.rcParams["ytick.labelsize"] = 10
    matplotlib.rcParams["legend.fontsize"] = 10
    matplotlib.rcParams["figure.dpi"] = 80
    matplotlib.rcParams["savefig.dpi"] = 100
    matplotlib.rcParams["axes.formatter.use_mathtext"] = False
    matplotlib.rcParams["text.usetex"] = False

    matplotlib.rcParams["figure.facecolor"] = "white"
    matplotlib.rcParams["axes.facecolor"] = "white"
    matplotlib.rcParams["savefig.facecolor"] = "white"
    matplotlib.rcParams["savefig.transparent"] = False
    matplotlib.rcParams["legend.facecolor"] = "white"
    matplotlib.rcParams["legend.edgecolor"] = "black"
    matplotlib.rcParams["patch.facecolor"] = "blue"
    matplotlib.rcParams["patch.edgecolor"] = "black"

    matplotlib.rcParams["figure.frameon"] = True
    matplotlib.rcParams["axes.axisbelow"] = True


def get_optimized_figure_params():
    """Return additional figure-level optimizations that can be applied per-figure."""
    return {
        "patch_visible": True,
        "axisbelow": True,
        "spines_top": False,
        "spines_right": False,
        "ticks_top": False,
        "ticks_right": False,
        "facecolor": "white",
        "legend_framealpha": 1.0,
        "legend_facecolor": "white",
    }
