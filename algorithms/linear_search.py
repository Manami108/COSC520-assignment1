def linear_search(values, target):
    for value in range(len(values)):
        if values[value] == target:
            return True
    return False

# Test
# mylist= ["Manami", "Mansi", "Arshida"]
# x = "Mansi"
# result = linear_search(mylist, x)

# if result:
#     print("Element is present in the list")
# else:
#     print("Element is not present in the list")