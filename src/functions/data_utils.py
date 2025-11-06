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

def update_accuracy(dataframes: list[pd.DataFrame], df_human: pd.DataFrame, df_ia: pd.DataFrame) -> None:
    """Updates the accuracy dataframes with the number of correct and incorrect matches for each IA model.

    Args:
        dataframes (list[pd.DataFrame]): List of three dataframes to update
        df_human (pd.DataFrame): DataFrame with human analysis
        df_ia (pd.DataFrame): DataFrame with IA analysis
    """
    human_defects = [Counter(df_human["Defect Type"]), Counter(df_human["Defect Qualifier"]), Counter(zip(df_human["Defect Type"], df_human["Defect Qualifier"]))]
            
    for model_name, df_model in df_ia.groupby("Model"):
        ia_defects = [Counter(df_model["Defect Type"]), Counter(df_model["Defect Qualifier"]), Counter(zip(df_model["Defect Type"], df_model["Defect Qualifier"]))]
        
        for idx, df in enumerate(dataframes):
            ia_correct = sum((ia_defects[idx] & human_defects[idx]).values())
            df.loc[model_name, "Correct"] += ia_correct
            df.loc[model_name, "Incorrect"] += sum((ia_defects[idx]).values()) - ia_correct
    

def count_matches(df_human: pd.DataFrame, df_ia: pd.DataFrame) -> list[pd.DataFrame]:
    """Creates three dataframes with the accuracy of every IA model for defect type, defect qualifier and both combined.

    Args:
        df_human (pd.DataFrame): A dataframe with human analysis
        df_ia (pd.DataFrame): A dataframe with IA analysis

    Returns:
        list[pd.DataFrame]: Three dataframes with the accuracy of every IA model for defect type, defect qualifier and both combined
    """
    dataframes = [pd.DataFrame(0, columns=["Correct", "Incorrect"], index=np.unique(df_ia["Model"])) for _ in range(3)]
    
    for commit, df_human_commit in df_human.groupby("P_COMMIT"):
        df_ia_commit = df_ia[df_ia["Sha"] == commit]
        
        if any(df_human_commit["Filenames"].isnull()) or any(df_human_commit["# Files"] != 1):
            update_accuracy(dataframes, df_human_commit, df_ia_commit)
        else:
            for file_name, df_human_file in df_human_commit.groupby("Filenames"):
                df_ia_file = df_ia_commit[df_ia_commit["File Name"] == file_name]
                update_accuracy(dataframes, df_human_file, df_ia_file)


    for name, df in zip(["Type", "Qualifier", "Combined"], dataframes):
        df["Accuracy (%)"] = (df["Correct"] / (df["Correct"] + df["Incorrect"]) * 100).round(2)
        df.Name = f"Defect {name}"
    
    return dataframes