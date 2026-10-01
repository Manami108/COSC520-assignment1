
from matplotlib.table import table

from utils.hash_functions import fnv1a64

# Input: a list of usernames and a target username to search for
# Output: True if the target username is found in the list, False otherwise

class HashTable:
    def __init__(self, expected_items):
        # Input: expected_items is the number of items that will be stored in the hash table
        # Output: a new hash table 
        # To reduce collisions, the table capacity is selected based on an expected load factor of approximately 0.7.
        
        if expected_items < 0:
            raise ValueError("expected_items must be nonnegative")
 
        self.capacity = int(expected_items / 0.7) + 1
        self.table = [None] * self.capacity

    def hash_function(self, key):
        # Input: a username
        # Output: an integer index in the hash table
        # The FNV-1a algorithm is used to compute a hash for the given key.
        
        return fnv1a64(key) % self.capacity

    def insert(self, key):
        # Input: a username
        # Output: True if the username was successfully inserted, False if it already exists
        # The hash function is first used to find an initial table index.
        # If the slot is already in use, the search continues through the following positions using linear probing.
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
        # Input: a username
        # Output: True if the username exists in the hash table, False otherwise
        # it moves through the following slots in the same order as the insertion procedure.
        index = self.hash_function(key)

        for _ in range(self.capacity):
            if self.table[index] is None:
                return False
            if self.table[index] == key:
                return True
            index = (index + 1) % self.capacity
        return False
    

