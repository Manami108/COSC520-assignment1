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
        # The constructor calculates the fingerprint size and required number of buckets.
        
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not 0 < target_fpr < 1:
            raise ValueError("target_fpr must be between 0 and 1")
        if not 0 < target_load < 1:
            raise ValueError("target_load must be between 0 and 1")
        
        # Each bucket can hold 4 fingerprints. 
        self.bucket_size = 4
        # the maximum number of relocation attempts is set to 500.
        self.max_kicks = 500
        self.rng = random.Random(0)
        # The fingerprint size is calculated. 
        self.fingerprint_bits = math.ceil(
            math.log2((2 * self.bucket_size) / target_fpr))
        
        self.fingerprint_mask = (1 << self.fingerprint_bits) - 1
        needed_buckets = math.ceil(
            expected_items
            / (self.bucket_size * target_load)
        )
        
        # The number of buckets is rounded up to the next power of two. 
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
        
        # It uses higher order bits to create a fingerprint. 
        fingerprint = ((h >> 32) & self.fingerprint_mask)
        
        # It uses lower order bits to determine the first bucket. 
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
        # Only the two candidate bucket locations are checked during lookup.

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
        
        # Try to insert without kicking first. 
        for index in (index1, index2):
            if len(self.buckets[index]) < self.bucket_size:
                self.buckets[index].append(fingerprint)
                return True
            
        # If both buckets are full, randomly choose one of the two candidate buckets to start the relocation process.
        index = self.rng.choice((index1, index2))
        current = fingerprint
        swaps = []

        for _ in range(self.max_kicks):
            
            # A random fingerprint is selected from the chosen bucket to be evicted.
            position = self.rng.randrange(self.bucket_size)
            evicted = self.buckets[index][position]
            self.buckets[index][position] = current
            # It records the previous value to allow for backtracking if the insertion fails.
            swaps.append((index, position, evicted))
            current = evicted
            # The alternative bucket for the evicted fingerprint is calculated, and the process continues.
            index = self._alt_index(index, current)

            if len(self.buckets[index]) < self.bucket_size:
                self.buckets[index].append(current)
                return True
            
        # The previous values are restored if the insertion fails after all relocation attempts.
        for bucket, position, evicted in reversed(swaps):
            self.buckets[bucket][position] = evicted
        return False
    
    def cuckoo_delete(self, key):
        # Input: a username
        # Output: True if the username is deleted, False if it is not found
        # The username is converted into a fingerprint, and both candidate buckets are searched.
        # If a matching fingerprint is found, it is removed from the bucket.
        
        fingerprint, index1, index2 = (self._locate(key))
        if fingerprint in self.buckets[index1]:
            self.buckets[index1].remove(fingerprint)
            return True
        if fingerprint in self.buckets[index2]:
            self.buckets[index2].remove(fingerprint)
            return True
        return False