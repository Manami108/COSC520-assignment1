# ============================================================
# 1. LINEAR SEARCH
# ============================================================

def linear_search(values, target):
    """
    Input:
        values: list of usernames
        target: username to find

    Output:
        True if target exists, otherwise False

    Complexity:
        O(n)
    """
    for value in values:
        if value == target:
            return True

    return False