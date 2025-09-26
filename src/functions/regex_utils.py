import regex


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

def extract_defects(text: str) -> dict[str, list[str]]:
    """Extracts all the defects that match the pattern from the given string
    
    Args:
        text (str): The string to be analyzed
        
    Returns:
        dict[str, str | None]: A dictionary where the key is the defect and the value is a list with the name of the defects found
    """
    "Extracts 'Defect Type' and 'Defect Qualifier' from a given text into a dictionary"
    
    text = regex.sub("<think>.*?(?:</think>|$)", "", text, flags=regex.DOTALL)  # Cleans the thinking from the IA's that support it, if it doesn't end, cleans the whole text
    
    result = {}
    for defect in ["Type", "Qualifier"]:
        matches = regex.findall(make_pattern(defect), text)                     # Finds the defect in the given text, using a specific pattern
        result[f"Defect {defect}"] = [m.strip("'\",*()") for m in matches]      # If found, it strips the defect from unwanted characters, otherwise returns None
    return result