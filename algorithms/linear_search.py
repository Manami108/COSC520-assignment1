# To find the target value, this approach goes through the list from the beginning and compares each element with the target. 
# Once a match is found, it returns True. 
# If the entire list is checked and match is not found, it returns False.

def linear_search(values, target):
    for value in range(len(values)):
        if values[value] == target:
            return True
    return False


