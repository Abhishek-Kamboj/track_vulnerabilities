import re
from typing import Dict, List


def parse_requirements(content: str) -> List[Dict[str, str]]:
    """Parse requirements.txt content into list of dependencies."""
    dependencies = []
    for line in content.split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            match = re.match(r"^([a-zA-Z0-9_-]+)(==|>=|<=|>|<)([\d\.]+.*)$", line)
            if match:
                dependencies.append(
                    {"name": match.group(1).lower(), "version": match.group(3)}
                )
    return dependencies
