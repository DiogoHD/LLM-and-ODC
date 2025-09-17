import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_bar(df_ia: pd.DataFrame, df_human: pd.DataFrame, category: str, ax: plt.Axes) -> None:
    "Creates Bar Graph"
    
    # Data
    counts = pd.crosstab(df_ia[category], df_ia["Model"])   # Creates a table with the frequency of each defect for each model
    human_counts  = df_human[category].value_counts()               # Counting Human Data
    counts = counts.reindex(human_counts.index, fill_value=0)       # Only keeps the real defects
    counts["Human"] = human_counts                                  # Adds "Human" column to the table
    
    # Data in percent
    percent = counts.copy()
    totals = counts.sum()
    for col in percent.columns:
        percent[col] = (percent[col]/totals[col]*100).round(2)

    print(counts)
    print(percent)
    
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
    ax.set_xticks(x + w*(counts.shape[1]-1)/2)          # counts.shape returns a tuple with the number of lines and columns (lines, columns); -1)/2 is used to center the text
    ax.set_xticklabels(counts.index, rotation=0, ha="center")
    ax.set_ylabel("Frequency")
    ax.yaxis.grid(True, linestyle='--', alpha=0.4, linewidth=1)         # Adds a y-grid for better visualization
    ax.set_title(category)
    ax.legend()

    
# Read CSVs
df_output = pd.read_csv("output.csv")
df_input = pd.read_csv("input.csv")

# Creating Bar Graphs
fig, axes = plt.subplots(1, 2, figsize=(16, 8), constrained_layout=True)    # constrained_layout automatically adjusts the space between subplots, titles, labels and legends
for i, defect in enumerate(["Defect Type", "Defect Qualifier"]):
    create_bar(df_output, df_input, defect, axes[i])

fig.suptitle("Defect Type and Defect Qualifier Comparison", fontsize=16)         # The Main Title
plt.show()