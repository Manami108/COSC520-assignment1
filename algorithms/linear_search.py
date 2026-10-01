# Input: a list of values and a target value to search for
# Output: True if the target is found in the list, False otherwise
# To find the target value, this approach goes through the list from the beginning and compares each element with the target. 

def linear_search(values, target):
    for value in range(len(values)):
        if values[value] == target:
            return True
    return False


