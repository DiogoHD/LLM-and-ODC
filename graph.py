import pandas as pd
import matplotlib.pyplot as plt
from functions import create_bar
    
# Read CSVs
df_output = pd.read_csv("output.csv")
df_input = pd.read_csv("input.csv")

# Creating Bar Graphs
fig, axes = plt.subplots(1, 2, figsize=(16, 8), constrained_layout=True, num="Vulnerabilities", sharey=True)    # constrained_layout automatically adjusts the space between subplots, titles, labels and legends
for i, defect in enumerate(["Defect Type", "Defect Qualifier"]):
    create_bar(df_output, df_input, defect, axes[i])

fig.suptitle("Defect Type and Defect Qualifier Comparison", fontsize=16)         # The Main Title
plt.show()