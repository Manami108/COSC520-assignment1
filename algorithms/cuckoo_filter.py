# Completed 
import math
import random

from utils.hash_functions import fnv1a64, mix64

class CuckooFilter:
    def __init__(self, expected_items, target_fpr=0.01, target_load=0.90):
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not 0 < target_fpr < 1:
            raise ValueError("target_fpr must be between 0 and 1")
        if not 0 < target_load < 1:
            raise ValueError("target_load must be between 0 and 1")
        
        self.bucket_size = 4
        self.max_kicks = 500
        self.rng = random.Random(0)
        self.fingerprint_bits = math.ceil(
            math.log2((2 * self.bucket_size) / target_fpr))
        
        self.fingerprint_mask = (1 << self.fingerprint_bits) - 1
    
        needed_buckets = math.ceil(
            expected_items
            / (self.bucket_size * target_load)
        )

        self.num_buckets = 1
        while self.num_buckets < max(2, needed_buckets):
            self.num_buckets *= 2
        self.mask = self.num_buckets - 1
        self.buckets = [
            []
            for _ in range(self.num_buckets)
        ]

    def _locate(self, key):
        h = mix64(fnv1a64(key))

        fingerprint = ((h >> 32) & self.fingerprint_mask)

        index1 = h & self.mask
        index2 = self._alt_index(index1, fingerprint)
        return fingerprint, index1, index2

    def _alt_index(self, index, fingerprint):
        offset = mix64(fingerprint) & self.mask

        if offset == 0:
            offset = 1
        return index ^ offset

    def contains(self, key):
        fingerprint, index1, index2 = self._locate(key)
        return (fingerprint in self.buckets[index1]
            or fingerprint in self.buckets[index2])

    def insert(self, key):
        fingerprint, index1, index2 = self._locate(key)

        for index in (index1, index2):
            if len(self.buckets[index]) < self.bucket_size:
                self.buckets[index].append(fingerprint)
                return True

        index = self.rng.choice((index1, index2))
        current = fingerprint
        swaps = []

        for _ in range(self.max_kicks):
            position = self.rng.randrange(self.bucket_size)
            evicted = self.buckets[index][position]
            self.buckets[index][position] = current
            swaps.append((index, position, evicted))
            current = evicted
            index = self._alt_index(index, current)

            if len(self.buckets[index]) < self.bucket_size:
                self.buckets[index].append(current)
                return True

        for bucket, position, evicted in reversed(swaps):
            self.buckets[bucket][position] = evicted
        return False