import math

from utils.hash_functions import fnv1a64, next_power_of_two


# ============================================================
# 3. HASH TABLE
# ============================================================

class HashTable:
    """
    Exact hash table implemented using open addressing
    and linear probing.

    Python dictionary/set implementations are not used.
    """

    def __init__(self, expected_items, max_load=0.65):

        required = max(
            2,
            math.ceil(expected_items / max_load)
        )

        self.capacity = next_power_of_two(required)

        self.mask = self.capacity - 1

        self.slots = [None] * self.capacity

        self.size = 0


    def insert(self, key):
        """
        Input:
            key: username

        Output:
            True if newly inserted
            False if username already exists

        Description:
            Uses linear probing when collisions occur.
        """

        index = fnv1a64(key) & self.mask

        for _ in range(self.capacity):

            if self.slots[index] is None:

                self.slots[index] = key
                self.size += 1

                return True

            if self.slots[index] == key:

                return False

            index = (index + 1) & self.mask

        raise RuntimeError("Hash table is full.")


    def contains(self, key):
        """
        Input:
            key: username

        Output:
            True if key exists, otherwise False
        """

        index = fnv1a64(key) & self.mask

        for _ in range(self.capacity):

            value = self.slots[index]

            if value is None:
                return False

            if value == key:
                return True

            index = (index + 1) & self.mask

        return False