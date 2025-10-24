from utils.plot.plot_manager import PlotManager
from PyQt6.QtWidgets import QWidget
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

class StudentScoreVisualizer():
    @staticmethod
    def create_score_distribution(target_widget: QWidget, score_data: list[dict]) -> PlotManager:
        """
        Finds/Creates canvas in target_widget, clears it, draws score distribution.

        Args:
            target_widget: The QWidget to draw the plot in.
            score_data: List of dictionaries with 'avg_score'.

        Returns:
            A PlotManager instance referencing the canvas's axes for configuration.
        """
        canvas = PlotManager._find_or_create_canvas(target_widget)
        if not canvas:
            PlotManager.logger.error(f"Could not get canvas for '{target_widget.objectName()}' to create score distribution.")
            fig, ax = plt.subplots(); ax.clear(); plt.close(fig) # Dummy fig/ax
            return PlotManager(fig, ax)

        # Proceed with plotting on the obtained canvas
        ax = canvas.axes
        fig = canvas.figure
        PlotManager.logger.info(f"Attempting to create score distribution plot in '{target_widget.objectName()}'...")

        try:
            ax.clear() # Clear canvas before drawing new plot
            SCORE_COL = 'avg_score'

            # --- Data Validation ---
            if not score_data:
                ax.set_title("No Data Available")
                ax.text(0.5, 0.5, "No scores provided", ha='center', va='center', transform=ax.transAxes)
                ax.set_xticks([]); ax.set_yticks([])
                PlotManager.logger.warning("No data provided for score distribution.")
                canvas.draw_idle()
                canvas._is_empty = True
                return PlotManager(fig, ax)

            df = pd.DataFrame(score_data)

            if SCORE_COL not in df.columns or df[SCORE_COL].isnull().all() or df[SCORE_COL].empty:
                ax.set_title(f"Invalid Data ('{SCORE_COL}')")
                ax.text(0.5, 0.5, f"Column '{SCORE_COL}' missing\nor contains no valid scores.", ha='center', va='center', transform=ax.transAxes, wrap=True)
                ax.set_xticks([]); ax.set_yticks([])
                PlotManager.logger.warning(f"Invalid or empty data in '{SCORE_COL}'.")
                canvas.draw_idle()
                canvas._is_empty = True
                return PlotManager(fig, ax)

            # --- Apply Style (Optional) ---
            try:
                PlotManager.logger.debug("Applied 'science' style.")
            except Exception as style_err:
                 PlotManager.logger.warning(f"Could not apply 'science' style: {style_err}. Using default.")

            # --- Plotting ---
            sns.histplot(data=df, x=SCORE_COL, kde=True, ax=ax, bins=20, stat='density',
                         color='skyblue', edgecolor='black')

            mean_score = df[SCORE_COL].mean()
            median_score = df[SCORE_COL].median()
            line_styles = {'linewidth': 1.5}
            legend_needed = False
            if pd.notna(mean_score):
                 ax.axvline(mean_score, color='red', linestyle='--', label=f'Mean ({mean_score:.1f})', **line_styles)
                 legend_needed = True
            if pd.notna(median_score):
                ax.axvline(median_score, color='green', linestyle=':', label=f'Median ({median_score:.1f})', **line_styles)
                legend_needed = True

            # --- Default Labels/Title ---
            ax.set_title("Student Score Distribution") # Default title
            ax.set_xlabel("Average Score")
            ax.set_ylabel("Density / Frequency")
            if legend_needed:
                ax.legend()
            ax.grid(True, linestyle='--', alpha=0.6)

            # --- Redraw Canvas ---
            canvas.draw_idle()
            canvas._is_empty = False # Mark canvas as containing a plot
            PlotManager.logger.info("Score distribution plot drawn successfully.")

            # --- Return Manager for Configuration ---
            return PlotManager(fig, ax) # Return manager referencing the plotted axes

        except Exception as e:
            PlotManager.logger.error(f"Error creating score distribution plot: {e}", exc_info=True)
            # Display error message on the canvas
            try:
                ax.clear()
                ax.set_title("Plotting Error")
                ax.text(0.5, 0.5, f"Could not generate plot:\n{type(e).__name__}", ha='center', va='center', transform=ax.transAxes, wrap=True)
                ax.set_xticks([]); ax.set_yticks([])
                canvas.draw_idle()
                canvas._is_empty = True
            except Exception as display_err:
                 PlotManager.logger.error(f"Further error displaying plot error message: {display_err}", exc_info=True)
            # Return manager referencing the axes in error state
            return PlotManager(fig, ax)
    