# Completed 
import math
from utils.hash_functions import fnv1a64, djb2_64, mix64

class BloomFilter:

    def __init__(self, expected_items, target_fpr=0.01):
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not 0 < target_fpr < 1:
            raise ValueError("target_fpr must be between 0 and 1")

        n = expected_items
        self.size = math.ceil(-(n * math.log(target_fpr)) / (math.log(2) ** 2))
        self.hash_count = max(1, round((self.size / n) * math.log(2)))
 
        self.bit_array = bytearray((self.size + 7) // 8)

    def _hashes(self, key):
        h1 = mix64(fnv1a64(key))
        h2 = mix64(djb2_64(key)) | 1
        
        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size
 
    def add(self, key):
        for position in self._hashes(key):
            self.bit_array[position >> 3] |= 1 << (position & 7)

    def contains(self, key):
        for position in self._hashes(key):
            if not self.bit_array[position >> 3] & (1 << (position & 7)):
                return False
        return True