import mysql.connector
from PyQt6.QtGui import QIcon, QPixmap
from media.resource_from_qt import *  # load Qt resources
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QPushButton, QLabel, QStackedWidget, QFrame, QWidget)
from database.connection_manager import DBConnectionManager
from database.execute_service import DBExecuteService
from ui.course_ui import Ui_MainWindow as CourseUI
from application.course.course_assessment import CourseAssessmentEx
from application.course.course_result import CourseResultEx
from application.course.course_student import CourseStudentEx
from base.widgets import ClickableFrame
from utils.logger import get_class_logger

from functools import partial


class CourseManagementEx():
    def __init__(self, 
                 main_window: QMainWindow,
                 ui: CourseUI
                 ):
        super().__init__()
        self.logger = get_class_logger(__name__,__class__.__name__)
        self.ui = ui
        self.main_window = main_window
        self.current_page = 1
        self.per_page = 6
        self.courses = []
        
        # Manage current course
        self.current_code_module: str = 'AAA'
        self.current_code_presentation: str = '2013J'
        
        self.page_stack = QStackedWidget()

        # 2. GET THE "COURSE LIST" PAGE (from the .ui file)
        self.course_list_page = self.ui.centralwidget
        
        # 3. CREATE THE "TAB" PAGE WIDGETS
        self.student_tab_page = CourseStudentEx()
        self.result_tab_page = CourseResultEx()
        self.assessment_tab_page = CourseAssessmentEx()

        # 4. ADD ALL 4 PAGES TO YOUR NEW STACK
        self.page_stack.addWidget(self.course_list_page)     # Index 0
        self.page_stack.addWidget(self.student_tab_page)   # Index 1
        self.page_stack.addWidget(self.result_tab_page)    # Index 2
        self.page_stack.addWidget(self.assessment_tab_page)  # Index 3

        # 5. SET THE STACK AS THE NEW CENTRAL WIDGET
        # This makes your QStackedWidget the main content of the CourseFrame
        self.main_window.setCentralWidget(self.page_stack)
        self.page_stack.setCurrentWidget(self.course_list_page)

        # self.setup_icons()
        self.connect_signals()
        self.load_courses_from_db()
        self.display_courses()
        self.logger.info(f"Current courses: {self.courses}")

        self.set_up_tab_pages()
        self.set_up_navigation_menus()
        
        
    # Convert QFrame
    def replace_frames_with_clickable(self):
        """
        Dynamically replaces the QFrames (course_1 to course_6) in the UI
        with our new ClickableFrame, preserving their content.
        """
        for i in range(1, 7):
            frame_name = f"course_{i}"
            original_frame: QFrame = getattr(self.ui, frame_name, None)
            
            if original_frame is None:
                continue

            # 1. Create a new ClickableFrame
            new_frame = ClickableFrame(original_frame.parentWidget())
            
            # 2. Copy properties
            new_frame.setObjectName(original_frame.objectName())
            new_frame.setGeometry(original_frame.geometry())
            new_frame.setAutoFillBackground(original_frame.autoFillBackground())
            new_frame.setStyleSheet(original_frame.styleSheet())
            new_frame.setFrameShape(original_frame.frameShape())
            new_frame.setFrameShadow(original_frame.frameShadow())
            
            # 3. Move the layout (and all children) from old frame to new frame
            layout = original_frame.layout()
            if layout:
                new_frame.setLayout(layout)
            
            # 4. Replace the old frame in its parent's layout
            parent_layout = original_frame.parentWidget().layout()
            if parent_layout:
                parent_layout.replaceWidget(original_frame, new_frame)
            
            # 5. Delete the old frame and update the UI reference
            original_frame.deleteLater()
            setattr(self.ui, frame_name, new_frame)
            
            # 6. Re-assign child references (like labels) to the new frame's scope
            # This is a bit of a hack, but UI-generated files need it
            for child in new_frame.findChildren(QWidget):
                child_name = child.objectName()
                if hasattr(self.ui, child_name):
                    setattr(self.ui, child_name, child)    

    # ---------------- CONNECT SIGNALS ----------------
    def connect_signals(self):
        self.replace_frames_with_clickable()
        self.ui.btn_next.clicked.connect(self.next_page)
        self.ui.btn_previous.clicked.connect(self.previous_page)
        
        for i in range(1, 7):
            course_button = getattr(self.ui, f"course_{i}")
            if course_button:
                course_button.clicked.connect(partial(self.on_course_clicked, i - 1))
        
    def on_course_clicked(self, index_on_page: int):
        """
        SLOT: Called when a course from the list is clicked.
        This is the main "drill-down" logic.
        """
        actual_index = (self.current_page - 1) * self.per_page + index_on_page
        
        if actual_index < len(self.courses):
            course_info = self.courses[actual_index]
            
            # 1. Store the course "state"
            self.current_code_module = course_info['code_module']
            self.current_code_presentation = course_info['code_presentation']
            
            # 2. Load data into ALL tab pages
            self.student_tab_page.load_data(self.current_code_module, self.current_code_presentation)
            self.result_tab_page.load_data(self.current_code_module, self.current_code_presentation)
            self.assessment_tab_page.load_data(self.current_code_module, self.current_code_presentation)
            
            # 3. Switch view to the default tab (Student List, Index 1)
            self.page_stack.setCurrentIndex(1)
    
    def set_up_tab_pages(self):        

        # Connect signals for ALL 3 TAB PAGES in a loop
        
        # This list holds the "pages" you want to navigate between
        tab_pages = [
            self.student_tab_page,   # Index 1 in page_stack
            self.result_tab_page,    # Index 2 in page_stack
            self.assessment_tab_page # Index 3 in page_stack
        ]

        # Gán hành vi cho tất cả menu "header" của từng trang tab
        for page in tab_pages:
            try:
                # Get the ui object from the page instance
                ui = page.ui 
                
                # Connect the buttons to the slots in this class
                ui.header_student.clicked.connect(lambda: self.switch_to(1))
                ui.header_result.clicked.connect(lambda: self.switch_to(2))
                ui.header_assessment.clicked.connect(lambda: self.switch_to(3))
                ui.header_return.clicked.connect(lambda: self.switch_to(0))
            except AttributeError as e:
                self.logger.warn(f"Warning: Could not connect header buttons for {page.__class__.__name__}. {e}")
    
    def set_up_navigation_menus(self):
        frames = [
            self.student_tab_page,
            self.result_tab_page,
            self.assessment_tab_page
        ]

        # Gán hành vi cho tất cả menu của từng frame
        for frame in frames:
            ui = frame.ui
            ui.menu_course.clicked.connect(lambda: self.ui.menu_course.click())
            ui.menu_student.clicked.connect(lambda: self.ui.menu_student.click())
            ui.menu_payment.clicked.connect(lambda: self.ui.menu_payment.click())
            ui.menu_analysis.clicked.connect(lambda: self.ui.menu_analysis.click())
            ui.menu_logout.clicked.connect(lambda: self.ui.menu_logout.click())
    
    def switch_to(self, index: int):
        """Chuyển tab theo index"""
        self.page_stack.setCurrentIndex(index)
    
    def set_up_course_children_page(self):
        pass
    
    def connect_course_bar(self):
        pass
    
    def load_courses_from_db(self):
        query = """
            SELECT name_course, code_module, code_presentation, module_presentation_length
            FROM courses 
            ORDER BY code_module, code_presentation;
        """
        self.courses = DBExecuteService.fetch_all(query) or []

    # ---------------- DISPLAY DATA ----------------
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
                getattr(self.ui, f"course_code_module{i + 1}").setText(course["name_course"])
                getattr(self.ui, f"course_code_presentation{i + 1}").setText(course["code_presentation"])
                getattr(self.ui, f"presentation{i + 1}").setText(str(course["module_presentation_length"]))
                frame.show()
            else:
                frame.hide()

        # self.update_pagination_buttons(total_pages)
        self.ui.btn_previous.setEnabled(self.current_page > 1)
        self.ui.btn_next.setEnabled(self.current_page < total_pages)


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
        self.current_page -= 1
        self.display_courses()
