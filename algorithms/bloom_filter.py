import math
from utils.hash_functions import fnv1a64, djb2_64, mix64

class BloomFilter:
    # Rather than storing each string directly, the Bloom filter records information in a bit array.
    def __init__(self, expected_items, target_fpr=0.01):
        # Input: expected_items is the number of items to sture 
        #        target_fpr is the desired false positive rate
        # Output: a new Bloom filter
        # The Bloom filter parameters are calculated from two inputs: the expected number of stored items and the target false-positive rate.
        # Then, it determines the size of the bit array and the number of hash functions.
        
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not 0 < target_fpr < 1:
            raise ValueError("target_fpr must be between 0 and 1")

        n = expected_items
        
        # The bit-array size m is computed as:
        # m = -n ln(p) / (ln(2))^2
        self.size = math.ceil(-(n * math.log(target_fpr)) / (math.log(2) ** 2))
        # The number of hash functions k is computed as:
        # k = (m/n) ln(2)
        self.hash_count = max(1, round((self.size / n) * math.log(2)))
        self.bit_array = bytearray((self.size + 7) // 8)

    def _hashes(self, key):
        # Input: a username
        # Output: a sequence of hash positions in the bit array
        # Two different base hashes are first computed, and their values are then, combined to determine each required position.
        h1 = mix64(fnv1a64(key))
        h2 = mix64(djb2_64(key)) | 1
        # Double hasing generates position i as:
        # (h1 + i * h2) mod m
        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size
 
    def bloom_insert(self, key):
        # Input: a username
        # Output: None
        # Each hash position corresponding to the key is set to 1.
        
        # position >> 3 selects the byte containing the target bit.
        # position & 7 selects the bit position within that byte.
        for position in self._hashes(key):
            self.bit_array[position >> 3] |= 1 << (position & 7)

    def bloom_search(self, key):
        # Input: a username
        # Output: True if the username may be present, False otherwise
        # If at least one required bit is 0, the key is definitely not present.
        # If all required bits are 1, the key may be present, but a false positive is possible.
        
        for position in self._hashes(key):
            if not self.bit_array[position >> 3] & (1 << (position & 7)):
                return False
        return True
