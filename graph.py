import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_bar(Category: str, ax: plt.axes) -> None:
    # Counting Data
    output_counts = df_output[Category].value_counts()
    input_counts  = df_input[Category].value_counts()
    
    # Category Union, witouth repetitions
    keys = sorted(set(output_counts.index) | set(input_counts.index))
    
    # Reindex to align the 2 series (missing elements = 0)
    output_counts = output_counts.reindex(keys, fill_value=0)
    input_counts  = input_counts.reindex(keys, fill_value=0)
    
    # Bar width and x locations
    w, x = 0.4, np.arange(len(keys))
    ax.bar(x - w/2, output_counts, width=w, label='IA')
    ax.bar(x + w/2, input_counts, width=w, label='Human')
    
    # Labels
    ax.set_xticks(x)
    ax.set_xticklabels(keys, rotation=90, ha="center")
    ax.set_ylabel("Frequency")
    ax.set_title(Category)
    
    # Adds values on top of the bars for the IA
    for i, value in enumerate(output_counts):
        ax.text(x[i] - w/2, value, str(value), ha='center', va='bottom')
    
    # Adds values on top of the bars for the Human
    for i, value in enumerate(input_counts):
        ax.text(x[i] + w/2, value, str(value), ha='center', va='bottom')
        
    # Adjust Y-axis limit to make room for values
    ymax = max(output_counts.max(), input_counts.max())
    ax.set_ylim(0, ymax * 1.10)  # 10% off
    

# Read CSVs
df_output = pd.read_csv("file.csv")
df_input = pd.read_csv("input.csv")

# Creating Bar Graphs
fig, axes = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)    # constrained_layout automatically adjusts the space between subplots, titles, labels and legends
create_bar("Defect Type", axes[0])
create_bar("Defect Qualifier", axes[1])

fig.legend(['IA', 'Human'], loc='lower center')    # Showing bar graph's legend
fig.suptitle("Defect Type and Defect Qualifier Comparison", fontsize=16)         # The Main Title
fig.tight_layout()              # Automatically adjusts margins and spacing
plt.show()