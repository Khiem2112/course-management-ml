from ui.course_result import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow
from utils.logger import get_class_logger
class CourseResultEx(QMainWindow):
  
  def __init__(self):
    super().__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi()
  
    self.logger = get_class_logger(__name__, __class__.__name__)
  