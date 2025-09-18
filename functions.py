from github import Github, GithubException, Commit
import ollama
from pathlib import Path
import regex
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# main.py 
def get_commit(project: str, sha: str) -> Commit.Commit | None:
    "Given a prompt and a sha from a commit, gets the commit"
    
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
    "Calls IA model via ollama, runs the especified prompt and stores the response in a text file"
    model_name: str = model.partition(":")[0]    # Take model name before ':' if present
    try:
        response: ollama.ChatResponse = ollama.chat(
            model = model,                                      # Defines which ollama's model is going to be used
            messages = [{"role": "user", "content": content}],  # Defines who's using the model and what's going to be its content
            )
        
        # Writes response in a text file
        file_path: Path = folder / f"{model_name}.txt"      # Creates the path to the text folder
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.message.content if response.message and response.message.content else "[No Model Response]")
        
    except Exception as e:
        print(f"Error calling model {model} for commit {folder.name}: {e}")
   
   
# data_analyser.py    
def make_pattern(name: str) -> regex.Pattern:
    "Creates a regex pattern to extract values associated with the especified field"
    # Uses a raw string so Python can allow escape characters
    pattern = regex.compile(rf"""
    (?:{name})      # Use that word witouth capturing it
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
    
    text = regex.sub(r"<think>.*?</think>", " ", text, flags=regex.DOTALL)  # Cleans the thinking from the IA's that support it
    
    result = {}
    for defect in ["Type", "Qualifier"]:
        matches = regex.findall(make_pattern(defect), text)                 # Finds the defect in the given text, using a especific pattern
        result[defect] = [m.strip("'\",*()") for m in matches]              # If found, it strips the defect from unwanted characters, otherwise returns None
    return result

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