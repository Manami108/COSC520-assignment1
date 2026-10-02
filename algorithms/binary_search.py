# Input: a sorted list of values and a target value to search for
# Output: True if the target is found in the list, False otherwise  
# This function starts by checking the list from the middle. 
# Depending on whether the target is smaller or larger, it continues searching in only one half of the remaining elements. 
def binary_search(values, target):
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

# Input: a sorted list of values and a new value to insert
# Output: True if the value is inserted, False if it already exists
# This function uses binary search to find the correct insertion position.
# The value is inserted at that position so that the list remains sorted.
def binary_insert(values, target):
    low = 0
    high = len(values) - 1

    while low <= high:
        mid = (low + high) // 2
        if values[mid] == target:
            return False
        if values[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    values.insert(low, target)
    return True

# Input: a sorted list of values and a target value to delete
# Output: True if the value is deleted, False if it does not exist
# This function uses binary search to find the target.
# If the target is found, it is removed while the remaining list stays sorted.
def binary_delete(values, target):
    low = 0
    high = len(values) - 1
    
    while low <= high:
        mid = (low + high) // 2
        if values[mid] == target:
            values.pop(mid)
            return True
        if values[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return False