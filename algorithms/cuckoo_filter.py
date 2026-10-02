# Completed 
import math
import random

from utils.hash_functions import fnv1a64, mix64

class CuckooFilter:
    # Rather than storing the complete item, the Cuckoo filter keeps a fingerprint. 
    # Two candidate buckets are available for each fingerprint, and relocation is used when neither bucket has an empty slot.
    
    def __init__(self, expected_items, target_fpr=0.01, target_load=0.90):
        # Input: expected_items is the number of items to store
        #        target_fpr is the desired false positive rate
        #        target_load is the desired load factor for the filter
        # Output: a new Cuckoo filter
        # To find the target value, this function goes through the list from the beginning and compares each element with the target. 
        
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
        # Input: a username
        # Output: the fingerprint and two possible bucket indices
        # Using the key hash, the function finds the first possible bucket.
        # It then combines this index with the fingerprint to obtain the second bucket.
        h = mix64(fnv1a64(key))

        fingerprint = ((h >> 32) & self.fingerprint_mask)

        index1 = h & self.mask
        index2 = self._alt_index(index1, fingerprint)
        return fingerprint, index1, index2

    def _alt_index(self, index, fingerprint):
        # Input: a bucket index and a fingerprint
        # Output: the alternative bucket index
        # A hash-based offset is combined with the bucket index using XOR.
        # This allows the algorithm to move from one candidate bucket to the other.

        offset = mix64(fingerprint) & self.mask

        if offset == 0:
            offset = 1
        return index ^ offset

    def cuckoo_search(self, key):
        # Input: a username
        # Output: True if the username is found in either possible bucket, False otherwise
        # Only the two candidate bucket locations are checked during lookup because the fingerprint can only be in one of them.
        
        fingerprint, index1, index2 = self._locate(key)
        return (fingerprint in self.buckets[index1]
            or fingerprint in self.buckets[index2])

    def cuckoo_insert(self, key):
        # Input: a username
        # Output: True if the username is inserted, False if no available position can be found
        # An available position in either candidate bucket is used first.
        # Otherwise, the filter starts relocating fingerprints by repeatedly evicting one and placing it in its alternative bucket. 
        # The process stops with failure if all relocation attempts are exhausted.
        
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
        # Input: a username
        # Output: True if the username is deleted, False if it is not found
        # The username is converted into a fingerprint, and both candidate buckets are searched.
        # If a matching fingerprint is found, it is removed from the appropriate bucket.

        fingerprint, index1, index2 = (self._locate(key))
        if fingerprint in self.buckets[index1]:
            self.buckets[index1].remove(fingerprint)
            return True
        if fingerprint in self.buckets[index2]:
            self.buckets[index2].remove(fingerprint)
            return True
        return False