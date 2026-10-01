# Completed

from utils.hash_functions import fnv1a64

class HashTable:

    def __init__(self, expected_items):
        if expected_items < 0:
            raise ValueError("expected_items must be nonnegative")
 
        self.capacity = int(expected_items / 0.7) + 1
        self.table = [None] * self.capacity

    def hash_function(self, key):
        return fnv1a64(key) % self.capacity

    def insert(self, key):
        index = self.hash_function(key)

        for _ in range(self.capacity):
            if self.table[index] is None:
                self.table[index] = key
                return True
            if self.table[index] == key:
                return False
            index = (index + 1) % self.capacity
        raise RuntimeError("Hash table is full.")

    def contains(self, key):
        index = self.hash_function(key)

        for _ in range(self.capacity):
            if self.table[index] is None:
                return False
            if self.table[index] == key:
                return True
            index = (index + 1) % self.capacity
        return False
    

