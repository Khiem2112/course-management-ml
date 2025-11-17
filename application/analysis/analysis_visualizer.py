# In application/analysis/analysis_visualizer.py
import pandas as pd
from PyQt6.QtWidgets import QWidget
from utils.plot.plot_manager import PlotManager
from utils.logger import get_class_logger

logger = get_class_logger(__name__, "AnalysisVisualizer")

class AnalysisVisualizer:
  # ... (CLUSTER_COLORS dictionary remains the same) ...
  CLUSTER_COLORS = {
      0: "#FF9999", 1: "#66B2FF", 2: "#99FF99", 3: "#FFCC99",
      4: "#C2C2F0", 5: "#FFB3E6", 6: "#C4E17F"
  }
  DEFAULT_COLOR = "#E0E0E0"

  @staticmethod
  def create_cluster_pie_chart(target_widget: QWidget, cluster_data: list[dict], name_map: dict = None) -> PlotManager:
    """
    Creates a pie chart with mapped names and consistent colors.
    
    Args:
        target_widget: The widget to draw on.
        cluster_data: List of dicts [{'cluster_id': 0, 'student_count': 10}, ...]
        name_map: Optional dict {0: "Cluster Name", ...}
    """
    try:
      if not cluster_data:
        return PlotManager.clear(target_widget).set_title("No Data")

      df = pd.DataFrame.from_records(cluster_data)
      if 'cluster_id' not in df.columns or 'student_count' not in df.columns:
        return PlotManager.clear(target_widget).set_title("Data Error")
      
      # --- Prepare Data, Labels, and Colors ---
      counts = []
      labels = []
      colors = []
      
      # Iterate through the DataFrame to build aligned lists
      for index, row in df.iterrows():
          c_id_raw = row['cluster_id']
          count = row['student_count']
          
          # 1. Resolve ID (handle "Cluster 0" strings or int 0)
          try:
              if isinstance(c_id_raw, str) and "Cluster" in c_id_raw:
                  c_id = int(c_id_raw.split(" ")[-1])
              else:
                  c_id = int(c_id_raw)
          except (ValueError, TypeError):
              c_id = -1

          # 2. Get Name (Label) -> THIS IS THE CHANGE
          if name_map and c_id in name_map:
              labels.append(name_map[c_id])
          else:
              labels.append(f"Cluster {c_id}")

          # 3. Get Color (Consistent with buttons)
          colors.append(AnalysisVisualizer.CLUSTER_COLORS.get(c_id, AnalysisVisualizer.DEFAULT_COLOR))
          counts.append(count)

      # --- Plotting ---
      plot_manager = PlotManager.get_or_create(target_widget)
      plot_manager.clear_plot()
      ax = plot_manager.axes

      # Plot using our prepared lists
      ax.pie(
        counts,
        labels=labels, # Use our descriptive names
        colors=colors, # Use our matched colors
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.85,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1}
      )
      
      ax.set_title("Student Cluster Distribution", fontsize=12)
      ax.axis('equal')
      
      plot_manager.draw()
      return plot_manager

    except Exception as e:
      logger.error(f"Failed to create cluster pie chart: {e}", exc_info=True)
      return PlotManager.clear(target_widget).set_title("Error")