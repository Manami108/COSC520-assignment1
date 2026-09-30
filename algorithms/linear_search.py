# Completed 

def linear_search(values, target):
    """Return whether target occurs in values by scanning from the start."""
    for value in range(len(values)):
        if values[value] == target:
            return True
    return False
