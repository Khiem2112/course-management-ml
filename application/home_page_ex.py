# application/home_page_ex.py

import sys
from typing import Optional # Import Optional for type hinting
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout

from ui.home_page import Ui_MainWindow
from database.student.student import get_student_score_per_course
from utils.logger import get_class_logger

# --- Import ONLY PlotManager (factory/controller class) ---
# MplCanvas is managed internally by PlotManager's static methods
from utils.plot.plot_manager import PlotManager

# ====================================================================
# Main Application Window Class (Using PlotManager Statics - Simplified)
# ====================================================================

class CourseManagementEx(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logger = get_class_logger(__name__, self.__class__.__name__)
        self.logger.info("Initializing CourseManagementEx window...")

        # --- No attribute to hold the display canvas ---
        # The MplCanvas existence is managed by PlotManager static methods

        # --- Load Initial Data and Set UI State ---
        self.load_student_score_distribution() # Load initial plot
        self.set_initial_page()

        # --- Connect Signals ---
        # Example: Connect a hypothetical button to update the plot
        # try:
        #     self.ui.update_plot_button.clicked.connect(self.update_plot_on_button_click)
        # except AttributeError: pass # Button might not exist

        self.logger.info("CourseManagementEx initialization complete.")

    # Removed _setup_plot_canvas method

    def set_initial_page(self):
        """Sets the currently visible page in the QStackedWidget."""
        try:
            self.ui.page_widget.setCurrentWidget(self.ui.course_page)
            self.logger.debug("Set initial page to 'course_page'.")
        except AttributeError:
            self.logger.error("UI elements 'page_widget' or 'course_page' not found.")
        except Exception as e:
            self.logger.error(f"Error setting initial page: {e}", exc_info=True)


    def load_student_score_distribution(self):
        """Fetches score data and uses PlotManager static method to draw the plot."""
        # Target the specific QWidget container holding the canvas
        target_widget = self.ui.verticalLayoutWidget
        if not target_widget:
             self.logger.error("Target widget 'verticalLayoutWidget' for plot not found. Cannot load score distribution.")
             return # Cannot proceed without the container

        self.logger.info("Loading student score distribution plot...")
        try:
            # 1. Fetch data
            score_data = get_student_score_per_course()
            self.logger.debug(f"Fetched {len(score_data) if score_data else 0} score records.")

            # 2. Call the PlotManager static method, passing the TARGET WIDGET and data
            #    This method finds/creates canvas, clears, plots, and redraws.
            plot_instance = PlotManager.create_score_distribution(target_widget, score_data)

            # 3. Optionally use the returned instance for immediate configuration
            if plot_instance and plot_instance.has_plot:
                plot_instance.set_title("Student Average Score Distribution (Final Title)") # Example config
                self.logger.info("Score distribution plot created and configured.")
            elif plot_instance: # Plot instance exists but has_plot is false (e.g., "No Data" or "Error")
                self.logger.warning("Plot generated, but indicates no data or an error state (check plot title).")
            # No 'else' needed as static method should always return a PlotManager instance

        except Exception as e:
            self.logger.error(f"Error during score distribution loading/plotting: {e}", exc_info=True)
            # Attempt to display an error message on the plot area via PlotManager.clear
            try:
                if target_widget: # Check again if target_widget exists
                    PlotManager.clear(target_widget).set_title("Error Loading Data")
            except Exception as clear_err:
                 self.logger.error(f"Failed to clear plot after error: {clear_err}", exc_info=True)


    def clear_current_plot(self):
        """Clears the plot currently shown in the designated container using PlotManager."""
        target_widget = self.ui.verticalLayoutWidget
        if not target_widget:
             self.logger.error("Target widget 'verticalLayoutWidget' for plot not found. Cannot clear plot.")
             return

        self.logger.info(f"Clearing current plot display in '{target_widget.objectName()}' via PlotManager.")
        PlotManager.clear(target_widget) # Use the static clear method

    # --- Example Update Function ---
    def update_plot_on_button_click(self):
         """Example handler to load/reload the score distribution plot."""
         self.logger.info("Update plot button clicked, reloading score distribution.")
         self.load_student_score_distribution() # Reloads using the static method


    # --- Placeholder methods ---
    def load_top5_student(self):
        self.logger.warning("load_top5_student method not yet implemented.")
        pass

    def load_statistic_data(self):
        self.logger.warning("load_statistic_data method not yet implemented.")
        pass

# ====================================================================
# Application Execution
# ====================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CourseManagementEx()
    window.show()
    sys.exit(app.exec())

