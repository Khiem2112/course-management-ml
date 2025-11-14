import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

# === IMPORT UI ===
from ui.course_ui import Ui_MainWindow as CourseUI
from ui.student_ui import Ui_MainWindow as StudentUI
from ui.payment_ui import Ui_MainWindow as PaymentUI
from ui.analysis_ui import Ui_MainWindow as AnalysisUI
from ui.cluster_analysis_ui import Ui_MainWindow as ClusterUI
from ui.course_result_ui import Ui_MainWindow as ResultUI
from ui.course_assessment_ui import Ui_MainWindow as AssessmentUI
from ui.course_student_ui import Ui_MainWindow as CourseStudentUI


# === TẠO FRAME CHO MỖI UI ===

class CourseFrame(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = CourseUI()
        self.ui.setupUi(self)


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


class ClusterFrame(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = ClusterUI()
        self.ui.setupUi(self)


class ResultFrame(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = ResultUI()
        self.ui.setupUi(self)


class AssessmentFrame(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = AssessmentUI()
        self.ui.setupUi(self)


class CourseStudentFrame(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = CourseStudentUI()
        self.ui.setupUi(self)


# === MAIN WINDOW CHÍNH ===
class MainApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hệ thống quản lý khóa học")

        # STACkED WIDGET
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # Khởi tạo 8 frame
        self.course_frame = CourseFrame()
        self.student_frame = StudentFrame()
        self.payment_frame = PaymentFrame()
        self.analysis_frame = AnalysisFrame()
        self.cluster_frame = ClusterFrame()
        self.result_frame = ResultFrame()
        self.assessment_frame = AssessmentFrame()
        self.course_student_frame = CourseStudentFrame()

        # Thêm vào stacked widget
        self.stacked.addWidget(self.course_frame)          # 0
        self.stacked.addWidget(self.student_frame)         # 1
        self.stacked.addWidget(self.payment_frame)         # 2
        self.stacked.addWidget(self.analysis_frame)        # 3
        self.stacked.addWidget(self.cluster_frame)         # 4
        self.stacked.addWidget(self.result_frame)          # 5
        self.stacked.addWidget(self.assessment_frame)      # 6
        self.stacked.addWidget(self.course_student_frame)  # 7

        self.stacked.setCurrentIndex(0)

        # Kết nối sidebar + header
        self.connect_sidebar()
        self.connect_header()

    # === SIDEBAR (menu_course, menu_student, …) ===
    def connect_sidebar(self):
        sidebar_map = {
            "menu_course": 0,
            "menu_student": 1,
            "menu_payment": 2,
            "menu_analysis": 3,
        }

        frames = [
            self.course_frame,
            self.student_frame,
            self.payment_frame,
            self.analysis_frame,
            self.cluster_frame,
            self.result_frame,
            self.assessment_frame,
            self.course_student_frame,
        ]

        for frame in frames:
            ui = frame.ui
            for btn_name, index in sidebar_map.items():
                if hasattr(ui, btn_name):
                    getattr(ui, btn_name).clicked.connect(lambda _, i=index: self.switch_to(i))

            if hasattr(ui, "menu_logout"):
                ui.menu_logout.clicked.connect(self.logout)


    # === HEADER (header_student, header_result, header_assessment) ===
    def connect_header(self):

        header_map = {
            "header_result": 5,
            "header_assessment": 6,
            "header_student": 7,  # Course Student PAGE
        }

        frames = [
            self.course_frame,
            self.student_frame,
            self.payment_frame,
            self.analysis_frame,
            self.cluster_frame,
            self.result_frame,
            self.assessment_frame,
            self.course_student_frame,
        ]

        for frame in frames:
            ui = frame.ui
            for btn_name, index in header_map.items():
                if hasattr(ui, btn_name):
                    getattr(ui, btn_name).clicked.connect(lambda _, i=index: self.switch_to(i))


    def switch_to(self, index):
        self.stacked.setCurrentIndex(index)

    def logout(self):
        QApplication.quit()


# === CHẠY APP ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainApp()
    win.show()
    sys.exit(app.exec())
