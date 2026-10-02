from utils.hash_functions import fnv1a64

class HashTable:
    def __init__(self, n):
        # Input: n is the number of items that will be stored in the hash table
        # Output: a new hash table 
        # To reduce collisions, the table capacity is selected based on an expected load factor of approximately 0.7.
        self.capacity = int(n / 0.7) + 1
        self.table = [None] * self.capacity
        
        # This is to mark deleted slots in the hash table, allowing for proper probing during searches and insertions.
        self.DELETED = object()

    def hash_function(self, key):
        # Input: a username
        # Output: an integer idx in the hash table
        # The FNV-1a algorithm is used to compute a hash for the given key.
        
        return fnv1a64(key) % self.capacity

    def hash_insert(self, key):
        # Input: a username
        # Output: True if the username was successfully inserted, False if it already exists
        # The hash function is first used to find an initial table index.
        # If the slot is already in use, the search continues through the following positions using linear probing.
        idx = self.hash_function(key)
        deleted_idx = None

        for _ in range(self.capacity):
            if self.table[idx] is None:
                if deleted_idx is not None:
                    self.table[deleted_idx] = key
                else:
                    self.table[idx] = key
                return True

            if self.table[idx] is self.DELETED:
                if deleted_idx is None:
                    deleted_idx = idx
            elif self.table[idx] == key:
                return False
            idx = (idx + 1) % self.capacity
            
        if deleted_idx is not None:
            self.table[deleted_idx] = key
            return True

        return False

    def hash_search(self, key):
        # Input: a username
        # Output: True if the username exists in the hash table, False otherwise
        # The search is begun at the hashed idx and checks subsequent slots using linear probing.
        
        idx = self.hash_function(key)

        for _ in range(self.capacity):
            if self.table[idx] is None:
                return False
            if self.table[idx] == key:
                return True
            idx = (idx + 1) % self.capacity
        return False

    def hash_delete(self, key):
        # Input: a username
        # Output: True if the username is deleted, False if it does not exist
        # The function searches for the username using linear probing.
        # When the username is found, the position is marked as deleted.
        idx = self.hash_function(key)

        for _ in range(self.capacity):
            if self.table[idx] is None:
                return False
            if self.table[idx] == key:
                self.table[idx] = self.DELETED
                return True
            idx = (idx + 1) % self.capacity
        return False
