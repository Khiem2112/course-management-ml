from plot_manager import PlotManager
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

class StudentScoreVisualizer():
    @staticmethod
    def create_score_distribution(score_data: list[dict]) -> PlotManager:
        """
        Creates a PlotManager instance containing a score distribution plot.

        Args:
            score_data: List of dictionaries with 'avg_score'.

        Returns:
            A PlotManager instance ready for further configuration or display.
        """
        PlotManager.logger.info("Creating score distribution plot content...")
        fig, ax = plt.subplots() # Create new Figure and Axes for this plot
        SCORE_COL = 'avg_score'

        try:
            if not score_data:
                PlotManager.logger.warning("No data provided for score distribution.")
                # Return an empty plot manager, caller can check has_plot
                return PlotManager.create_empty().set_title("No Data Available")

            df = pd.DataFrame(score_data)

            if SCORE_COL not in df.columns or df[SCORE_COL].isnull().all() or df[SCORE_COL].empty:
                PlotManager.logger.warning(f"Invalid or empty data in '{SCORE_COL}'.")
                return PlotManager.create_empty().set_title(f"Invalid Data in '{SCORE_COL}'")

            # Apply style before plotting
            try:
                plt.style.use('science')
                PlotManager.logger.debug("Applied 'science' style for score distribution.")
            except Exception as style_err:
                 PlotManager.logger.warning(f"Could not apply 'science' style: {style_err}")

            # Plot histogram and KDE
            sns.histplot(data=df, x=SCORE_COL, kde=True, ax=ax, bins=20, stat='density',
                         color='skyblue', edgecolor='black')

            # Add mean/median lines
            mean_score = df[SCORE_COL].mean()
            median_score = df[SCORE_COL].median()
            line_styles = {'linewidth': 1.5}
            if pd.notna(mean_score):
                 ax.axvline(mean_score, color='red', linestyle='--',
                            label=f'Mean ({mean_score:.1f})', **line_styles)
            if pd.notna(median_score):
                ax.axvline(median_score, color='green', linestyle=':',
                           label=f'Median ({median_score:.1f})', **line_styles)

            # Set default labels/title (can be overridden later)
            ax.set_title("Student Score Distribution")
            ax.set_xlabel("Average Score")
            ax.set_ylabel("Density / Frequency")
            if pd.notna(mean_score) or pd.notna(median_score):
                ax.legend()
            ax.grid(True, linestyle='--', alpha=0.6)

            PlotManager.logger.info("Score distribution plot content created successfully.")
            return PlotManager(fig, ax)

        except Exception as e:
            PlotManager.logger.error(f"Error creating score distribution plot content: {e}", exc_info=True)
            # Return an empty plot with an error title
            return PlotManager.create_empty().set_title(f"Error: {type(e).__name__}")