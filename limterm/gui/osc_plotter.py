from ..i18n import t
from ..matplotlib_optimizations import get_optimized_figure_params
import matplotlib.pyplot as plt


class OscPlotter:

    def __init__(self, graph_manager, trigger_source, trigger_level, window_size):
        self.graph_manager = graph_manager
        self.trigger_source = trigger_source
        self.trigger_level = trigger_level
        self.window_size = window_size

        self.data_line = None
        self.trigger_level_line = None
        self.trigger_point_line = None
        self.expected_window_line = None

        self.use_lines_only = True
        self.persistent_plotting = True
        self.background = None

        self.set_buffer_size = 4
        self.capture_sets = []
        self.current_set_index = 0

    def plot_realtime_data(self, trigger_data):
        if not trigger_data or not hasattr(self, "graph_manager"):
            return

        try:
            trigger_col = int(self.trigger_source.get_value()) - 1

            x_data, y_data = self._extract_plot_data(trigger_data, trigger_col)

            if x_data and y_data:
                self._plot_current_and_buffer_sets(
                    x_data, y_data, trigger_col, t("ui.osc_tab.capture_live_title")
                )

        except Exception as e:
            print(t("errors.realtime_plot_error", error=str(e)))

    def plot_final_data(self, trigger_data):
        if not trigger_data or not hasattr(self, "graph_manager"):
            return

        try:
            trigger_col = int(self.trigger_source.get_value()) - 1

            x_data, y_data = self._extract_plot_data(trigger_data, trigger_col)

            if x_data and y_data:
                self._add_to_buffer(x_data, y_data)

                self._plot_buffer_sets(
                    trigger_col, t("ui.osc_tab.capture_complete_title")
                )

                return y_data

        except Exception as e:
            print(t("errors.final_plot_error", error=str(e)))
            return None

    def _add_to_buffer(self, x_data, y_data):
        while len(self.capture_sets) < self.set_buffer_size:
            self.capture_sets.append(None)

        self.capture_sets[self.current_set_index] = (x_data, y_data)

        self.current_set_index = (self.current_set_index + 1) % self.set_buffer_size

    def _plot_current_and_buffer_sets(self, current_x, current_y, trigger_col, title):
        self.graph_manager.clear()

        for capture_set in self.capture_sets:
            if capture_set is not None:
                x_data, y_data = capture_set
                self.graph_manager.ax.plot(x_data, y_data, color="blue", linewidth=0.8)

        if current_x and current_y:
            self.graph_manager.ax.plot(
                current_x, current_y, color="blue", linewidth=1.0
            )

        self._add_static_elements(trigger_col, title)

        self._update_axis_limits()

        self.graph_manager.canvas.draw_idle()

    def _plot_buffer_sets(self, trigger_col, title):
        self.graph_manager.clear()

        for capture_set in self.capture_sets:
            if capture_set is not None:
                x_data, y_data = capture_set
                self.graph_manager.ax.plot(x_data, y_data, color="blue", linewidth=0.8)

        self._add_static_elements(trigger_col, title)

        self._update_axis_limits()

        self.graph_manager.canvas.draw_idle()

    def _add_static_elements(self, trigger_col, title):
        trigger_level = float(self.trigger_level.get_value())

        all_x = []
        for capture_set in self.capture_sets:
            if capture_set is not None:
                x_data, _ = capture_set
                all_x.extend(x_data)

        if all_x:
            min_x, max_x = min(all_x), max(all_x)
        else:
            min_x, max_x = 0, int(self.window_size.get_value())

        self.graph_manager.ax.plot(
            [min_x, max_x],
            [trigger_level, trigger_level],
            color="red",
            linestyle="--",
            label=t("ui.osc_tab.trigger_level_line"),
        )

        self.graph_manager.ax.set_xlabel(t("ui.osc_tab.samples_after_trigger"))
        self.graph_manager.ax.set_ylabel(
            t("ui.osc_tab.column_label", column=trigger_col + 1)
        )
        self.graph_manager.ax.set_title(title)
        self.graph_manager.ax.grid(True, alpha=1.0, linewidth=0.5, color="lightgray")

    def _update_axis_limits(self):
        all_x = []
        all_y = []

        for capture_set in self.capture_sets:
            if capture_set is not None:
                x_data, y_data = capture_set
                all_x.extend(x_data)
                all_y.extend(y_data)

        if not all_x or not all_y:
            self.graph_manager.ax.set_xlim(0, int(self.window_size.get_value()))
            return

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        x_range = max_x - min_x
        y_range = max_y - min_y

        x_margin = max(1, x_range * 0.05)
        y_margin = max(0.1, y_range * 0.1)

        self.graph_manager.ax.set_xlim(min_x - x_margin, max_x + x_margin)
        self.graph_manager.ax.set_ylim(min_y - y_margin, max_y + y_margin)

    def clear_all_data(self):
        self.capture_sets = []
        self.current_set_index = 0
        self.data_line = None
        self.trigger_level_line = None
        self.trigger_point_line = None
        self.expected_window_line = None
        self.background = None

        if hasattr(self, "graph_manager"):
            self.graph_manager.clear()

    def _extract_plot_data(self, trigger_data, trigger_col):
        x_data = []
        y_data = []

        for i, line in enumerate(trigger_data):
            try:
                values = line.split()
                if trigger_col < len(values):
                    x_data.append(i)
                    y_data.append(float(values[trigger_col]))
            except (ValueError, IndexError):
                continue

        return x_data, y_data
