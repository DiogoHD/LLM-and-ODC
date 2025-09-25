import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import ollama
import pandas as pd
import regex
from github import Commit, Github, GithubException


# main.py 
def fetch_commit(project: str, sha: str) -> Commit.Commit | None:
    "Given a project and a sha from a commit, fetches the commit"
    
    g = Github()
    
    try:
        # Gets the repository
        match project:
            case "Linux":
                repo = g.get_repo("torvalds/linux")
            case "Mozilla":
                repo = g.get_repo("mozilla/gecko-dev")
            case "Xen":
                repo = g.get_repo("xen-project/xen")
            case _:
                print(f"Unknown Project '{project}' for commit '{sha}'")
                return None
        commit = repo.get_commit(sha)       # Gets the commit
        return commit
        
    except GithubException as e:
        print(f"Error accessing repository '{project}' with commit '{sha}': {e}")       # If it can't access the repo or the commit, ir prints an error
        return None

def create_message(commit: Commit.Commit, prompt: str) -> list[tuple[str, str]]:
    "Given a commit and initial prompt, creates a message from the IA"
    if commit is None:
        return []
    
    response_format = "Your response should not provide an explanation and should only contain the following response format for each defect you classify in each file:\nDefect Type: <Defect Type>\nDefect Qualifier: <Defect Qualifier>"  
    # Save prompt for each file from the commit
    content = []
    for f in commit.files:
        file_prompt = f"{prompt}\n\nFile name: {f.filename}\nChanges: {str(f.changes)}\nPatch (diff):\n{f.patch}\n\n{response_format}"      # Joins the prompt with the commit and the format intended
        content.append((file_prompt, f.filename))
    
    return content

def call_model(model: str, content: str, folder: Path) -> None:
    "Calls IA model via ollama, runs the specified prompt and stores the response in a text file"
    model_name: str = model.partition(":")[0]    # Take model name before ':' if present
    
    try:
        response: ollama.ChatResponse = ollama.chat(
            model = model,                                      # Defines which ollama's model is going to be used
            messages = [{"role": "user", "content": content}],  # Defines who's using the model and what's going to be its content
            )
        
        # Writes response in a text file
        file_path: Path = folder / f"{model_name}.txt"      # Creates the path to the text folder
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.message.content if response.message and response.message.content else "[No Model Response]")
        except (OSError, PermissionError, UnicodeEncodeError) as e:
            raise RuntimeError(f"Failed to write text file to {file_path}: {e}") from e
        
    except Exception as e:
        print(f"Error calling model {model} for file {folder.name} in commit {folder.parent.name}: {e}")

def process_commit(row, prompt: str, models: list[str]) -> None:
    """
    Function used to work with ThreadPoolExecutor() from concurrent.future
    
    Args:
        row (pd.NamedTuple): The return value of itertuples()
        prompt (str): The prompt for the IA
        models (list[str]): A list of the IA models downloaded via ollama
    """
    script_dir = Path(__file__).parent          # Get the folder where this file is located (src/)
    output_dir = script_dir.parent / "test"   # Goes up one level and joins with data directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    sha: str = row.P_COMMIT
    sha_dir: Path = output_dir / sha            # Directory's path to save IA's response
    sha_dir.mkdir(parents=True, exist_ok=True)  # Creates the directory if it doesn't exist; parents=True creates every needed parent directory if it doesn't exist; exist_ok=True doesn't give a error if the directory already exists
    
    # Create prompt for the IA
    commit: Commit.Commit = fetch_commit(row.Project, sha)
    content = create_message(commit, prompt)
    
    for message, file_name in content:
        safe_name = file_name.replace("/", "-").replace(".", "_")       # Replaces / and . so it doesn't create multiple directories and a file
        file_dir: Path = sha_dir / safe_name
        file_dir.mkdir(parents=True, exist_ok=True)
        for model in models:  
            call_model(model, message, file_dir)


# data_analyzer.py    
def make_pattern(name: str) -> regex.Pattern:
    "Creates a regex pattern to extract values associated with the specified field"
    # Uses a raw string so Python can allow escape characters
    pattern = regex.compile(rf"""
    (?:{name})      # Use that word without capturing it
    {{e<=1}}        # Fuzzy Matching - Allows at most 1 typo (only possible using the module regex (impossible with re))
    \s*[:\-–—]\s*   # Allows various separators and it can have 0 or multiple spaces before or after the separator
    (?:\d+\)?\s*)?  # If a number appears before the word that we want [2) or 3] it ignores it
    [*\s(<[\{{]*    # Allows the word to be between some kind of brackets or be in bold
    ([A-Za-z/]+)    # Captures the first word after the string (that only can contain letters and a /)
    """, regex.IGNORECASE | regex.VERBOSE)
    # regex.IGNORECASE makes the search be case-insensitive
    # regex.VERBOSE makes the search ignore newlines, spaces, tabs and comments
    
    return pattern

def extract_defects(text: str) -> dict[str, str | None]:
    "Extracts 'Defect Type' and 'Defect Qualifier' from a given text into a dictionary"
    
    text = regex.sub("<think>.*?(?:</think>|$)", "", text, flags=regex.DOTALL)      # Cleans the thinking from the IA's that support it, if it doesn't end, cleans the whole text
    
    result = {}
    for defect in ["Type", "Qualifier"]:
        matches = regex.findall(make_pattern(defect), text)                 # Finds the defect in the given text, using a specific pattern
        result[f"Defect {defect}"] = [m.strip("'\",*()") for m in matches]              # If found, it strips the defect from unwanted characters, otherwise returns None
    return result

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
    
    output = pd.crosstab(df_ia[category], df_ia["Model"])           # Creates a table with the frequency of each defect for each model
    human_counts = df_human[df_human["P_COMMIT"].isin(df_ia["Sha"])]
    human_counts = human_counts[category].value_counts()               # Counting Human Data
    output = output.reindex(human_counts.index, fill_value=0)       # Only keeps the real defects
    output["Human"] = human_counts                                  # Adds "Human" column to the table
    
    # Data in percent
    percent = output.copy()
    totals = output.sum()
    for col in percent.columns:
        percent[col] = (percent[col]/totals[col]*100).round(2)
    
    print(output)
    print(percent)
    print("\n")
    
    return output

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
    nrows = math.ceil(n / ncols)        # 
    
    fig, axs = plt.subplots(nrows, ncols, figsize=(4*ncols, 4*nrows), constrained_layout=True, num="Pie Chart - " + df.index.name, sharey=True)    # constrained_layout automatically adjusts the space between subplots, titles, labels and legends
    axs: np.ndarray[plt.Axes] = axs.flatten()       # Transforms the 2D matrix in a 1D matrix
    wedges_all = []         # To store the wedges of all graphs for a global legend 
    
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