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

# Test
# mylist = ["Mansi", "Arshida", "Manami"]       
# x = "Manami"
# result = binary_search(mylist, x)

# if result:
#     print("Element is present in the list")
# else:
#     print("Element is not present in the list")
    