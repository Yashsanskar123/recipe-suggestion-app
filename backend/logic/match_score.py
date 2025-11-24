def calculate_score(missing_count: int):
    """
    Your custom scoring logic:
        0 missing → 100%
        1-2 missing → 70%
        3-4 missing → 40%
        more → 0%
    """

    if missing_count == 0:
        return 100
    elif missing_count <= 2:
        return 70
    elif missing_count <= 4:
        return 40
    else:
        return 0
    
    