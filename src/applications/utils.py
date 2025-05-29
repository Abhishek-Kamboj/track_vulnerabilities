import re
from re import Match
from typing import Dict, List

def is_a_valid_line(line:str)->bool:
    """
    confirms that line has '==' in the middle of it
    ^(?!==)  Ensures the string does not start with '=='.
    (.*==.*)  Confirms that '==' exists somewhere in the string.
    (?<!==)$  Ensures the string does not end with '=='.

    Args:
        line (str): line of text to analyse

    Returns:
        bool: True if '==' found else false
    """
    pattern: str = r"^(?!==)(.*==.*)(?<!==)$"
    return bool(re.match(pattern, line))

def parse_requirements(content: str) -> List[Dict[str, str]]:
    """
    Parse requirements.txt content into list of dependencies.

    Args:
        content (str): content of requirement.txt file as a string.

    Returns:
        List[Dict[str, str]]: Each row of list as dependency name as key of
                              dictionay and version as value.
    """
    dependencies = []
    for line in content.split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            if not(is_a_valid_line(line)):
                raise Exception("only '==' is permitted in Requirement.txt ")

            match: Match = re.match(r"^([a-zA-Z0-9_-]+)(==)([\d\.]+.*)$", line)
            if match:
                dependencies.append(
                    {"name": match.group(1).lower(), "version": match.group(3)}
                )
    return dependencies
