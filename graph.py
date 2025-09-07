import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read CSVs
df_output = pd.read_csv("file.csv")
df_input = pd.read_csv("input.csv")

# Counting Data
output_type_counts = df_output["Defect Type"].value_counts()
input_type_counts  = df_input["Defect Type"].value_counts()

output_qualifier_counts = df_output["Defect Qualifier"].value_counts()
input_qualifier_counts = df_input["Defect Qualifier"].value_counts()

# Category Union, witouth repetitions
keys_type = sorted(set(output_type_counts.index) | set(input_type_counts.index))
keys_qualifier = sorted(set(output_qualifier_counts.index) | set(input_qualifier_counts.index))

# Reindexar para alinhar as duas séries (faltas = 0)
output_type_counts = output_type_counts.reindex(keys_type, fill_value=0)
input_type_counts  = input_type_counts.reindex(keys_type, fill_value=0)

output_qualifier_counts = output_qualifier_counts.reindex(keys_qualifier, fill_value=0)
input_qualifier_counts  = input_qualifier_counts.reindex(keys_qualifier, fill_value=0)


# Bar width and x locations
w, xt = 0.4, np.arange(len(keys_type))
v, xq = 0.4, np.arange(len(keys_qualifier))

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
axes[0].bar(xt - w/2, output_type_counts, width=w, label='IA')
axes[0].bar(xt + w/2, input_type_counts, width=w, label='Human')
axes[1].bar(xq - v/2, output_qualifier_counts, width=v, label='IA')
axes[1].bar(xq + v/2, input_qualifier_counts, width=v, label='Human')


# Labels
axes[0].set_xticks(xt)
axes[0].set_xticklabels(keys_type, rotation=45, ha="right")
axes[1].set_xticks(xq)
axes[1].set_xticklabels(keys_qualifier, rotation=45, ha="right")

axes[0].set_ylabel('Defect Type')
axes[0].set_title('Defect Type - Comparison')
axes[1].set_ylabel('Defect Qualifier')
axes[1].set_title('Defect Qualifier - Comparison')

# Adds values on top of the bars
for i, value in enumerate(output_type_counts):
    axes[0].text(xt[i] - w/2, value, str(value), ha='center', va='bottom')
    
 # Adds values on top of the bars
for i, value in enumerate(input_type_counts):
    axes[0].text(xt[i] + w/2, value, str(value), ha='center', va='bottom')
    
# Adds values on top of the bars
for i, value in enumerate(output_qualifier_counts):
    axes[1].text(xq[i] - v/2, value, str(value), ha='center', va='bottom')
    
 # Adds values on top of the bars
for i, value in enumerate(input_qualifier_counts):
    axes[1].text(xq[i] + v/2, value, str(value), ha='center', va='bottom')


axes[0].legend()
axes[1].legend()
plt.suptitle("Results")
plt.tight_layout()
plt.show()