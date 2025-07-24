"""
Graph tab settings management module.
Handles preferences, settings loading/saving, and translation utilities.
"""

from ..i18n import get_config_manager
from ..config import MARKER_MAPPING


class GraphTabSettings:
    """Manages settings and preferences for the graph tab."""

    def __init__(self, config_manager=None):
        self.config_manager = config_manager or get_config_manager()
        self.graph_settings = {}

    def load_preferences(self):
        """Load preferences from config."""
        # Load main settings
        self.graph_settings['x_column'] = self.config_manager.load_tab_setting(
            'graph.general', 'x_column', '1'
        )
        self.graph_settings['chart_type'] = self.config_manager.load_tab_setting(
            'graph.general', 'chart_type', 'Time Series'
        )
        self.graph_settings['refresh_rate'] = self.config_manager.load_tab_setting(
            'graph.general', 'refresh_rate', '30'
        )

        # Load series settings
        for i in range(5):
            group = f'graph_series_{i}'
            series_settings = self.load_group_preferences(group)
            self.graph_settings[f'series_{i}'] = series_settings

        return self.graph_settings

    def load_group_preferences(self, group):
        """Load preferences for a specific group."""
        return {
            'column': self.config_manager.load_tab_setting(group, 'column', ''),
            'type': self.config_manager.load_tab_setting(group, 'type', 'Line'),
            'color': self.config_manager.load_tab_setting(group, 'color', 'blue'),
            'marker': self.config_manager.load_tab_setting(group, 'marker', 'o'),
            'enabled': self.config_manager.load_tab_setting(group, 'enabled', False)
        }

    def save_preferences(self, settings):
        """Save preferences to config."""
        # Save main settings
        if 'x_column' in settings:
            self.config_manager.save_tab_setting('graph.general', 'x_column', settings['x_column'])
        if 'chart_type' in settings:
            self.config_manager.save_tab_setting('graph.general', 'chart_type', settings['chart_type'])
        if 'refresh_rate' in settings:
            self.config_manager.save_tab_setting('graph.general', 'refresh_rate', settings['refresh_rate'])

        # Save series settings
        for i in range(5):
            series_key = f'series_{i}'
            if series_key in settings:
                group = f'graph_series_{i}'
                series_data = settings[series_key]
                for key, value in series_data.items():
                    self.config_manager.save_tab_setting(group, key, value)

    def get_series_settings(self, series_index):
        """Get settings for a specific series."""
        return self.graph_settings.get(f'series_{series_index}', {
            'column': '',
            'type': 'Line',
            'color': 'blue',
            'marker': 'o',
            'enabled': False
        })

    def update_series_settings(self, series_index, key, value):
        """Update settings for a specific series."""
        series_key = f'series_{series_index}'
        if series_key not in self.graph_settings:
            self.graph_settings[series_key] = {}
        self.graph_settings[series_key][key] = value

    def get_translated_graph_types(self):
        """Get list of translated graph type options."""
        from ..i18n import t
        return [
            t("ui.graph_types.line"),
            t("ui.graph_types.scatter")
        ]

    def get_translated_colors(self):
        """Get list of translated color options."""
        from ..i18n import t
        return [
            t("ui.colors.blue"),
            t("ui.colors.red"),
            t("ui.colors.green"),
            t("ui.colors.orange"),
            t("ui.colors.magenta"),
            t("ui.colors.cyan"),
            t("ui.colors.yellow")
        ]

    def get_translated_markers(self):
        """Get list of translated marker options."""
        from ..i18n import t
        return [
            t("ui.markers.circle"),
            t("ui.markers.square"),
            t("ui.markers.triangle"),
            t("ui.markers.diamond"),
            t("ui.markers.star"),
            t("ui.markers.plus")
        ]

    def get_original_marker(self, translated_marker):
        """Convert translated marker back to original marker symbol."""
        from ..i18n import t
        marker_map = {
            t("ui.markers.circle"): "o",
            t("ui.markers.square"): "s",
            t("ui.markers.triangle"): "^",
            t("ui.markers.diamond"): "D",
            t("ui.markers.star"): "*",
            t("ui.markers.plus"): "+"
        }
        return marker_map.get(translated_marker, "o")

    def get_translated_marker_from_original(self, original_marker):
        """Convert original marker symbol to translated marker."""
        from ..i18n import t
        reverse_map = {
            "o": t("ui.markers.circle"),
            "s": t("ui.markers.square"),
            "^": t("ui.markers.triangle"),
            "D": t("ui.markers.diamond"),
            "*": t("ui.markers.star"),
            "+": t("ui.markers.plus")
        }
        return reverse_map.get(original_marker, t("ui.markers.circle"))

    def get_original_graph_type(self, translated_type):
        """Convert translated graph type back to original type."""
        from ..i18n import t
        type_map = {
            t("ui.graph_types.line"): "line",
            t("ui.graph_types.scatter"): "scatter"
        }
        return type_map.get(translated_type, "line")

    def get_original_color(self, translated_color):
        """Convert translated color back to original color."""
        from ..i18n import t
        color_map = {
            t("ui.colors.blue"): "blue",
            t("ui.colors.red"): "red",
            t("ui.colors.green"): "green",
            t("ui.colors.orange"): "orange",
            t("ui.colors.magenta"): "magenta",
            t("ui.colors.cyan"): "cyan",
            t("ui.colors.yellow"): "yellow"
        }
        return color_map.get(translated_color, "blue")
