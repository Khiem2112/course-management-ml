from email.policy import Policy
import sys
import pandas as pd
import seaborn as sns
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QFrame, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# Assuming your Qt Designer file is named main_window.ui
# You would generate main_window_ui.py from it using 'pyuic6 main_window.ui -o main_window_ui.py'
from ui.home_page import Ui_MainWindow 

# Database
from database.student.student import get_student_score_per_course, get_top_5_highest_score_student

# Logger
from utils.logger import get_class_logger

# Plot
from utils.plot.student_score import create_score_distribution_plot

# ====================================================================
# 1. Matplotlib Canvas Class
# ====================================================================

class MplCanvas(FigureCanvas):
    """A standard Matplotlib canvas embedded in a QWidget."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Create a Figure object and an Axes object
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        
        # Initialize FigureCanvas base class
        super().__init__(fig)
        
        # Set the parent (optional, but good practice for organization)
        if parent:
            self.setParent(parent)

# ====================================================================
# 2. Main Application Window Class
# ====================================================================

class CourseManagementEx(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load the UI from the generated Python file
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logger = get_class_logger(__name__, __class__.__name__)

        # The canvas instance
        self.plot_canvas = None 
        
        # Initialize the canvas and plot the data
        self.init_plot_widget()
        self.make_window_expanded()
        self.load_student_score_distribution()
        self.set_initial_page()
    
    def init_plot_widget(self):
        """
        Creates a dedicated QVBoxLayout within the placeholder widget 
        and adds the MplCanvas to it.
        """
        # Create canvas
        self.plot_canvas = MplCanvas(parent=self.ui.plot_layout)
        self.plot_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Add the canvas to the layout, making it the sole occupant
        self.ui.plot_layout.addWidget(self.plot_canvas)    

    def load_and_plot_data(self):
        """Fetches data and draws the plot on the canvas."""
        
        # --- Data Loading (Replace with your database logic) ---
        data = {'scores': [65, 78, 82, 91, 55, 72, 88, 79, 68, 85, 95, 61]}
        df = pd.DataFrame(data)

        # --- Plotting ---
        # 1. Clear the previous plot (essential for updates)
        self.plot_canvas.axes.clear()

        # 2. Plot the new data using Seaborn on the canvas's axes
        sns.histplot(data=df, x='scores', kde=True, ax=self.plot_canvas.axes)

        # 3. Set titles and labels
        self.plot_canvas.axes.set_title('Average Score Distribution', fontsize=12)
        self.plot_canvas.axes.set_xlabel('Score')
        self.plot_canvas.axes.set_ylabel('Frequency')

        # 4. Redraw the canvas to update the display
        self.plot_canvas.draw()
        
    # Example method to show how to update the plot (e.g., connected to a button)
    
    def set_initial_page(self):
        self.ui.page_widget.setCurrentWidget(self.ui.course_page)
    
    def update_plot_on_button_click(self):
        print("Updating plot...")
        # Imagine fetching new data here...
        new_data = {'scores': [50, 60, 70, 80, 90, 100]}
        df_new = pd.DataFrame(new_data)
        
        self.plot_canvas.axes.clear()
        sns.histplot(data=df_new, x='scores', kde=True, ax=self.plot_canvas.axes, color='orange')
        self.plot_canvas.axes.set_title('Updated Distribution')
        self.plot_canvas.draw()
        
    
    def load_student_score_distribution(self):
        sample_data = get_student_score_per_course()
        create_score_distribution_plot(
            sample_data, 
            ax=self.plot_canvas.axes, # Pass the target axes
            title="Final Score Distribution - 2013J Module AAA"
        )
        
        # Tell the MplCanvas widget to redraw itself with the new content
        self.plot_canvas.draw()
    def make_window_expanded(self):
        self.ui.centralwidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ui.page_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def load_top5_student(self):
        pass
    def load_statistic_data(self):
        pass

# ====================================================================
# 3. Application Execution
# ====================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CourseManagementEx()
    window.show()
    sys.exit(app.exec()) 