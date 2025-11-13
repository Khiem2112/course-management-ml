# In application/analysis/analysis_visualizer.py
import pandas as pd
from PyQt6.QtWidgets import QWidget
from utils.plot.plot_manager import PlotManager
from utils.logger import get_class_logger

logger = get_class_logger(__name__, "AnalysisVisualizer")

class AnalysisVisualizer:
  """
  Manages creating and updating plots for the Analysis page.
  """
  @staticmethod
  def create_cluster_pie_chart(target_widget: QWidget, cluster_data: list[dict]) -> PlotManager:
    """
    Creates a pie chart from pre-aggregated cluster data.

    Args:
        target_widget: The QWidget to draw on.
        cluster_data: A list of dicts, e.g., 
                      [{'cluster_id': 'Cluster 0', 'student_count': 150}, ...]
    """
    try:
      if not cluster_data:
        logger.warning("No cluster data provided to visualize.")
        return PlotManager.clear(target_widget).set_title("No Data")

      # 1. Convert pre-aggregated data to DataFrame
      df = pd.DataFrame.from_records(cluster_data)

      # 2. Check for required columns
      if 'cluster_id' not in df.columns or 'total_student' not in df.columns:
        logger.error("Data for pie chart is missing 'cluster_id' or 'total_student'.")
        return PlotManager.clear(target_widget).set_title("Data Error")
      
      # 3. Set cluster_id as the index (for labels) and plot 'student_count'
      plot_data = df.set_index('cluster_id')['total_student']
      
      # 4. Get PlotManager and create the pie chart
      canvas = PlotManager._find_or_create_canvas(target_widget)
      plot_manager = PlotManager(canvas.figure, canvas.axes)
      ax = plot_manager.axes

      plot_data.plot(
        kind='pie',
        ax=ax,
        autopct='%1.1f%%', # Add percentages
        startangle=90,
        pctdistance=0.85
        # Labels are automatically taken from the 'plot_data' index
      )
      
      ax.set_ylabel('') # Remove the 'student_count' y-label
      ax.set_title("Student Cluster Distribution", fontsize=12)
      ax.axis('equal') # Equal aspect ratio ensures pie is drawn as a circle.
      
      plot_manager.draw()
      logger.info("Cluster pie chart created successfully.")
      return plot_manager

    except Exception as e:
      logger.error(f"Failed to create cluster pie chart: {e}", exc_info=True)
      return PlotManager.clear(target_widget).set_title("Error")