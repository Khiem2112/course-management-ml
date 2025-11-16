# In application/analysis_ex.py
import sys
from functools import partial
from PyQt6.QtWidgets import (
  QWidget, 
  QPushButton, 
  QLabel, 
  QTableWidgetItem, 
  QMessageBox, 
  QVBoxLayout,
  QMainWindow
)
from PyQt6.QtCore import Qt
from ui.analysis_ui import Ui_MainWindow as AnalysisUI
from database.student.student_logic import StudentsLogic
from utils.table.table_manager import TableWidgetManager
from utils.logger import get_class_logger
from application.analysis.analysis_visualizer import AnalysisVisualizer

# Import the RecommendationService from your predict.py file
# (Adjust path if predict.py is not in the root or a reachable module)
from inference.predict import RecommendationManager as RecommendationService

class AnalysisManagementEx:
  def __init__(self, main_window: QMainWindow, ui:AnalysisUI):
    
    self.main_window = main_window # This is the AnalysisFrame (QWidget)
    self.ui = ui
    self.logger = get_class_logger(__name__, self.__class__.__name__)
    
    self.all_students_data = [] # Holds the FULL list
    
    # --- 1. Instantiate Services ---
    self.table_manager = TableWidgetManager(table_widget=self.ui.analysis_table)
    self.recommend_service = RecommendationService() # From predict.py
    

    # --- 3. Connect Signals & Load Data ---
    # self.connect_signals()
    self.load_cluster_data()

  def load_cluster_data(self):
    """
    Fetches ALL student cluster data from the DB and displays it.
    """
    # --- NOTE: You must create this function in StudentsLogic ---
    # It should return a list of dicts:
    # [{'id_student': 123, 'code_module': 'AAA', 'code_presentation': '2013J', 'cluster_id': 0, ...}, ...]
    self.all_students_data = StudentsLogic.get_all_clusters() or []
    
    if not self.all_students_data:
      self.logger.warning("No student cluster data found.")
      return

    # 1. Load data into the table
    self.table_manager.load_data(
      data=self.all_students_data,
      table_type='no_id' # Example: hides 'id' column if it exists
    )
    
    # 2. Visualize the cluster distribution
    self.logger.info(f'Student data: {self.all_students_data}')
    AnalysisVisualizer.create_cluster_pie_chart(
      target_widget=self.ui.pie_chart_widget, # The QWidget for plotting
      cluster_data=self.all_students_data
    )

  def connect_signals(self):
    """Connects UI elements like the table."""
    try:
      # Connect table click to show recommendation
      
      # Connect search/filter buttons
      # self.ui.analysis_search_button.clicked.connect(self.on_search)
      pass
    except AttributeError as e:
      self.logger.warning(f"Could not connect analysis signals: {e}")

