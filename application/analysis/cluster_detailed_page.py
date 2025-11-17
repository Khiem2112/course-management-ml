# In application/analysis/cluster_detail_page.py
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QLabel
from PyQt6.QtCore import Qt
from ui.cluster_detail_ui import Ui_ClusterDetailPageWidget # From the .ui I provided
from database.student.student_logic import StudentsLogic
from ml.inference.predict import RecommendationManager as RecommendationService #
from utils.table.table_manager import TableWidgetManager
from utils.logger import get_class_logger

class ClusterDetailPage(QWidget):
  """
  This is the "Detail" page widget. It shows the list of students
  in a cluster and their recommendations.
  """
  def __init__(self, recommend_service: RecommendationService, parent=None):
    super().__init__(parent)
    self.ui = Ui_ClusterDetailPageWidget()
    self.ui.setupUi(self)
    self.logger = get_class_logger(__name__, self.__class__.__name__)
    
    # Store the single, shared instance of the service
    self.recommend_service = recommend_service
    self.table_manager = TableWidgetManager(self.ui.student_table)
    
    # Connect the table click signal to our new slot
    self.ui.student_table.itemClicked.connect(self.on_student_selected)
  def _preprocess_student_data(self, raw_student_list: list[dict]) -> list[dict]:
    """
    PURE LOGIC: Transforms raw DB rows into display-ready dictionaries.
    No UI manipulation happens here.
    """
    processed_list = []
    
    for row in raw_student_list:
      # 1. Extract raw data
      method_id = row.get('study_method_id')
      cluster_id = row.get('cluster_id')
      
      # 2. Get Recommendation Labels (In-Memory, Instant)
      # We use the service's internal logic to map IDs -> Labels
      if method_id is not None and cluster_id is not None:
        reco_data = self.recommend_service.get_recommendation(
            study_method_id=int(method_id), 
            cluster_id=int(cluster_id)
        )
        method_label = reco_data.get('study_method_name', 'Unknown')
        engagement_label = reco_data.get('engagement_level_name', 'Unknown')
      else:
        method_label = "N/A"
        engagement_label = "N/A"

      # 3. Create a clean dictionary for the table
      # Keys here should match the headers you want to display
      processed_item = {
        "Student ID": row.get('id_student'),
        "Name": row.get('name_student', 'Unknown'),
        "Region": row.get('region', 'Unknown'),
        "Study Method": method_label,
        "Engagement": engagement_label
      }
      processed_list.append(processed_item)
        
    return processed_list

  def load_data(self, cluster_id: int, cluster_name: str):
    """
    Orchestrates the Fetch -> Process -> Load pipeline.
    """
    self.logger.info(f"Loading detail page for {cluster_name} (ID: {cluster_id})")
    self.ui.title_label.setText(f"Students in: {cluster_name}")

    # --- Step 1: Fetch Data (One Query) ---
    raw_data = StudentsLogic.get_students_by_cluster(cluster_id) or []

    # --- Step 2: Preprocess Data (Pure Logic) ---
    display_data = self._preprocess_student_data(raw_data)

    # --- Step 3: Load to Table (UI Manager) ---
    # We define the order of columns we want
    headers = ["Student ID", "Name", "Region", "Study Method", "Engagement"]
    
    self.table_manager.load_data(
        data=display_data, 
        header_labels=headers
    )
    
    self._clear_recommendation_area()

  def on_student_selected(self, item: QTableWidgetItem):
    """
    Fires when a student is clicked in the table.
    Populates the scroll area with their courses.
    """
    try:
      # Get the student_id from the clicked row (Column 0)
      student_id_item = self.ui.student_table.item(item.row(), 0)
      student_id = int(student_id_item.text())
      
      # 1. Clear the old recommendations
      self._clear_recommendation_area()
      
      # 2. Use your function from predict.py
      #
      reco = self.recommend_service.get_recommendation_for_student(student_id)
      
      if reco['status'] != 'success':
        # Show the error message from your service
        self.ui.recommendation_title_label.setText(reco['message'])
        return

      # 3. Set title and add new course labels
      self.ui.recommendation_title_label.setText(f"Recs for {student_id}")
      
      for course in reco['recommendations']:
        course_label = QLabel(f"• {course}")
        course_label.setWordWrap(True)
        course_label.setProperty("class", "course_label") # For styling
        self.ui.recommendation_layout.addWidget(course_label)
        
      # Add a spacer at the end to push them up
      self.ui.recommendation_layout.addStretch()

    except Exception as e:
      self.logger.error(f"Error in on_student_selected: {e}", exc_info=True)
      self._clear_recommendation_area()
      self.ui.recommendation_title_label.setText("Error loading courses.")

  def _clear_recommendation_area(self):
    """Clears all course labels from the scroll area."""
    layout = self.ui.recommendation_layout
    # Remove all widgets except the title label (at index 0)
    while layout.count() > 1:
      child = layout.takeAt(1) # Take item at index 1
      if child.widget():
        child.widget().deleteLater()
      elif child.spacerItem():
        layout.removeItem(child)
    # Set default text
    self.ui.recommendation_title_label.setText("Select a student to see recommendations")