from ui.course_result import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget
from utils.logger import get_class_logger
from database.course.course import get_n_highest_score_student, get_dropout_percentage
from database.student.student import get_student_score_per_course
from utils.plot.plot_manager import PlotManager
from utils.plot.student_score import StudentScoreVisualizer
from utils.plot.course import CourseInfoVisualizer

class CourseResultEx(QMainWindow):
  
  def __init__(self):
    super().__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
  
    self.logger = get_class_logger(__name__, __class__.__name__)
    self.pre_run_the_page()
    
    
  def pre_run_the_page(self):
    self.visualize_student_score_distibution()
    self.show_top_5_students()
    self.visualize_drop_out_rate()
  
  def connect_all(self):
    
    pass
    
  def visualize_student_score_distibution(self):
    target_widget = self.ui.line_chart
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
      plot_instance = StudentScoreVisualizer.create_score_distribution(target_widget, score_data)

      # 3. Optionally use the returned instance for immediate configuration
      if plot_instance and plot_instance.has_plot:
        plot_instance.set_title("Student Average Score Distribution") # Example config
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
# ...existing code...
  def show_top_5_students(self):
    """
    Fill the existing UI labels course_result_1 .. course_result_5 with
    "rank. Name — score" using get_n_highest_score_student.
    """
    try:
      top5_frame = getattr(self.ui, "course_result_top5", None)
      if top5_frame is None:
        self.logger.error("UI does not have 'course_result_top5' frame. Cannot load top-5 students.")
        return

      students = get_n_highest_score_student(code_module='AAA',
                                             code_presentation='2013J',
                                             n=5) or []
      self.logger.debug(f"Fetched {len(students)} top student records.")

      def _get_field(obj, keys):
        if obj is None:
          return None
        if isinstance(obj, dict):
          for k in keys:
            if k in obj and obj[k] is not None:
              return obj[k]
        else:
          for k in keys:
            if hasattr(obj, k):
              val = getattr(obj, k)
              if val is not None:
                return val
        return None
      for idx in range(5):
        i = idx + 1
        label = getattr(self.ui, f"course_result_{i}", None)
        if label is None:
          if idx == 0:
            self.logger.warning("Expected labels course_result_1..course_result_5 not found in UI.")
          continue

        student = students[idx] if idx < len(students) else None

        # Resolve name
        name = _get_field(student, ["id_student"])
        if not name:
          name = "No student"

        # Resolve score
        score = _get_field(student, ["avg_student_score"])
        score_text = f"{score}" if score is not None else "-"

        # Compose and set label text: "1. Name — score"
        label.setText(f"{i}. {name} \u2014 {score_text} points")

      self.logger.info("Top-5 student labels populated.")

    except Exception as e:
      self.logger.error(f"Failed to load top-5 students: {e}", exc_info=True)
    
  def show_course_statistic_info(self):
    pass
  
  def visualize_drop_out_rate(self):
    data = get_dropout_percentage(code_module='AAA',code_presentation='2013J')
    plot_manager = CourseInfoVisualizer.create_dropout_rate_pie(data=data, target_widget=self.ui.pie_chart)
    plot_manager.set_title("Dropout/Retention Rate")
    