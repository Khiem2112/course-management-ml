# In your application/course/course_student_ex.py file
from ui.course_assessment_ui import Ui_MainWindow as CourseAssessmentUI
from media.resource_from_qt import *
from PyQt6.QtWidgets import (QWidget, QMessageBox, QPushButton, QLabel, QMainWindow) # <-- CHANGED
from database.assessment.assessment_logic import AssessmentLogic
from utils.table.table_manager import TableWidgetManager
from functools import partial # <-- ADDED

# --- CRITICAL: Inherit from QWidget ---
class CourseAssessmentEx(QMainWindow):
  def __init__(self, parent=None): # <-- Add parent
    super().__init__(parent)     # <-- Call super() with parent
    self.ui = CourseAssessmentUI()
    self.ui.setupUi(self)
    
    self.students = [] # This holds the FULL list of students
    
    # --- 1. Add Pagination State ---
    self.current_page = 1
    self.per_page = 15 #
    
    # --- 2. Initialize Table Manager (do it once) ---
    # YOU MUST CHANGE 'self.ui.course_student_table'
    # to match the objectName of your QTableWidget in course_student.ui
    self.table_manager = TableWidgetManager(table_widget=self.ui.course_assessment_table)
    
    # --- 3. Connect Pagination Signals ---
    self.connect_signals()

  def load_data(self, code_module: str, code_presentation: str):
    """
    Main entry point. Fetches all students and displays the first page.
    """
    self.code_module = code_module
    self.code_presentation = code_presentation
    
    # 1. Fetch ALL students from the database
    self.students = AssessmentLogic.get_all_assessments_per_course(
      code_module=self.code_module,
      code_presentation=self.code_presentation
    ) or []
    
    # 2. Reset to page 1 and display
    self.current_page = 1
    self.display_current_page() # Call new display function

  def display_current_page(self):
    """
    Slices the full student list and loads the current page into the table.
    """
    if not self.students:
      self.table_manager.load_data(data=[]) # Clear table
      self.update_pagination_buttons(total_pages=1)
      return

    # 1. Calculate pagination
    total_students = len(self.students)
    total_pages = max(1, (total_students + self.per_page - 1) // self.per_page)
    self.current_page = min(self.current_page, total_pages)

    # 2. Slice the data
    start = (self.current_page - 1) * self.per_page
    end = start + self.per_page
    data_slice = self.students[start:end]

    # 3. Load the slice into the table
    self.table_manager.load_data(data=data_slice)
    
    # 4. Update pagination UI
    self.update_pagination_buttons(total_pages)
    
    # 5. Enable/Disable buttons
    self.ui.course_assessment_previous.setEnabled(self.current_page > 1)
    self.ui.course_assessment_next.setEnabled(self.current_page < total_pages)

  def connect_signals(self):
    """Connects the next/previous buttons."""
    try:
      # YOU MUST CHANGE these names to match your .ui file
      self.ui.course_assessment_previous.clicked.connect(self.previous_page)
      self.ui.course_assessment_next.clicked.connect(self.next_page)
    except AttributeError as e:
      print(f"Warning: Could not connect student pagination buttons: {e}")

  # --- PAGINATION LOGIC (Adapted from your CourseManagementEx) ---

  def update_pagination_buttons(self, total_pages):
    """Dynamically creates the page number buttons."""
    # that contains the layout for the page numbers.
    layout = self.ui.course_assessment_page.layout() 
    if layout is None:
      print(f"Error: UI element 'course_student_page' in {self.ui} has no layout.")
      return

    # Clear existing buttons
    while layout.count():
      item = layout.takeAt(0)
      if item.widget():
        item.widget().deleteLater()

    pages_to_show = self.get_visible_pages(total_pages)

    for page in pages_to_show:
      if page == "...":
        dots = QLabel("...")
        dots.setStyleSheet("color: gray; font-weight: bold; margin: 0 4px;")
        layout.addWidget(dots)
      else:
        btn = QPushButton(str(page))
        btn.setFixedSize(32, 32)
        btn.clicked.connect(partial(self.go_to_page, page))

        # Style the current page button
        if page == self.current_page:
          btn.setStyleSheet("""
            QPushButton {
              background-color: #2b6cb0; color: white;
              border: 2px solid #1a365d; font-weight: bold;
              border-radius: 6px;
            }
          """)
        else:
          btn.setStyleSheet("""
            QPushButton {
              background-color: #e2e8f0; color: black;
              border-radius: 6px;
            }
            QPushButton:hover { background-color: #cbd5e0; }
          """)
        layout.addWidget(btn)

  def get_visible_pages(self, total_pages):
    """Calculates which page numbers to show."""
    pages = []
    if total_pages <= 7:
      pages = list(range(1, total_pages + 1))
    else:
      if self.current_page <= 4:
        pages = [1, 2, 3, 4, 5, "...", total_pages]
      elif self.current_page >= total_pages - 3:
        pages = [1, "..."] + list(range(total_pages - 4, total_pages + 1))
      else:
        pages = [1, "...",
                 self.current_page - 1, self.current_page, self.current_page + 1,
                 "...", total_pages]
    return pages

  def go_to_page(self, page):
    """Navigates to a specific page number."""
    self.current_page = page
    self.display_current_page() # Re-display

  def next_page(self):
    """Navigates to the next page."""
    self.current_page += 1
    self.display_current_page() # Re-display

  def previous_page(self):
    """Navigates to the previous page."""
    self.current_page -= 1
    self.display_current_page() # Re-display