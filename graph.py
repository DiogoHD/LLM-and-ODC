import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("file.csv")


# Defect Type Bar Plot
keys_type = list(set(df["Defect Type"]))
df_type  = df["Defect Type"].value_counts()
plt.subplot(1, 2, 1)
df_type.plot(kind = "bar")
plt.title("Defect Type - Count")
# Adds values on top of the bars
for i, value in enumerate(df_type):
    plt.text(i, value, str(value), ha='center', va='bottom')

# Defect Qualifier Bar Plot
keys_qualifier = list(set(df["Defect Qualifier"]))
df_qualifier = df["Defect Qualifier"].value_counts()
plt.subplot(1, 2, 2)
df_qualifier.plot(kind = "bar")
plt.title("Defect Qualifier - Count")
# Adds values on top of the bars
for i, value in enumerate(df_qualifier):
    plt.text(i, value, str(value), ha='center', va='bottom')


plt.suptitle("Results")
plt.show()