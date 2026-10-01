# This function starts by checking the list from the middle. 
# Depending on whether the target is smaller or larger, it continues searching in only one half of the remaining elements. 
# It returns True if the target is found and False if it is not.

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
