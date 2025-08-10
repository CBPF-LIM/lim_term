from ..config import COLOR_KEYS, MARKER_MAPPING
from ..i18n import t


def get_translated_graph_types():
    return [t("ui.graph_types.line"), t("ui.graph_types.scatter")]


def get_graph_type_mapping():
    return {
        t("ui.graph_types.line"): "line",
        t("ui.graph_types.scatter"): "scatter",
    }


def get_translated_colors():
    return [t(f"ui.colors.{color}") for color in COLOR_KEYS]


def get_color_mapping():
    return {t(f"ui.colors.{color}"): color for color in COLOR_KEYS}


def get_translated_markers():
    return [t(f"ui.markers.{m}") for m in MARKER_MAPPING.keys()]


def get_marker_mapping():
    return {t(f"ui.markers.{m}"): m for m in MARKER_MAPPING.keys()}


def get_original_marker_from_internal(internal_marker: str) -> str:
    return MARKER_MAPPING.get(internal_marker, "o")


def get_original_marker(translated_marker: str) -> str:
    for key, sym in MARKER_MAPPING.items():
        if t(f"ui.markers.{key}") == translated_marker:
            return sym
    return MARKER_MAPPING.get("circle", "o")


def get_default_series_hex_colors():
    # Fallback hex colors when no internal color is selected
    return ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#ff00ff"]
