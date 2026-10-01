# Input: a list of values and a target value to search for
# Output: True if the target is found in the list, False otherwise
# To find the target value, this approach goes through the list from the beginning and compares each element with the target. 

def linear_search(values, target):
    for value in range(len(values)):
        if values[value] == target:
            return True
    return False

# Input: a list of values and a new value to insert
# Output: True if the value is inserted, False if it already exists
# This function first checks whether the value already exists.
# If it does not exist, the value is added to the end of the list.

def linear_insert(values, target):
    if linear_search(values, target):
        return False
    values.append(target)
    return True

# Input: a list of values and a target value to delete
# Output: True if the value is deleted, False if it does not exist
# This function searches through the list until the target is found.
# When it is found, the target is removed from the list.

def linear_delete(values, target):
    for index in range(len(values)):
        if values[index] == target:
            values.pop(index)
            return True
    return False