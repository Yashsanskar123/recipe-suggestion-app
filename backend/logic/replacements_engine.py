from typing import List,Dict
from.replacements import REPLACEMENTS

def suggest_replacements(missing: list[str]) -> Dict[str, List[str]]:
    """
    Returns alternative ingredients for each missing ingredient.

    """

    suggestions = {}

    for item in missing:
        item_lower = item.lower()

        if item_lower in REPLACEMENTS:
            suggestions[item] = REPLACEMENTS[item_lower]
        else:
            suggestions[item] = ["No replacement available"]
    return suggestions
