# utils/plot/plot_manager.py

from __future__ import annotations # Allow type hinting PlotManager within the class
from typing import Optional

from PyQt6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout # Added QVBoxLayout
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
# ====================================================================
class MplCanvas(FigureCanvas):
    """
    A Qt Widget that embeds and displays a Matplotlib Figure.
    Plotting is done directly onto its 'axes' attribute.
    """
    logger = get_class_logger(__name__, "MplCanvas") # Logger for the canvas itself

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
            self._is_empty = True
            self.clear_display() # Start in a clean state
            MplCanvas.logger.debug("MplCanvas initialized successfully.")
        except Exception as e:
            MplCanvas.logger.error(f"Error during MplCanvas initialization: {e}", exc_info=True)
            # Handle error state, maybe prevent widget from being fully functional
            # For simplicity, we'll let it potentially fail to draw later


    def clear_display(self):
        """Clears the axes, displays an empty state message, and redraws."""
        try:
            self.axes.clear()
            self.axes.set_title("Plot Area") # Generic title for empty state
            self.axes.set_xticks([])
            self.axes.set_yticks([])
            self.figure.canvas.draw_idle() # Use draw_idle for efficiency
            self._is_empty = True
            MplCanvas.logger.debug("MplCanvas display cleared.")
        except Exception as e:
            MplCanvas.logger.error(f"Error clearing MplCanvas display: {e}", exc_info=True)

    @property
    def is_empty(self) -> bool:
        """Returns True if the canvas is cleared or hasn't displayed a plot."""
        try:
             # Check if axes contains lines, collections, patches etc.
            return not bool(self.axes.has_data())
        except Exception:
             return True # Assume empty if error occurs during check


