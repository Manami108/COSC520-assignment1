# Still needs to be checked.

import math
import random

from utils.hash_functions import fnv1a64, djb2_64


class CuckooFilter:

    def __init__(self, expected_items, target_fpr=0.01):
        """Create a Cuckoo filter for the expected number of items."""
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")

        if not 0 < target_fpr < 1:
            raise ValueError("target_fpr must be between 0 and 1")

        self.bucket_size = 4
        self.max_kicks = 500
        self.rng = random.Random(0)

        self.fingerprint_bits = math.ceil(
            math.log2((2 * self.bucket_size) / target_fpr)
        )

        target_load = 0.90
        needed_buckets = math.ceil(
            expected_items / (self.bucket_size * target_load)
        )

        # A power of two allows XOR to find the alternate bucket.
        self.num_buckets = 1
        while self.num_buckets < max(2, needed_buckets):
            self.num_buckets *= 2

        self.mask = self.num_buckets - 1

        self.buckets = [
            [] for _ in range(self.num_buckets)
        ]

    def _fingerprint(self, key):
        """Create a short fingerprint for a key."""
        hash_value = fnv1a64("fingerprint:" + key)
        return hash_value & ((1 << self.fingerprint_bits) - 1)

    def _index1(self, key):
        """Return the first bucket index."""
        return fnv1a64(key) & self.mask

    def _index2(self, index, fingerprint):
        """Return the alternate bucket index."""
        fingerprint_hash = djb2_64(fingerprint) & self.mask
        return index ^ fingerprint_hash

    def contains(self, key):
        """Return True if the key may be present."""
        fingerprint = self._fingerprint(key)
        index1 = self._index1(key)
        index2 = self._index2(index1, fingerprint)

        return (
            fingerprint in self.buckets[index1]
            or fingerprint in self.buckets[index2]
        )

    def insert(self, key):
        """Insert a key into the Cuckoo filter."""
        fingerprint = self._fingerprint(key)
        index1 = self._index1(key)
        index2 = self._index2(index1, fingerprint)

        # Insert directly if either bucket has space.
        if len(self.buckets[index1]) < self.bucket_size:
            self.buckets[index1].append(fingerprint)
            return True

        if len(self.buckets[index2]) < self.bucket_size:
            self.buckets[index2].append(fingerprint)
            return True

        # Both buckets are full, so start relocating fingerprints.
        index = self.rng.choice([index1, index2])
        current_fingerprint = fingerprint
        swaps = []

        for _ in range(self.max_kicks):
            position = self.rng.randrange(self.bucket_size)

            evicted = self.buckets[index][position]
            self.buckets[index][position] = current_fingerprint
            swaps.append((index, position, evicted))

            current_fingerprint = evicted
            index = self._index2(index, current_fingerprint)

            if len(self.buckets[index]) < self.bucket_size:
                self.buckets[index].append(current_fingerprint)
                return True

        # Restore the filter if insertion fails.
        for bucket, position, evicted in reversed(swaps):
            self.buckets[bucket][position] = evicted

        return False