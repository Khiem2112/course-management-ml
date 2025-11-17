from PyQt6.QtWidgets import QWidget

from utils.plot.plot_manager import PlotManager


class CourseInfoVisualizer():
    @staticmethod
    def create_dropout_rate_pie(data: dict, target_widget: QWidget) -> PlotManager:
        canvas = PlotManager._find_or_create_canvas(target_widget=target_widget)

        ax = canvas.axes
        fig = canvas.figure

        drop_out_dict = data

        # CHUYỂN Decimal → float, dict_values → list
        values = [float(v) for v in drop_out_dict.values()]
        labels = list(drop_out_dict.keys())

        ax.clear()  # tránh vẽ chồng
        ax.pie(values, labels=labels, autopct="%1.1f%%")

        fig.tight_layout()

        return PlotManager(canvas)
