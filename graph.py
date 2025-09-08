import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_bar(category: str, ax: plt.axes) -> None:
    "Creates Bar Graph"
    
    # Data
    counts = pd.crosstab(df_output[category], df_output["Model"])   # Creates a table with the frequency of each defect for each model
    human_counts  = df_input[category].value_counts()               # Counting Human Data
    counts = counts.reindex(human_counts.index, fill_value=0)       # Only keeps the real defects
    counts["Human"] = human_counts                                  # Adds "Human" column to the table
    
    # Bar width and x locations
    x = np.arange(len(counts))
    w = 0.15
    
    # Draw Bars for each Defect Type
    for i, col in enumerate(counts.columns):
        bars = ax.bar(x + i*w, counts[col], width=w, label=col)
        ax.bar_label(bars, fontsize=8)
    
    # Adjust Y-axis limit to make room for values
    ymax = counts.values.max()      # counts.values returns only the numeric data in the DataFrame; counts.values.max() finds the max value in that array
    ax.set_ylim(0, ymax * 1.10)     # 10% off 
    
    # Labels
    ax.set_xticks(x + w*(len(counts.columns)-1)/2)
    ax.set_xticklabels(counts.index, rotation=0, ha="center")
    ax.set_ylabel("Frequency")
    ax.set_title(category)
    ax.legend()

    
# Read CSVs
df_output = pd.read_csv("file.csv")
df_input = pd.read_csv("input.csv")

# Creating Bar Graphs
fig, axes = plt.subplots(1, 2, figsize=(16, 8), constrained_layout=True)    # constrained_layout automatically adjusts the space between subplots, titles, labels and legends
create_bar("Defect Type", axes[0])
create_bar("Defect Qualifier", axes[1])

fig.suptitle("Defect Type and Defect Qualifier Comparison", fontsize=16)         # The Main Title
plt.show()