import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ..config import FIGURE_SIZE, FIGURE_DPI


class GraphManager:


    def __init__(self, parent_widget):
        self.figure = plt.Figure(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, parent_widget)

    def get_widget(self):

        return self.canvas.get_tk_widget()

    def clear(self):

        self.ax.clear()

    def plot_line(self, x_data, y_data, color="blue", marker="o"):

        self.ax.plot(x_data, y_data, color=color, marker=marker)



    def plot_scatter(self, x_data, y_data, color="blue", marker="o"):

        self.ax.scatter(x_data, y_data, color=color, marker=marker)

    def set_limits(self, min_x=None, max_x=None, min_y=None, max_y=None):

        if min_x is not None or max_x is not None:
            self.ax.set_xlim(min_x, max_x)
        if min_y is not None or max_y is not None:
            self.ax.set_ylim(min_y, max_y)

    def set_labels(self, title="Graph", xlabel="X", ylabel="Y"):

        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

    def update(self):

        self.canvas.draw()

    def plot_from_settings(self, x_data, y_data, settings, x_col=0, y_col=1, title=None, xlabel=None, ylabel=None):

        self.clear()

        graph_type = settings.get("type", "Linha")
        color = settings.get("color", "blue").lower()
        marker = settings.get("dot_type", "o")


        if color in ["blue", "cyan", "teal", "green", "lime", "yellow", "amber",
                    "orange", "red", "magenta", "indigo", "violet", "turquoise",
                    "aquamarine", "springgreen", "chartreuse", "gold", "coral",
                    "crimson", "pink"]:
            color = color.lower()

        if graph_type == "Linha":
            self.plot_line(x_data, y_data, color=color, marker=marker)
        elif graph_type == "Dispersão":
            self.plot_scatter(x_data, y_data, color=color, marker=marker)


        min_x = float(settings.get("min_x", "0")) if settings.get("min_x") else None
        max_x = float(settings.get("max_x", "0")) if settings.get("max_x") else None
        min_y = float(settings.get("min_y", "0")) if settings.get("min_y") else None
        max_y = float(settings.get("max_y", "0")) if settings.get("max_y") else None

        self.set_limits(min_x, max_x, min_y, max_y)
        self.set_labels(
            title=title or "Graph",
            xlabel=xlabel or f"Column {x_col + 1}",
            ylabel=ylabel or f"Column {y_col + 1}"
        )
        self.update()

    def plot_multi_series(self, x_data, y_series_data, settings_list, x_col=0, title=None, xlabel=None, ylabel=None):

        self.clear()

        plotted_series = 0

        for i, (y_data, settings) in enumerate(zip(y_series_data, settings_list)):
            if not y_data:
                continue

            graph_type = settings.get("type", "Line")
            color = settings.get("color", "blue").lower()
            marker = settings.get("marker", "o")


            if color in ["blue", "cyan", "teal", "green", "lime", "yellow", "amber",
                        "orange", "red", "magenta", "indigo", "violet", "turquoise",
                        "aquamarine", "springgreen", "chartreuse", "gold", "coral",
                        "crimson", "pink"]:
                color = color.lower()


            series_label = f"Y{i+1}"


            if graph_type in ["Linha", "Line", "line"]:
                self.ax.plot(x_data, y_data, color=color, marker=marker, label=series_label)
            elif graph_type in ["Dispersão", "Scatter", "scatter"]:
                self.ax.scatter(x_data, y_data, color=color, marker=marker, label=series_label)

            plotted_series += 1


        if plotted_series > 1:
            self.ax.legend()


        if settings_list:
            first_settings = settings_list[0]
            min_y = float(first_settings.get("min_y", "0")) if first_settings.get("min_y") else None
            max_y = float(first_settings.get("max_y", "0")) if first_settings.get("max_y") else None
            self.set_limits(None, None, min_y, max_y)

        self.set_labels(
            title=title or "Graph",
            xlabel=xlabel or f"Column {x_col + 1}",
            ylabel=ylabel or "Value"
        )
        self.update()

    def plot_stacked_series(self, x_data, y_series_data, colors, normalize_100=False, title=None, xlabel=None, ylabel=None):
        """Plot stacked area chart using pure Python without numpy dependency"""
        self.clear()

        if not y_series_data or not x_data:
            return


        x_list = list(x_data)
        y_lists = []
        labels = []
        actual_colors = []


        for i, y_data in enumerate(y_series_data):
            if y_data:
                y_lists.append(list(y_data))
                labels.append(f"Y{i+1}")
                actual_colors.append(colors[i] if i < len(colors) else "#1f77b4")

        if not y_lists:
            return


        min_length = min(len(x_list), min(len(y) for y in y_lists))
        x_list = x_list[:min_length]
        y_lists = [y[:min_length] for y in y_lists]


        if normalize_100:

            normalized_y_lists = []
            for i in range(min_length):
                total = sum(y_list[i] for y_list in y_lists)
                if total == 0:
                    total = 1
                normalized_y_lists.append([y_list[i] / total * 100 for y_list in y_lists])


            y_lists = [[normalized_y_lists[i][j] for i in range(min_length)] for j in range(len(y_lists))]
            ylabel_text = ylabel or "Percentage (%)"
        else:
            ylabel_text = ylabel or "Value"


        self.ax.stackplot(x_list, *y_lists, labels=labels, colors=actual_colors, alpha=0.8)


        self.ax.legend(loc='upper left')


        self.set_labels(
            title=title or "Stacked Chart",
            xlabel=xlabel or "X",
            ylabel=ylabel_text
        )

        self.update()
