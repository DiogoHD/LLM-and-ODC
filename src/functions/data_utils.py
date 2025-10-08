import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


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
    root_dir = Path(__file__).parent.parent.parent  # Get the root folder
    data_dir = root_dir / "data"                    # Joins with data directory
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / f"{name}.xlsx"
    
    # Opening excel
    try:
        df = pd.read_excel(file_path, sheet_name=0, header=1, engine="openpyxl")
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
    
    df = pd.crosstab(df_ia[category], df_ia["Model"])                   # Creates a table with the frequency of each defect for each model
    human_counts = df_human[df_human["P_COMMIT"].isin(df_ia["Sha"])]    # Only gets the defects classification from the humans that were analyzed by the IA
    human_counts = human_counts[category].value_counts()                # Counting Human Data
    
    valid_idx = human_counts.index      # Allowed defects
    # Divides the dataframe in two dataframes: One with the allowed defects and the other with the strange ones
    df_valid = df.loc[df.index.isin(valid_idx)]
    df_other = df.loc[~df.index.isin(valid_idx)]
        
    # Sums the rest in a single line
    if not df_other.empty:
        df_other = pd.DataFrame(df_other.sum()).T   # Sums all the lines in the rest Dataframe, creating a Series, then it converts into a Dataframe and transposes it
        df_other.index = ["Other"]                  # Names the line to Other
        df_final = pd.concat([df_valid, df_other])  # Concatenates the df_valid with the df_other
    else:
        df_final = df_valid
        
    
    df_final["Human"] = human_counts.reindex(df_final.index, fill_value=0).astype(int)   # Adds "Human" column to the Dataframe
    df_final.index.name = category  # Define index name
    
    # Data in percent
    percent = ((df_final / df_final.sum())*100).round(2)
    
    print("\n\n\n")
    print("Frequency Table:")
    print(df_final)
    print("\nPercent Table:")
    print(percent)
    
    return df_final

def create_bar(df: pd.DataFrame, category: str, ax: plt.Axes) -> None:
    """Creates a Bar Graph
    
    Args:
        df (pd.DataFrame): DataFrame with the frequency of each element
        category (str): The graph's title
        ax (plt.Axes): Graph's position in the subplot
    """
    
    # Convert the dataframe from wide to long format
    df_long = df.reset_index().melt(id_vars=df.index.name, var_name="Model", value_name="Frequency")
    bars = sns.barplot(data=df_long, x=category, y="Frequency", hue="Model", ax=ax, palette="tab20")
    
    # Show bar labels (the number above the bar) for each defect
    for bar in bars.patches:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 1, int(height), ha='center', va='bottom', fontsize=6.5)
    
    # Labels
    ax.set_ylabel("Frequency")
    ax.grid(axis="y", linestyle='--', alpha=0.4, linewidth=1)         # Adds a y-grid for better visualization
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
    n_cols = math.ceil(math.sqrt(n))     # Rounds the square root up
    n_rows = math.ceil(n / n_cols)
    
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 4*n_rows), num="Pie Chart - " + df.index.name, sharey=True)
    axs: np.ndarray[plt.Axes] = axs.flatten()       # Transforms the 2D matrix in a 1D matrix
    
    labels = df.index.tolist()
    cmap = plt.get_cmap("tab20")    # Palette with up to 20 different colors
    colors_map = {label: cmap(i / max(1, len(labels)-1)) for i, label in enumerate(labels)}
    
    for index, model in enumerate(df.columns):
        frequency = df.loc[:, model]
        frequency = frequency[frequency > 0]
        
        axs[index].pie(frequency, labels=None, autopct=func, colors=[colors_map[i] for i in frequency.index])
        axs[index].set_title(model)
    
    for j in range(n, len(axs)):
        fig.delaxes(axs[j])
    
    fig.suptitle(df.index.name)
    legend_handles = [plt.Line2D([0], [0], color=colors_map[label], lw=4) for label in labels]
    fig.legend(legend_handles, labels, title=df.index.name, loc="lower right")