import math
from utils.hash_functions import fnv1a64, djb2_64, mix64

class BloomFilter:
    # Rather than storing each string directly, the Bloom filter records information in a bit array.
    def __init__(self, n, p=0.01):
        # Input: n is the number of items to sture 
        #        p is the desired false positive rate
        # Output: a new Bloom filter
        # The Bloom filter parameters are calculated from two inputs: the expected number of stored items and the target false-positive rate.
        # Then, it determines the size of the bit array and the number of hash functions.

        # The bit-array size m is computed as:
        # m = -n ln(p) / (ln(2))^2
        self.size = math.ceil(-(n * math.log(p)) / (math.log(2) ** 2))
        # The number of hash functions k is computed as:
        # k = (m/n) ln(2)
        self.hash_count = max(1, round((self.size / n) * math.log(2)))
        self.bit_array = [0] * self.size

    def _hashes(self, key):
        # Input: a username
        # Output: a sequence of hash idxs in the bit array
        # Two different base hashes are first computed, and their values are then, combined to determine each required idx.
        h1 = mix64(fnv1a64(key))
        h2 = mix64(djb2_64(key)) | 1
        # Double hasing generates idx i as:
        # (h1 + i * h2) mod m
        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size
 
    def bloom_insert(self, key):
        # Input: a username
        # Output: None
        # Each hash position corresponding to the key is set to 1.
        for idx in self._hashes(key):
            self.bit_array[idx] = 1

    def bloom_search(self, key):
        # Input: a username
        # Output: True if the username may be present, False otherwise
        # If at least one required bit is 0, the key is definitely not present.
        # If all required bits are 1, the key may be present, but a false positive is possible.
        for idx in self._hashes(key):
            if self.bit_array[idx] == 0:
                return False
        return True
