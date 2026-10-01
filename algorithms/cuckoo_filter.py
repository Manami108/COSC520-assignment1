# Completed 
import math
import random

from utils.hash_functions import fnv1a64, mix64

class CuckooFilter:
    """
    This class implements a Cuckoo filter for probabilistic membership
    testing. Each item is represented by a compact fingerprint that can
    be stored in one of two possible buckets. When both buckets are full,
    existing fingerprints may be relocated to create space.
    """
    def __init__(self, expected_items, target_fpr=0.01, target_load=0.90):

        """
        This method creates a Cuckoo filter for the expected number of
        items. It calculates the fingerprint size and the number of
        buckets required based on the target false-positive rate and
        target load factor. The number of buckets is rounded up to a
        power of two.
        """
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
        """
        This method calculates the fingerprint and the two possible bucket
        locations for a key. The first bucket is obtained from the key's
        hash value, and the second bucket is calculated from the first
        bucket and the fingerprint. It returns the fingerprint and both
        bucket indices.
        """        

        h = mix64(fnv1a64(key))

        fingerprint = ((h >> 32) & self.fingerprint_mask)

        index1 = h & self.mask
        index2 = self._alt_index(index1, fingerprint)
        return fingerprint, index1, index2

    def _alt_index(self, index, fingerprint):
        
        """
        This method calculates the alternative bucket index for a
        fingerprint. It combines the current bucket index with a
        hash-derived offset using the XOR operation. It returns the
        other possible bucket for the fingerprint.
        """
        offset = mix64(fingerprint) & self.mask

        if offset == 0:
            offset = 1
        return index ^ offset

    def cuckoo_search(self, key):
        
        """
        This method checks whether a key may exist in the Cuckoo filter.
        It calculates the key's fingerprint and checks both possible
        buckets. It returns True if the fingerprint appears in either
        bucket and False otherwise. Because only fingerprints are stored,
        a True result may be a false positive.
        """
        fingerprint, index1, index2 = self._locate(key)
        return (fingerprint in self.buckets[index1]
            or fingerprint in self.buckets[index2])

    def cuckoo_insert(self, key):
        
        """
        This method inserts a key into the Cuckoo filter. It first tries
        to place the fingerprint into either of its two possible buckets.
        If both buckets are full, it repeatedly evicts an existing
        fingerprint and moves it to its alternative bucket. It returns
        True when the insertion succeeds and False if no available
        position can be found after the maximum number of attempts.
        """
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
    
    def cuckoo_delete(self, key):
        """
        Input: a username
        Output: True if the username is deleted, False if it is not found

        This method calculates the username's fingerprint and checks
        both possible buckets. If the fingerprint is found, it is
        removed from the corresponding bucket.
        """

        fingerprint, index1, index2 = (self._locate(key))
        if fingerprint in self.buckets[index1]:
            self.buckets[index1].remove(fingerprint)
            return True
        if fingerprint in self.buckets[index2]:
            self.buckets[index2].remove(fingerprint)
            return True
        return False