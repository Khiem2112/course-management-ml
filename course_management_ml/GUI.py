import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ui.course_ui import Ui_MainWindow as CourseUI
from ui.student_ui import Ui_MainWindow as StudentUI
from ui.payment_ui import Ui_MainWindow as PaymentUI
from ui.analysis_ui import Ui_MainWindow as AnalysisUI
from application.course_ex import CourseManagementEx

# ====== FRAME CHO MỖI UI ======
class CourseFrame(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = CourseUI()
        self.ui.setupUi(self)
        self.logic = CourseManagementEx(self.ui)

class StudentFrame(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = StudentUI()
        self.ui.setupUi(self)


class PaymentFrame(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = PaymentUI()
        self.ui.setupUi(self)


class AnalysisFrame(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = AnalysisUI()
        self.ui.setupUi(self)

# ====== MAIN WINDOW CHÍNH ======
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hệ thống quản lý khóa học")

        # Tạo stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Tạo các frame con
        self.course_frame = CourseFrame(self)
        self.student_frame = StudentFrame(self)
        self.payment_frame = PaymentFrame(self)
        self.analysis_frame = AnalysisFrame(self)

        # Thêm frame vào stacked widget
        self.stacked_widget.addWidget(self.course_frame)   # index 0
        self.stacked_widget.addWidget(self.student_frame)  # index 1
        self.stacked_widget.addWidget(self.payment_frame)  # index 2
        self.stacked_widget.addWidget(self.analysis_frame) # index 3

        # Mặc định mở tab "Course"
        self.stacked_widget.setCurrentIndex(0)

        # Gắn sự kiện cho menu
        self.connect_menus()

    def connect_menus(self):
        """Kết nối 4 nút menu giữa các frame"""
        frames = [
            self.course_frame,
            self.student_frame,
            self.payment_frame,
            self.analysis_frame
        ]

        # Gán hành vi cho tất cả menu của từng frame
        for frame in frames:
            ui = frame.ui
            ui.menu_course.clicked.connect(lambda: self.switch_to(0))
            ui.menu_student.clicked.connect(lambda: self.switch_to(1))
            ui.menu_payment.clicked.connect(lambda: self.switch_to(2))
            ui.menu_analysis.clicked.connect(lambda: self.switch_to(3))
            ui.menu_logout.clicked.connect(self.logout)

    def switch_to(self, index: int):
        """Chuyển tab theo index"""
        self.stacked_widget.setCurrentIndex(index)

    def logout(self):
        """Thoát ứng dụng"""
        QApplication.quit()


# ====== CHẠY APP ======
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
