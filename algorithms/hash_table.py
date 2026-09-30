# Completed

from utils.hash_functions import fnv1a64

class HashTable:

    def __init__(self, expected_items):
        """Create a hash table for the expected number of items."""
        self.capacity = int(expected_items / 0.7) + 1
        self.table = [None] * self.capacity

    def hash_function(self, key):
        """Return the table index for a key."""
        return fnv1a64(key) % self.capacity

    def insert(self, key):
        """Insert a key using linear probing."""
        index = self.hash_function(key)

        for _ in range(self.capacity):
            if self.table[index] is None:
                self.table[index] = key
                return True

            if self.table[index] == key:
                return False

            # Linear probing after a collision.
            index = (index + 1) % self.capacity

        raise RuntimeError("Hash table is full.")

    def contains(self, key):
        """Return True if the key exists in the table."""
        index = self.hash_function(key)

        for _ in range(self.capacity):
            # Empty slot means the key is not present.
            if self.table[index] is None:
                return False

            if self.table[index] == key:
                return True

            index = (index + 1) % self.capacity

        return False
    

