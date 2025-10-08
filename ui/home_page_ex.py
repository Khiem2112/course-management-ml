import sys
import pandas as pd
import seaborn as sns
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QFrame
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Assuming your Qt Designer file is named main_window.ui
# You would generate main_window_ui.py from it using 'pyuic6 main_window.ui -o main_window_ui.py'
from ui.home_page import Ui_MainWindow 

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

        # The canvas instance
        self.plot_canvas = None 
        
        # Initialize the canvas and plot the data
        self.init_plot_widget()
        self.load_and_plot_data()
        self.ui.pushButton.clicked.connect(self.update_plot_on_button_click)

    def init_plot_widget(self):
        """
        Creates a dedicated QVBoxLayout within the placeholder widget 
        and adds the MplCanvas to it.
        """
        # CRITICAL STEP: Access the placeholder widget created in Qt Designer
        # Assume the placeholder QFrame/QWidget is named 'plot_container' in your .ui file
        plot_container: QFrame = self.ui.plot_container_2 
        
        # Create a layout manager specifically for the container
        plot_layout = QVBoxLayout(plot_container)
        
        # Remove margins/spacing so the plot fills the container perfectly
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setSpacing(0)

        # Create the canvas object
        # We don't set width/height here; the QVBoxLayout will manage its size.
        self.plot_canvas = MplCanvas(plot_container)
        
        # Add the canvas to the layout, making it the sole occupant
        plot_layout.addWidget(self.plot_canvas)

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
    def update_plot_on_button_click(self):
        print("Updating plot...")
        # Imagine fetching new data here...
        new_data = {'scores': [50, 60, 70, 80, 90, 100]}
        df_new = pd.DataFrame(new_data)
        
        self.plot_canvas.axes.clear()
        sns.histplot(data=df_new, x='scores', kde=True, ax=self.plot_canvas.axes, color='orange')
        self.plot_canvas.axes.set_title('Updated Distribution')
        self.plot_canvas.draw()


# ====================================================================
# 3. Application Execution
# ====================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CourseManagementEx()
    window.show()
    sys.exit(app.exec())