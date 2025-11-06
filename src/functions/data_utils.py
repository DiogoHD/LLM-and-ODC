from collections import Counter
from pathlib import Path

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

def count_matches(df_human: pd.DataFrame, df_ia: pd.DataFrame) -> pd.DataFrame:
    """Creates a DataFrame with the accuracy of every IA.

    Args:
        df_human (pd.DataFrame): A dataframe with human analysis
        df_ia (pd.DataFrame): A dataframe with IA analysis

    Returns:
        pd.DataFrame: A dataframe with the accuracy of every IA
    """
    result = pd.DataFrame(0, columns=["Correct", "Incorrect"], index=np.unique(df_ia["Model"]))
    
    for commit, df_human_commit in df_human.groupby("P_COMMIT"):
        human_defects = Counter(zip(df_human_commit["Defect Type"], df_human_commit["Defect Qualifier"]))
        df_ia_commit = df_ia[df_ia["Sha"] == commit]
        
        for model_name, df_model in df_ia_commit.groupby("Model"):
            ia_defects = Counter(zip(df_model["Defect Type"], df_model["Defect Qualifier"]))
            
            # Correct = Intersection between human and IA defects
            correct = sum((human_defects & ia_defects).values())
            result.loc[model_name, "Correct"] += correct
            # Incorrect = Defects caught by IA but not by humans
            result.loc[model_name, "Incorrect"] += sum((ia_defects - human_defects).values())
    result["Accuracy"] = (result["Correct"] / (result["Correct"] + result["Incorrect"]) * 100).round(2)
    return result