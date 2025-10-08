import pandas as pd
from matplotlib.axes import Axes
from matplotlib import pyplot as plt
import scienceplots # Ensure this is installed

def create_score_distribution_plot(score_data: list[dict], ax: Axes, title: str = "Student Score Distribution"):
    """
    Plots the student score distribution directly onto the provided Matplotlib Axes object.

    Args:
        score_data (list[dict]): List of dictionaries containing score data.
        ax (Axes): The Matplotlib Axes object to draw the plot on (i.e., self.plot_canvas.axes).
        title (str): The title for the plot.
    """
    
    # --- 1. Preparation ---
    df = pd.DataFrame(score_data)
    SCORE_COL = 'avg_score'

    if SCORE_COL not in df.columns:
        ax.set_title("Data Error")
        ax.text(0.5, 0.5, f"Score column '{SCORE_COL}' not found.", transform=ax.transAxes, ha='center')
        return

    # Clear any previous plot on the axes
    ax.clear() 

    # --- 2. Styling ---
    # Apply the style only when plotting starts
    # try:
    #     plt.style.use(['science', 'grid']) 
    # except ValueError:
    #     pass # Use default if not found

    # --- 3. Plotting: Histogram and KDE ---
    
    # Histogram
    df[SCORE_COL].plot(
        kind='hist', ax=ax, bins=20, density=True, alpha=0.7, 
        label='Score Frequency'
    )
    
    # KDE Plot
    df[SCORE_COL].plot(
        kind='kde', ax=ax, linewidth=2, color='#0078d4', 
        label='Score Density Estimate'
    )

    # --- 4. Annotation ---
    mean_score = df[SCORE_COL].mean()
    median_score = df[SCORE_COL].median()

    ax.axvline(mean_score, color='red', linestyle='--', linewidth=1.5, label=f'Mean ({mean_score:.1f})')
    ax.axvline(median_score, color='green', linestyle=':', linewidth=1.5, label=f'Median ({median_score:.1f})')
    
    ax.set_title(title)
    ax.set_xlabel("Student Score")
    ax.set_ylabel("Density / Frequency")
    ax.legend()
    
    # Note: We do NOT call plt.show() here.