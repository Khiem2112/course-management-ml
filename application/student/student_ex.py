# In application/student_ex.py
import sys
from functools import partial
from PyQt6.QtWidgets import (
  QWidget, 
  QPushButton, 
  QLabel, 
  QTableWidgetItem, 
  QMessageBox, 
  QHBoxLayout,
  QFrame,
  QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ui.student_ui import Ui_MainWindow as StudentUI
from database.student.student_logic import StudentsLogic
from utils.table.table_manager import TableWidgetManager
from media.resource_from_qt import * # For icons
from utils.logger import get_class_logger

class StudentManagementEx: # <-- Note: Not inheriting from QWidget or QMainWindow
  def __init__(self, main_window: QWidget, ui: StudentUI):
    self.main_window = main_window # This is the StudentFrame (QWidget)
    self.ui = ui
    self.logger = get_class_logger(__name__, self.__class__.__name__)
    
    self.students = [] # Holds the FULL list of all students
    self.current_page = 1
    self.per_page = 15 # <-- YOU CAN CHANGE THIS: Students per page
    
    # --- 1. Load Icons ---
    # ** YOU MUST ADD YOUR ICON PATHS TO resource_from_qt.qrc **
    # and recompile it, or use file paths.
    self.edit_icon = QIcon(":/Icons/images/icons/Course_Student/update.png")
    self.delete_icon = QIcon(":/Icons/images/icons/Course_Student/delete.png")

    # --- 2. Instantiate Table Manager ---
    # ** CHANGE THIS to the objectName of your table in student.ui **
    #
    self.table_manager = TableWidgetManager(table_widget=self.ui.student_table)

    self.connect_signals()
    self.load_all_students()

  def load_all_students(self):
    """
    Fetches ALL students from the DB and displays the first page.
    """
    # NOTE: You must create this new function in StudentsLogic
    # It should return a list of dictionaries, e.g.,
    # [{'id_student': 1, 'gender': 'M', ...}, ...]
    self.students = StudentsLogic.get_all_students() or []
    
    self.current_page = 1
    self.display_current_page()

  def display_current_page(self):
    """
    Slices the full student list, loads data via TableManager,
    and then adds the action buttons.
    """
    if not self.students:
      self.ui.student_table.setRowCount(0)
      self.update_pagination_buttons(total_pages=1)
      return

    # 1. Calculate pagination
    total_students = len(self.students)
    total_pages = max(1, (total_students + self.per_page - 1) // self.per_page)
    self.current_page = min(self.current_page, total_pages)

    # 2. Slice the data
    start = (self.current_page - 1) * self.per_page
    end = start + self.per_page
    data_slice = self.students[start:end] # This is a list[dict]

    # 4. Load data using TableWidgetManager
    self.table_manager.load_data(
      data=data_slice
    )
    
    # 5. Add the action buttons (Edit/Delete)
    self._add_action_buttons(data_slice)

    # 6. Update pagination UI
    self.update_pagination_buttons(total_pages)
    
    # 7. Enable/Disable buttons
    self.ui.student_previous.setEnabled(self.current_page > 1)
    self.ui.student_next.setEnabled(self.current_page < total_pages)

  def _add_action_buttons(self, data_slice: list[dict]):
    """
    Adds 'Edit' and 'Delete' columns with buttons to the table
    *after* TableWidgetManager has populated the data.
    """
    table = self.ui.student_table
    
    # Get current column count (from data)
    data_col_count = table.columnCount()
    
    # Add two new columns
    table.setColumnCount(data_col_count + 2)
    
    # Set headers for the new columns
    table.setHorizontalHeaderItem(data_col_count, QTableWidgetItem("Edit"))
    table.setHorizontalHeaderItem(data_col_count + 1, QTableWidgetItem("Delete"))

    for row_index, student_record in enumerate(data_slice):
      # Get the student ID for this row
      student_id = student_record.get("id_student")
      
      # 1. Create Edit Button
      edit_btn = QPushButton(self.edit_icon, "")
      edit_btn.setToolTip(f"Edit student {student_id}")
      edit_btn.setFixedSize(28, 28) # Small square button
      edit_btn.clicked.connect(partial(self.on_edit_student, student_id))
      
      # 2. Create Delete Button
      delete_btn = QPushButton(self.delete_icon, "")
      delete_btn.setToolTip(f"Delete student {student_id}")
      delete_btn.setFixedSize(28, 28) # Small square button
      delete_btn.clicked.connect(partial(self.on_delete_student, student_id))
      
      # 3. Add buttons to cells
      # We must center buttons in the cell. We use a holder widget and layout.
      edit_widget = QWidget()
      edit_layout = QHBoxLayout(edit_widget)
      edit_layout.addWidget(edit_btn)
      edit_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
      edit_layout.setContentsMargins(0,0,0,0)
      table.setCellWidget(row_index, data_col_count, edit_widget)

      delete_widget = QWidget()
      delete_layout = QHBoxLayout(delete_widget)
      delete_layout.addWidget(delete_btn)
      delete_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
      delete_layout.setContentsMargins(0,0,0,0)
      table.setCellWidget(row_index, data_col_count + 1, delete_widget)
    
    table.resizeColumnsToContents()


  def connect_signals(self):
    """Connects the next/previous buttons."""
    try:
      # ** CHANGE THESE NAMES if they are different in your .ui file **
      #
      self.ui.student_previous.clicked.connect(self.previous_page)
      self.ui.student_next.clicked.connect(self.next_page)
      # Connect search/filter buttons if they exist
      # self.ui.student_search_button.clicked.connect(self.on_search)
    except AttributeError as e:
      self.logger.warning(f"Could not connect student pagination buttons: {e}")

  # --- Action Button Slots ---

  def on_edit_student(self, student_id: int):
    """Placeholder slot for the Edit button."""
    self.logger.info(f"REQUEST TO EDIT STUDENT: {student_id}")
    #
    # --- YOU WOULD ADD YOUR LOGIC HERE ---
    # 1. Fetch all details for this student_id
    # student_data = StudentsLogic.get_student_details(student_id)
    # 2. Create and show a new dialog/form (e.g., QDialog)
    # dialog = EditStudentDialog(student_data)
    # if dialog.exec():
    #   # 3. If dialog is saved, get new data and update DB
    #   new_data = dialog.get_data()
    #   StudentsLogic.update_student(student_id, new_data)
    #   # 4. Refresh the table
    #   self.load_all_students() 
    #
    QMessageBox.information(self.main_window, "Edit Student", f"Not implemented: Edit student {student_id}")

  def on_delete_student(self, student_id: int):
    """Slot for the Delete button."""
    self.logger.info(f"REQUEST TO DELETE STUDENT: {student_id}")
    
    reply = QMessageBox.warning(
      self.main_window, 
      "Delete Student", 
      f"Are you sure you want to permanently delete student {student_id}?",
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
      QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.Yes:
      self.logger.info(f"DELETING student {student_id}...")
      #
      # --- YOU WOULD ADD YOUR DB LOGIC HERE ---
      # success = StudentsLogic.delete_student(student_id)
      # if success:
      #   QMessageBox.information(self.main_window, "Success", "Student deleted.")
      #   self.load_all_students() # Refresh table
      # else:
      #   QMessageBox.critical(self.main_window, "Error", "Failed to delete student.")
      #
      # Placeholder for now:
      QMessageBox.information(self.main_window, "Delete", f"Not implemented: Delete student {student_id}")

  # --- PAGINATION LOGIC (Adapted from your CourseManagementEx) ---
  #

  def update_pagination_buttons(self, total_pages):
    """Dynamically creates the page number buttons."""
    # ** CHANGE THIS NAME if your layout widget is different in .ui file **
    #
    layout = self.ui.student_page.layout() 
    if layout is None:
      self.logger.error("UI element 'student_page' has no layout.")
      return

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
    self.current_page = page
    self.display_current_page()

  def next_page(self):
    self.current_page += 1
    self.display_current_page()

  def previous_page(self):
    self.current_page -= 1
    self.display_current_page()