# In a new file, e.g., application/course/base_course_tab.py
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget

class BaseCourseTabPage(QWidget, ABC):
    """
    This is the interface (Abstract Base Class) for all pages
    that act as a "tab" within the course detail section.
    
    It guarantees that every tab *must* implement a load_data method.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 'ui' will be defined by the subclass
        self.ui = None 
    
    @abstractmethod
    def load_data(self, code_module: str, code_presentation: str):
        """
        This method is required by all subclasses. It will be called
        by CourseManagementEx when a new course is selected.

        Args:
            code_module (str): The course module code (e.g., 'AAA').
            code_presentation (str): The course presentation code (e.g., '2013J').
        """
        pass