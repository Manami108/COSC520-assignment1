import math

from utils.hash_functions import fnv1a64, djb2_64


class BloomFilter:

    def __init__(self, expected_items, target_fpr=0.01):
        """Create a Bloom filter for the expected number of items."""
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")

        if not 0 < target_fpr < 1:
            raise ValueError("target_fpr must be between 0 and 1")

        n = expected_items
        p = target_fpr

        # Optimal number of bits:
        # m = -(n * ln(p)) / (ln(2)^2)
        self.size = math.ceil(
            -(n * math.log(p)) / (math.log(2) ** 2)
        )

        # Optimal number of hash positions:
        # k = (m / n) * ln(2)
        self.hash_count = max(
            1,
            round((self.size / n) * math.log(2))
        )

        # Store 8 Bloom-filter bits in each byte.
        self.bit_array = bytearray((self.size + 7) // 8)

    def _hashes(self, key):
        """
        Generate bit positions using double hashing.

        position_i = (h1 + i * h2) mod m
        """
        h1 = fnv1a64(key)
        h2 = djb2_64(key)

        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size

    def add(self, key):
        """Add a key to the Bloom filter."""
        for position in self._hashes(key):
            byte_index = position // 8
            bit_index = position % 8

            self.bit_array[byte_index] |= 1 << bit_index

    def contains(self, key):
        """Return True if the key may be present."""
        for position in self._hashes(key):
            byte_index = position // 8
            bit_index = position % 8

            if not self.bit_array[byte_index] & (1 << bit_index):
                return False

        return True