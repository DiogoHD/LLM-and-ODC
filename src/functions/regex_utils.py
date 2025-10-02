import regex


def remove_think_blocks(text: str) -> str:
    """Removes the think block from a given text
    
    Args:
        text (str): The input string that may contain '<think>' and '</think>' blocks.
    
    Returns:
        str: The string with the '<think>' block(s) removed according to the rules:
            - If both opening and closing tags exist, removes from the first '<think>' to the last '</think>'.
            - If only the opening tag exists, removes from the first '<think>' to the end of the string.
            - If only the closing tag exists, removes from the beginning of the string until the last '</think>'
            - If neither a '<think>' tag nor a '</think> tag exists, returns the original string unchanged.
    """
    start = text.find("<think>")
    end = text.rfind("</think>")
    
    if end == -1:
        # If there's no think block, returns the entire text
        if start == -1:
            return text
        # If there's <think> but there isn't </think>, cuts everything
        else:
            return ""
    else:
        # If there's at least one </think> tag, cuts until the last </think>, returning everything but the think block
        return text[end + len("</think>"):]

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
    
    text = remove_think_blocks(text)  # Cleans the thinking from the IA's that support it, if it doesn't end, cleans the whole text
    
    result = {}
    for defect in ["Type", "Qualifier"]:
        matches = regex.findall(make_pattern(defect), text)                     # Finds the defect in the given text, using a specific pattern
        result[f"Defect {defect}"] = [m.strip("'\",*()") for m in matches]      # If found, it strips the defect from unwanted characters, otherwise returns None
    return result