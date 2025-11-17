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
  QMainWindow,
  QStackedWidget
)
from PyQt6.QtCore import Qt
from ui.analysis_ui import Ui_MainWindow as AnalysisUI
from database.student.student_logic import StudentsLogic
from utils.table.table_manager import TableWidgetManager
from utils.logger import get_class_logger
from application.analysis.analysis_visualizer import AnalysisVisualizer
from application.analysis.cluster_detailed_page import ClusterDetailPage

# Import the RecommendationService from your predict.py file
# (Adjust path if predict.py is not in the root or a reachable module)
from  ml.inference.predict import RecommendationManager as RecommendationService

import sys
from functools import partial
from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QPushButton
from base.widgets import ClusterPaperWidget
from ui.analysis_ui import Ui_MainWindow as AnalysisUI
from database.student.student_logic import StudentsLogic
from utils.logger import get_class_logger
from application.analysis.analysis_visualizer import AnalysisVisualizer
from application.analysis.cluster_detailed_page import ClusterDetailPage # <-- Import Detail Page
class AnalysisManagementEx:
  def __init__(self, main_window: QWidget, ui: AnalysisUI):
        
    self.main_window = main_window # This is the AnalysisFrame (QWidget)
    self.ui = ui
    self.logger = get_class_logger(__name__, self.__class__.__name__)
    
    self.recommend_service = RecommendationService()
    
    # --- 1. Find the parent layout of the content ---
    # This is the main vertical layout of the central_page
    self.ui.horizontalLayout.setStretch(1,1)
    self.content_parent_layout = self.ui.verticalLayout_2 
    if not self.content_parent_layout:
        self.logger.error("UI is missing 'verticalLayout_2'. Cannot build router.")
        return

    # --- 2. Identify the original "Master Page" (Page 0) ---
    # This is the frame holding your pie chart and cluster list
    self.cluster_list_page = self.ui.main_page
    if not self.cluster_list_page:
        self.logger.error("UI is missing 'main_page'. Cannot build router.")
        return

    # --- 3. Create the "Detail Page" (Page 1) ---
    self.cluster_detail_page = ClusterDetailPage(self.recommend_service)
    
    # --- 4. Create the Router Stack ---
    self.page_stack = QStackedWidget()
    self.page_stack.addWidget(self.cluster_list_page)  # Index 0
    self.page_stack.addWidget(self.cluster_detail_page) # Index 1

    # --- 5. CRITICAL FIX: Replace frame_6 with the page_stack ---
    # This swaps the original content (frame_6) with your new router.
    self.content_parent_layout.addWidget(self.page_stack)
    
    # --- 7. Set the stretch factor ---
    # This tells the layout to give all extra space to your new stack
    # (just like it did for frame_6)
    #
    self.content_parent_layout.setStretch(2, 10)

    # --- 6. Connect signals and load data ---
    self.connect_signals()
    self.load_cluster_list_page()
    self.page_stack.setCurrentIndex(0) # Start on the list page

  def load_cluster_list_page(self):
    """
    Loads the pie chart and the list of clickable cluster "papers".
    """
    # 1. Get aggregated data for the pie chart
    cluster_counts = StudentsLogic.get_cluster_student_counts()
    
    if not cluster_counts:
      self.logger.warning("No cluster count data found. Analysis page will be empty.")
      return

    # Visualize the cluster distribution
    AnalysisVisualizer.create_cluster_pie_chart(
      target_widget=self.ui.pie_chart_widget,
      cluster_data=cluster_counts,
      name_map=self.recommend_service.CLUSTER_NAME_MAP # <--- Pass the map here
    )
    
    
    

    # Create the "Cluster Papers"
    list_layout = self.ui.cluster_layout 
    if list_layout is None: return
    
    # --- BEAUTIFY LAYOUT ---
    list_layout.setSpacing(15) # Add nice gap between items
    list_layout.setContentsMargins(10, 10, 15, 10) # Add padding around the list
    # -----------------------

    # Clear old list
    while list_layout.count():
      child = list_layout.takeAt(0)
      if child.widget(): child.widget().deleteLater()
        
    # 4. Add new ClusterPaperWidgets
    for cluster_info in cluster_counts:
      cluster_name_label = cluster_info['cluster_id']
      count = cluster_info['student_count']
      
      try:
        cluster_raw_id = int(cluster_name_label.split(" ")[-1])
      except:
        cluster_raw_id = -1
      
      # Get friendly name
      cluster_name = self.recommend_service.CLUSTER_NAME_MAP.get(
          cluster_raw_id, cluster_name_label
      )
      
      # Get Color
      bg_color = AnalysisVisualizer.CLUSTER_COLORS.get(
          cluster_raw_id, AnalysisVisualizer.DEFAULT_COLOR
      )
      
      # Text for the label
      paper_text = f"{cluster_name}\n({count} Students)"
      
      # --- CREATE CUSTOM WIDGET ---
      paper_widget = ClusterPaperWidget(text=paper_text, color=bg_color)
      
      # Connect Click
      paper_widget.clicked.connect(
          partial(self.show_cluster_detail, cluster_raw_id, cluster_name)
      )
      
      list_layout.addWidget(paper_widget)
      
    list_layout.addStretch() # Push items to the top
    
  def connect_signals(self):
    """Connects the Back button."""
    try:
      self.cluster_detail_page.ui.back_button.clicked.connect(self.show_cluster_list)
    except AttributeError as e:
      self.logger.warning(f"Could not connect navigation signals: {e}")

  # --- SLOTS for navigation ---
  
  def show_cluster_detail(self, cluster_id: int, cluster_name: str):
    """
    Navigates to the detail page for a specific cluster.
    """
    self.logger.info(f"Navigating to detail for cluster {cluster_id}")
    self.cluster_detail_page.load_data(cluster_id, cluster_name)
    self.page_stack.setCurrentIndex(1)
    
  def show_cluster_list(self):
    """
    Navigates back to the main cluster list.
    """
    self.logger.info("Navigating back to cluster list")
    self.page_stack.setCurrentIndex(0)