import math

class BloomFilter:

    def __init__(self, expected_items):
        # Number of bits:
        # m = -n ln(p) / (ln 2)^2
        n = expected_items
        p = 0.01

        self.size = math.ceil(
            -n * math.log(p)
            / (math.log(2) ** 2)
        )

        # Number of hash functions:
        # k = (m / n) ln 2
        self.hash_count = round(
            (self.size / n)
            * math.log(2)
        )

        # Initially every bit is 0.
        self.bit_array = [0] * self.size


    def hash_function(self, key, seed):
        hash_value = seed
        
        for char in key:
            hash_value = (
                hash_value * 31
                + ord(char)
            ) % self.size
        return hash_value


    def add(self, key):
        for i in range(self.hash_count):
            position = self.hash_function(
                key,
                i + 1
            )
            self.bit_array[position] = 1
            

    def contains(self, key):
        for i in range(self.hash_count):
            position = self.hash_function(
                key,
                i + 1
            )
            if self.bit_array[position] == 0:
                return False
        return True
    
 # Test
bloom = BloomFilter(10)

bloom.add("Arshida")
bloom.add("Mansi")
bloom.add("Manami")

x = "John"
result = bloom.contains(x)

if result:
    print("Element may be present in the Bloom filter")
else:
    print("Element is not present in the Bloom filter")   