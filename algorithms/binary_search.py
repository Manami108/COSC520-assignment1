# ============================================================
# 2. BINARY SEARCH
# ============================================================

def binary_search(values, target):
    """
    Input:
        values: sorted list of usernames
        target: username to find

    Output:
        True if target exists, otherwise False

    Complexity:
        O(log n)
    """
    low = 0
    high = len(values) - 1

    while low <= high:

        mid = (low + high) // 2

        if values[mid] == target:
            return True

        if values[mid] < target:
            low = mid + 1

        else:
            high = mid - 1

    return False