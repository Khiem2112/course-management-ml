from database.course.course import get_dropout_percentage
from utils.plot.plot_manager import PlotManager, MplCanvas
from PyQt6.QtWidgets import QWidget

class CourseInfoVisualizer():
  @staticmethod
  def create_dropout_rate_pie(data: dict, target_widget: QWidget) -> PlotManager:
    
    canvas = PlotManager._find_or_create_canvas(target_widget=target_widget)
    
    ax = canvas.axes
    fig = canvas.figure
    
    drop_out_dict = data
    ax.pie(x=drop_out_dict.values(), labels= drop_out_dict.keys(), autopct="%1.1f%%")
    return PlotManager(figure=fig, axes=ax)