import sys
from PyQt6.QtWidgets import QMainWindow, QApplication
from ui.home_page_ex import CourseManagementEx
from ui.home_page import Ui_MainWindow

if __name__ == "__main__":
  app = QApplication(sys.argv)
  course_management = CourseManagementEx()
  course_management.show()
  sys.exit(app.exec())
  