import sys
import mysql.connector

from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QPushButton, QLabel)
from PyQt6.QtGui import QIcon, QPixmap
from Course.course import Ui_MainWindow
import resource_from_qt  # ⚡ file được sinh ra từ .qrc

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.current_page = 1
        self.per_page = 6
        self.courses = []

        # Gắn sự kiện
        self.ui.btn_next.clicked.connect(self.next_page)
        self.ui.btn_previous.clicked.connect(self.previous_page)

        # Lấy dữ liệu ban đầu
        self.load_courses_from_db()

        #import icon/images
        self.ui.brand.setPixmap(QPixmap(":/Images/images/Logo DUKI.png"))
        self.ui.menu_course.setIcon(QIcon(":/Icons/images/icons/Course/Course.png"))
        self.ui.menu_student.setIcon(QIcon(":/Icons/images/icons/Course/Student1.png"))
        self.ui.menu_analysis.setIcon(QIcon(":/Icons/images/icons/Course/Analysis.png"))
        self.ui.menu_payment.setIcon(QIcon(":/Icons/images/icons/Course/Payment.png"))
        self.ui.menu_logout.setIcon(QIcon(":/Icons/images/icons/Course/Log_Out.png"))
        self.ui.btn_filter.setIcon(QIcon(":/Icons/images/icons/Course/Filter1.png"))
        self.ui.btn_create.setIcon(QIcon(":/Icons/images/icons/Course/Create1.png"))
        self.ui.btn_next.setIcon(QIcon(":/Icons/images/icons/Course/ri-Photoroom.png"))
        self.ui.btn_previous.setIcon(QIcon(":/Icons/images/icons/Course/le-Photoroom.png"))
        self.ui.image_course_1.setPixmap(QPixmap(":/Images/images/course_image.png"))
        self.ui.image_course_2.setPixmap(QPixmap(":/Images/images/course_image.png"))
        self.ui.image_course_3.setPixmap(QPixmap(":/Images/images/course_image.png"))
        self.ui.image_course_4.setPixmap(QPixmap(":/Images/images/course_image.png"))
        self.ui.image_course_5.setPixmap(QPixmap(":/Images/images/course_image.png"))
        self.ui.image_course_6.setPixmap(QPixmap(":/Images/images/course_image.png"))
        self.ui.btn_search.setIcon(QIcon(":/Icons/images/icons/Course/magnifier.png"))

    # ---------------------- Kết nối MySQL ----------------------
    def connect_db(self):
        return mysql.connector.connect(
            host="tramway.proxy.rlwy.net",
            port=25079,
            user="root",
            password="CkjQqbvmmpblZmyrmLnlSEVAAURNRlRt",
            database="railway"
        )

    # ---------------------- Load dữ liệu ----------------------
    def load_courses_from_db(self):
        try:
            conn = self.connect_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT code_module, code_presentation, module_presentation_length
                FROM courses
                ORDER BY code_module, code_presentation;
            """)
            self.courses = cursor.fetchall()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            self.courses = []

        self.display_courses()

    # ---------------------- Hiển thị dữ liệu ----------------------
    def display_courses(self):
        total_pages = max(1, (len(self.courses) + self.per_page - 1) // self.per_page)
        self.current_page = min(self.current_page, total_pages)

        start = (self.current_page - 1) * self.per_page
        end = start + self.per_page
        data = self.courses[start:end]

        frames = [
            self.ui.course_1, self.ui.course_2, self.ui.course_3,
            self.ui.course_4, self.ui.course_5, self.ui.course_6
        ]

        for i in range(6):
            frame = frames[i]
            if i < len(data):
                course = data[i]
                getattr(self.ui, f"course_code_module{i+1}").setText(course["code_module"])
                getattr(self.ui, f"course_code_presentation{i+1}").setText(course["code_presentation"])
                getattr(self.ui, f"presentation{i+1}").setText(str(course["module_presentation_length"]))
                frame.show()
            else:
                frame.hide()

        self.update_pagination_buttons(total_pages)
        self.ui.btn_previous.setEnabled(self.current_page > 1)
        self.ui.btn_next.setEnabled(self.current_page < total_pages)

    # ---------------------- Tạo nút phân trang ----------------------
    def update_pagination_buttons(self, total_pages):
        layout = self.ui.pagination_layout.layout() if hasattr(self.ui.pagination_layout, 'layout') else self.ui.pagination_layout
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
                btn.clicked.connect(lambda _, p=page: self.go_to_page(p))

                # Style cho trang hiện tại
                if page == self.current_page:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2b6cb0;
                            color: white;
                            border: 2px solid #1a365d;
                            font-weight: bold;
                            border-radius: 6px;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e2e8f0;
                            color: black;
                            border-radius: 6px;
                        }
                        QPushButton:hover {
                            background-color: #cbd5e0;
                        }
                    """)

                layout.addWidget(btn)

    # ---------------------- Tính toán danh sách trang hiển thị ----------------------
    def get_visible_pages(self, total_pages):
        pages = []

        # Hiển thị toàn bộ nếu trang ít
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

    # ---------------------- Điều khiển chuyển trang ----------------------
    def go_to_page(self, page):
        self.current_page = page
        self.display_courses()

    def next_page(self):
        self.current_page += 1
        self.display_courses()

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_courses()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
