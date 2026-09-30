# Completed 

def binary_search(values, target):
    """Return whether target occurs in an ascending sorted sequence."""
    low = 0
    high = len(values)-1

    while low <= high:
        mid = (low + high) // 2

        if values[mid] == target:
            return True

        if values[mid] < target:
            low = mid+1
        else:
            high = mid-1

    return False
