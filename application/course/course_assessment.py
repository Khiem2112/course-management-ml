from ui.course_assessment_ui import Ui_MainWindow as CourseAssessmentUI
import mysql.connector
from media.resource_from_qt import *  # load Qt resources
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QPushButton, QLabel)
from database.connection_manager import DBConnectionManager
from database.execute_service import DBExecuteService
from ui.course_ui import Ui_MainWindow as CourseUI

class CourseAssessmentEx(QMainWindow):
  def __init__(self):
    super().__init__()
    self.ui = CourseAssessmentUI()
    self.ui.setupUi(self)
  def load_data(self, code_module: str, code_presentation: str):
    pass
  
