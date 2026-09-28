# Still discussing the methodology. maybe FNV-1a etc. can be used. 

class HashTable:

    def __init__(self, expected_items, max_load=0.7):
        self.capacity = int(expected_items / max_load) + 1
        self.table = [None] * self.capacity
        self.count = 0

    def hash_function(self, key):
        hash_value = 0

        for char in key:
            hash_value = (
                hash_value * 31
                + ord(char)
            ) % self.capacity

        return hash_value


    def insert(self, key):
        index = self.hash_function(key)

        for _ in range(self.capacity):

            if self.table[index] is None:

                self.table[index] = key
                self.count += 1

                return True

            if self.table[index] == key:

                return False

            # Collision:
            # move to the next position.
            index = (
                index + 1
            ) % self.capacity

        raise RuntimeError(
            "Hash table is full."
        )


    def contains(self, key):
        index = self.hash_function(key)

        for _ in range(self.capacity):

            # Empty position means the key was never inserted.
            if self.table[index] is None:

                return False

            if self.table[index] == key:

                return True

            index = (
                index + 1
            ) % self.capacity

        return False
    
# Test
# table = HashTable(10)

# table.insert("Arshida")
# table.insert("Mansi")
# table.insert("Manami")

# x = "Manami"
# result = table.contains(x)

# if result:
#     print("Element is present in the hash table")
# else:
#     print("Element is not present in the hash table")


'''previous method of hash table implementation.'''
# import math
# from utils.hash_functions import fnv1a64, next_power_of_two
# class HashTable:
# # gotta think about max load
#     def __init__(self, expected_items, max_load=0.7):
#         required = max(
#             2,
#             math.ceil(expected_items / max_load)
#         )
#         self.capacity = next_power_of_two(required)
#         self.mask = self.capacity - 1
#         self.slots = [None] * self.capacity
#         self.size = 0
#     def insert(self, key):
#         index = fnv1a64(key) & self.mask
#         for _ in range(self.capacity):
#             if self.slots[index] is None:
#                 self.slots[index] = key
#                 self.size += 1
#                 return True
#             if self.slots[index] == key:
#                 return False
#             index = (index + 1) & self.mask
#         raise RuntimeError("Hash table is full.")
#     def contains(self, key):
#         index = fnv1a64(key) & self.mask
#         for _ in range(self.capacity):
#             value = self.slots[index]
#             if value is None:
#                 return False
#             if value == key:
#                 return True
#             index = (index + 1) & self.mask
#         return False