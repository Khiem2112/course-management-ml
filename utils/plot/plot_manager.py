# utils/plot/plot_manager.py

from __future__ import annotations
from typing import Optional

from PyQt6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import pandas as pd
import seaborn as sns
from utils.logger import get_class_logger
import scienceplots
import matplotlib.pyplot as plt
import numpy as np

# ====================================================================
# 1. Matplotlib Canvas Class (Display Widget)
# (This class is correct, no changes needed)
# ====================================================================
class MplCanvas(FigureCanvas):
  """
  A Qt Widget that embeds and displays a Matplotlib Figure.
  Plotting is done directly onto its 'axes' attribute.
  """
  logger = get_class_logger(__name__, "MplCanvas")

  def __init__(self, parent: Optional[QWidget] = None, width: int = 5, height: int = 4, dpi: int = 100):
    try:
      self.figure: Figure = Figure(figsize=(width, height), dpi=dpi)
      self.axes: Axes = self.figure.add_subplot(111)
      super().__init__(self.figure)

      if parent:
        self.setParent(parent)

      self.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding
      )
      self.updateGeometry()
      self._is_empty: bool = True
    except Exception as e:
      MplCanvas.logger.error(f"Failed to initialize MplCanvas: {e}", exc_info=True)
      self.figure, self_axes = plt.subplots(); plt.close(self.figure)
      self.axes = self_axes

  def clear_display(self):
    """Clears the axes, resets properties, and redraws the canvas."""
    try:
      self.axes.clear()
      self.axes.set_title("")
      self.axes.set_xlabel("")
      self.axes.set_ylabel("")
      self.axes.grid(False)
      if self.figure.legends:
        self.figure.legends.clear()
      self._is_empty = True
      self.draw_idle()
    except Exception as e:
      MplCanvas.logger.error(f"Failed to clear canvas: {e}", exc_info=True)

# ====================================================================
# 2. PlotManager Class (Controller/Wrapper)
# --- THIS IS THE CORRECTED CLASS ---
# ====================================================================
class PlotManager:
  """
  A controller class that manages plotting operations on a target
  MplCanvas widget.
  """
  logger = get_class_logger(__name__, "PlotManager")

  # --- FIX 1: __init__ now accepts the MplCanvas ---
  def __init__(self, canvas: MplCanvas):
    """
    Initializes the PlotManager to control a specific MplCanvas.
    """
    self.canvas: MplCanvas = canvas
    self.figure: Figure = canvas.figure
    self.axes: Axes = canvas.axes
    self.has_plot: bool = not canvas._is_empty

  # --- FIX 2: draw() now calls the canvas.draw_idle() ---
  def draw(self) -> PlotManager:
    """
    Redraws the associated canvas to show any changes.
    """
    try:
      self.canvas.draw_idle()
      self.has_plot = not self.canvas._is_empty
    except Exception as e:
      PlotManager.logger.error(f"Failed to draw canvas: {e}", exc_info=True)
    return self

  def clear_plot(self) -> PlotManager:
    """Clears the axes of the managed canvas."""
    try:
      self.axes.clear()
      self.canvas._is_empty = True
      # We don't draw here; the plotting function will call draw()
    except Exception as e:
      PlotManager.logger.error(f"Failed to clear plot: {e}", exc_info=True)
    return self

  def set_title(self, title: str, fontsize: int = 12) -> PlotManager:
    try:
      self.axes.set_title(title, fontsize=fontsize)
    except Exception as e:
      PlotManager.logger.warning(f"Failed to set title: {e}")
    return self
  
  # --- STATIC METHODS (Factory/Constructors) ---

  @staticmethod
  def _find_or_create_canvas(target_widget: QWidget) -> MplCanvas | None:
    """
    Finds the MplCanvas within target_widget, or creates one.
    This method ensures the canvas is part of the layout.
    """
    if not target_widget:
      PlotManager.logger.error("Target widget is None. Cannot find or create canvas.")
      return None

    try:
      # 1. Try to find an existing canvas
      canvas = target_widget.findChild(MplCanvas)
      if canvas:
        PlotManager.logger.debug(f"Found existing canvas in '{target_widget.objectName()}'.")
        return canvas

      # 2. If no canvas, create one
      PlotManager.logger.info(f"No canvas found in '{target_widget.objectName()}'. Creating new one.")
      new_canvas = MplCanvas(parent=target_widget)
      
      # 3. Add the new canvas to the target widget's layout
      layout = target_widget.layout()
      if layout is None:
        PlotManager.logger.info(f"Target '{target_widget.objectName()}' has no layout. Creating new QVBoxLayout.")
        layout = QVBoxLayout(target_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        target_widget.setLayout(layout) # Set the new layout on the widget
        
      layout.addWidget(new_canvas)
      return new_canvas

    except Exception as e:
      PlotManager.logger.error(f"Error finding/creating canvas in '{target_widget.objectName()}': {e}", exc_info=True)
      return None

  @staticmethod
  def get_or_create(target_widget: QWidget) -> PlotManager:
    """
    Gets a PlotManager instance for the canvas inside target_widget.
    Creates the canvas if it doesn't exist.
    """
    canvas = PlotManager._find_or_create_canvas(target_widget)
    if canvas:
      # --- FIX 3: Return a manager that holds the *canvas* ---
      return PlotManager(canvas)
    else:
      PlotManager.logger.error(f"Could not create PlotManager for '{target_widget.objectName()}'.")
      # Return a dummy manager to prevent crashes
      dummy_canvas = MplCanvas()
      dummy_canvas.axes.text(0.5, 0.5, "Error: Plot widget missing", ha='center')
      return PlotManager(dummy_canvas)

  @staticmethod
  def clear(target_widget: QWidget) -> PlotManager:
    """
    Clears the plot on the canvas inside target_widget.
    """
    canvas = PlotManager._find_or_create_canvas(target_widget)
    if canvas:
      PlotManager.logger.info(f"Clearing plot on canvas within '{target_widget.objectName()}'.")
      canvas.clear_display()
      # --- FIX 4: Return a manager that holds the *canvas* ---
      return PlotManager(canvas)
    else:
      PlotManager.logger.error(f"Could not find or create canvas in '{target_widget.objectName()}' to clear.")
      dummy_canvas = MplCanvas()
      dummy_canvas.axes.text(0.5, 0.5, "Error: Plot widget missing", ha='center')
      return PlotManager(dummy_canvas)