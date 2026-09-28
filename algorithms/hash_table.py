class HashTable:

    def __init__(self, expected_items, max_load=0.7):

        self.capacity = int(
            expected_items / max_load
        ) + 1
        self.table = [None] * self.capacity

    def hash_function(self, key):

        hash_value = 0xcbf29ce484222325
        fnv_prime = 0x00000100000001b3

        for byte in key.encode("utf-8"):
            hash_value ^= byte
            hash_value *= fnv_prime
            # Keep the hash value within 64 bits.
            hash_value &= 0xFFFFFFFFFFFFFFFF

        return (
            hash_value
            % self.capacity
        )


    def insert(self, key):
        index = self.hash_function(key)
        for _ in range(
            self.capacity
        ):

            if self.table[index] is None:
                self.table[index] = key
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
        for _ in range(
            self.capacity
        ):
            # An empty position means that
            # the key was not inserted.
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