# ====================================================================
# 2. Plot Manager Class (Plotting Controller & Configurator)
# ====================================================================
class PlotManager:
    """
    Provides static methods to find/create an MplCanvas within a target QWidget,
    create plots directly on that canvas, and return an instance referencing
    the plotted axes for further configuration.
    """
    logger = get_class_logger(__name__, "PlotManager") # Class level logger

    def __init__(self, figure: Figure, axes: Axes):
        """
        Initializes the PlotManager, referencing the Figure and Axes
        where a plot was just drawn by a static method.

        Args:
            figure: The Matplotlib Figure containing the plot.
            axes: The Matplotlib Axes containing the plot.
        """
        if not isinstance(figure, Figure) or not isinstance(axes, Axes):
            PlotManager.logger.error(f"Initialization failed: Invalid types for figure ({type(figure)}) or axes ({type(axes)}).")
            raise TypeError("PlotManager requires valid Matplotlib Figure and Axes objects.")

        self.figure: Figure = figure
        self.axes: Axes = axes
        PlotManager.logger.debug(f"PlotManager instance created referencing axes with title: '{axes.get_title()}'")

    # --- Configuration Methods (Operate on the referenced Axes) ---
    # These methods modify the plot *after* a static method has drawn it.

    def set_title(self, title: str, **kwargs) -> PlotManager:
        """Sets the title of the referenced plot and redraws the canvas."""
        try:
            self.axes.set_title(title, **kwargs)
            if self.figure.canvas: # Check if canvas exists
                self.figure.canvas.draw_idle()
            PlotManager.logger.debug(f"Plot title set to: '{title}'")
        except Exception as e:
            PlotManager.logger.error(f"Error setting title: {e}", exc_info=True)
        return self # Allow chaining

    def set_xlabel(self, label: str, **kwargs) -> PlotManager:
        """Sets the label for the X-axis of the referenced plot and redraws."""
        try:
            self.axes.set_xlabel(label, **kwargs)
            if self.figure.canvas:
                self.figure.canvas.draw_idle()
            PlotManager.logger.debug(f"Plot xlabel set to: '{label}'")
        except Exception as e:
            PlotManager.logger.error(f"Error setting xlabel: {e}", exc_info=True)
        return self

    def set_ylabel(self, label: str, **kwargs) -> PlotManager:
        """Sets the label for the Y-axis of the referenced plot and redraws."""
        try:
            self.axes.set_ylabel(label, **kwargs)
            if self.figure.canvas:
                self.figure.canvas.draw_idle()
            PlotManager.logger.debug(f"Plot ylabel set to: '{label}'")
        except Exception as e:
            PlotManager.logger.error(f"Error setting ylabel: {e}", exc_info=True)
        return self

    def apply_grid(self, visible: bool = True, **kwargs) -> PlotManager:
        """Applies or removes a grid on the referenced plot and redraws."""
        try:
            self.axes.grid(visible, **kwargs)
            if self.figure.canvas:
                self.figure.canvas.draw_idle()
            PlotManager.logger.debug(f"Plot grid visibility set to: {visible}")
        except Exception as e:
            PlotManager.logger.error(f"Error applying grid: {e}", exc_info=True)
        return self

    def add_legend(self, **kwargs) -> PlotManager:
        """Adds a legend to the referenced plot if applicable and redraws."""
        try:
            handles, labels = self.axes.get_legend_handles_labels()
            if handles or labels:
                self.axes.legend(**kwargs)
                if self.figure.canvas:
                    self.figure.canvas.draw_idle()
                PlotManager.logger.debug("Plot legend added.")
            else:
                PlotManager.logger.warning("No labeled artists found for legend.")
        except Exception as e:
            PlotManager.logger.error(f"Error adding legend: {e}", exc_info=True)
        return self

    # --- State Property ---

    @property
    def has_plot(self) -> bool:
        """Returns True if the referenced Axes contain plotted data."""
        try:
            return bool(self.axes.has_data())
        except Exception:
             PlotManager.logger.warning("Error checking axes data state.", exc_info=True)
             return False # Assume no plot if error occurs

    # --- Helper to Find or Create Canvas ---

    @staticmethod
    def _find_or_create_canvas(target_widget: QWidget) -> Optional[MplCanvas]:
        """
        Finds an existing MplCanvas within the target widget or creates/adds one.
        Assumes the target_widget should ONLY contain the MplCanvas.
        """
        if not isinstance(target_widget, QWidget):
            PlotManager.logger.error("_find_or_create_canvas requires a QWidget instance.")
            return None

        # Attempt to find an existing MplCanvas child
        canvas = target_widget.findChild(MplCanvas)
        if isinstance(canvas, MplCanvas):
            PlotManager.logger.debug(f"Found existing MplCanvas in '{target_widget.objectName()}'.")
            return canvas
        else:
             PlotManager.logger.debug(f"No MplCanvas found in '{target_widget.objectName()}', attempting to create.")

        # If not found, create a new one and add it
        try:
            # Check for existing layout
            layout = target_widget.layout()
            if not layout:
                # Create a layout if one doesn't exist
                layout = QVBoxLayout(target_widget)
                layout.setContentsMargins(0, 0, 0, 0)
                target_widget.setLayout(layout)
                PlotManager.logger.debug(f"Created new QVBoxLayout for '{target_widget.objectName()}'.")
            else:
                 # If layout exists, clear it assuming it's dedicated to the plot
                 # WARNING: This will remove any other widgets in that layout!
                 if layout.count() > 0:
                     PlotManager.logger.warning(f"Clearing existing content of layout in '{target_widget.objectName()}' before adding canvas.")
                     while layout.count():
                         item = layout.takeAt(0)
                         widget = item.widget()
                         if widget:
                             widget.deleteLater() # Schedule deletion

            # Create and add the canvas
            new_canvas = MplCanvas(parent=target_widget)
            layout.addWidget(new_canvas)
            PlotManager.logger.info(f"Created and added new MplCanvas to '{target_widget.objectName()}'.")
            return new_canvas

        except Exception as e:
            PlotManager.logger.error(f"Failed to create or add MplCanvas to '{target_widget.objectName()}': {e}", exc_info=True)
            return None


    # --- Static Plotting & Clearing Methods ---

    @staticmethod
    def clear(target_widget: QWidget) -> PlotManager:
        """
        Finds/Creates the MplCanvas in target_widget and clears its display.

        Args:
            target_widget: The QWidget containing (or intended to contain) the MplCanvas.

        Returns:
            A PlotManager instance referencing the cleared canvas's axes.
        """
        canvas = PlotManager._find_or_create_canvas(target_widget)
        if canvas:
            PlotManager.logger.info(f"Clearing plot on canvas within '{target_widget.objectName()}'.")
            canvas.clear_display()
            return PlotManager(canvas.figure, canvas.axes)
        else:
            PlotManager.logger.error(f"Could not find or create canvas in '{target_widget.objectName()}' to clear.")
            # Return a dummy manager referencing placeholder fig/ax
            fig, ax = plt.subplots(); ax.clear(); plt.close(fig)
            return PlotManager(fig, ax)


    # --- Add other static create_... methods here ---
    # Example:
    # @staticmethod
    # def create_scatter(target_widget: QWidget, x_data, y_data) -> PlotManager:
    #     canvas = PlotManager._find_or_create_canvas(target_widget)
    #     if not canvas:
    #         fig, ax = plt.subplots(); ax.clear(); plt.close(fig)
    #         return PlotManager(fig, ax)
    #
    #     ax = canvas.axes
    #     fig = canvas.figure
    #     try:
    #         ax.clear()
    #         # ... validation ...
    #         ax.scatter(x_data, y_data)
    #         ax.set_title("Scatter Plot") # Default
    #         # ... other plotting ...
    #         canvas.draw_idle()
    #         canvas._is_empty = False
    #         return PlotManager(fig, ax) # Return manager for config
    #     except Exception as e:
    #         # ... error handling, draw error message on canvas ...
    #         return PlotManager(fig, ax) # Return manager referencing error state

