import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def excel_reader(name: str) -> pd.DataFrame:
    """Accesses a excel in the data folder and converts it to a pandas dataframe
    
    Args:
        name (str): The name of the excel file without extension
        
    Raises:
        RuntimeError: If it can't open the excel file
        
    Returns:
        pd.DataFrame: A pandas dataframe
    """
    
    # Accessing the location of the excel
    script_dir = Path(__file__).parent          # Get the folder where this file is located (src/)
    data_dir = script_dir.parent / "data"       # Goes up one level and joins with data directory
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / f"{name}.xlsx"
    
    # Opening excel
    try:
        df = pd.read_excel(file_path, sheet_name=0, header=1)
    except Exception as e:
        raise RuntimeError(f"Failed to open excel file in {file_path}: {e}") from e
    
    desired_cols = ["V_ID", "Project", "CVE", "V_CLASSIFICATION", "P_COMMIT", "Defect Type", "Defect Qualifier", "# Files", "Filenames"]
    df = df[desired_cols]
    
    return df

def create_crosstab(df_ia: pd.DataFrame, df_human: pd.DataFrame, category: str) -> pd.DataFrame:
    """Creates a table with the frequency of each defect for each IA model and returns it.\n
    It also prints the table the Frequency Table and a Percent Table
    
    Args:
        df_ia (pd.DataFrame): Dataframe with analysis of AI responses
        df_human (pd.DataFrame): Dataframe with human responses
        category (str): The category being analyzed
    
    Returns:
        pd.DataFrame: Cross tabulation with two factors
    """
    
    df = pd.crosstab(df_ia[category], df_ia["Model"])           # Creates a table with the frequency of each defect for each model
    human_counts = df_human[df_human["P_COMMIT"].isin(df_ia["Sha"])]
    human_counts = human_counts[category].value_counts()               # Counting Human Data
    df = df.reindex(human_counts.index, fill_value=0)       # Only keeps the real defects
    df["Human"] = human_counts                                  # Adds "Human" column to the table
    
    # Data in percent
    percent = df.copy()
    totals = df.sum()
    for col in percent.columns:
        percent[col] = (percent[col]/totals[col]*100).round(2)
    
    print(df)
    print(percent)
    print("\n")
    
    return df

def create_bar(df: pd.DataFrame, category: str, ax: plt.Axes) -> None:
    """Creates a Bar Graph
    
    Args:
        df (pd.DataFrame): DataFrame with the frequency of each element
        category (str): The graph's title
        ax (plt.Axes): Graph's position in the subplot
    """
    
    # Bar width and x locations
    x = np.arange(len(df))
    w = 0.05
    
    # Draw Bars for each Defect Type
    for i, col in enumerate(df.columns):
        bars = ax.bar(x + i*w, df[col], width=w, label=col)
        ax.bar_label(bars, fontsize=8)
    
    # Adjust Y-axis limit to make room for values
    ymax = df.values.max()      # counts.values returns only the numeric data in the DataFrame; counts.values.max() finds the max value in that array
    ax.set_ylim(0, ymax * 1.10)     # 10% off 
    
    # Labels
    ax.set_xticks(x + w*(df.shape[1]-1)/2)          # counts.shape returns a tuple with the number of lines and columns (lines, columns); -1)/2 is used to center the text
    ax.set_xticklabels(df.index, rotation=0, ha="center")
    ax.set_ylabel("Frequency")
    ax.yaxis.grid(True, linestyle='--', alpha=0.4, linewidth=1)         # Adds a y-grid for better visualization
    ax.set_title(category)
    ax.legend()

def create_pie(df: pd.DataFrame) -> None:
    """Creates multiple Pie Charts using matplotlib to show the proportion between the responses of each IA.
    
    Args:
        df (pd.DataFrame): DataFrame with the frequency of each IA response
    """
    
    # Only writes percent if it is greater than zero
    def func(pct):
        return f'{pct:.1f}%' if pct > 0 else '' 
    
    n = len(df.columns)
    ncols = math.ceil(math.sqrt(n))     # Rounds the square root up
    nrows = math.ceil(n / ncols)
    
    fig, axs = plt.subplots(nrows, ncols, figsize=(4*ncols, 4*nrows), constrained_layout=True, num="Pie Chart - " + df.index.name, sharey=True)    # constrained_layout automatically adjusts the space between subplots, titles, labels and legends
    axs: np.ndarray[plt.Axes] = axs.flatten()       # Transforms the 2D matrix in a 1D matrix
    
    labels = df.index.tolist()
    cmap = plt.get_cmap("tab20")    # palette with up to 20 different colors
    colors_map = {label: cmap(i / len(labels)) for i, label in enumerate(labels)}
    
    for index, model in enumerate(df.columns):
        frequency = df.loc[:, model]
        frequency = frequency[frequency > 0]
        
        axs[index].pie(frequency, labels=None, autopct=func, colors=[colors_map[i] for i in frequency.index])
        axs[index].set_title(model)
    
    for j in range(len(df.columns), len(axs)):
        fig.delaxes(axs[j])
    
    fig.suptitle(df.index.name)
    legend_handles = [plt.Line2D([0], [0], color=colors_map[label], lw=4) for label in labels]
    fig.legend(legend_handles, labels, title=df.index.name, loc="lower right")