import math
import random

from utils.hash_functions import fnv1a64, mix64

class CuckooFilter:
    # Rather than storing the complete item, the Cuckoo filter keeps a fingerprint. 
    # Two candidate buckets are available for each fingerprint, and relocation is used when neither bucket has an empty slot.
    
    def __init__(self, n, p=0.01):
        # Input: n is the number of items to store
        #        p is the desired false positive rate
        #        target_load is the desired load factor for the filter
        # Output: a new Cuckoo filter
        # The constructor calculates the fingerprint size and required number of buckets.

        # Each bucket can hold 4 fingerprints. 
        self.bucket_size = 4
        # the maximum number of relocation attempts is set to 500.
        self.max_kicks = 500
        self.rng = random.Random(0)
        # The fingerprint size is calculated. 
        bits = math.ceil(
            math.log2((2 * self.bucket_size) / p))
        
        self.fp_mask = (1 << bits) - 1
        needed = math.ceil(n / (self.bucket_size * 0.9))
        
        # The number of buckets is rounded up to the next power of two. 
        self.num_buckets = 2
        while self.num_buckets < needed:
            self.num_buckets *= 2
        self.mask = self.num_buckets - 1
        self.buckets = [[] for _ in range(self.num_buckets)]

    def _locate(self, key):
        # Input: a username
        # Output: the fingerprint and two possible bucket indices
        # Using the key hash, the function finds the first possible bucket.
        # It then combines this index with the fingerprint to obtain the second bucket.
        h = mix64(fnv1a64(key))
        
        # It uses higher order bits to create a fingerprint. 
        fp = (h >> 32) & self.fp_mask
        
        # It uses lower order bits to determine the first bucket. 
        idx1 = h & self.mask
        idx2 = self._alt_idx(idx1, fp)
        return fp, idx1, idx2

    def _alt_idx(self, idx, fp):
        # Input: a bucket index and a fingerprint
        # Output: the alternative bucket index
        # A hash-based offset is combined with the bucket index using XOR.
        # This allows the algorithm to move from one candidate bucket to the other.

        offset = mix64(fp) & self.mask

        if offset == 0:
            offset = 1
        return idx ^ offset

    def cuckoo_search(self, key):
        # Input: a username
        # Output: True if the username is found in either possible bucket, False otherwise
        # Only the two candidate bucket locations are checked during lookup.

        fp, idx1, idx2 = self._locate(key)
        return (fp in self.buckets[idx1]
            or fp in self.buckets[idx2])

    def cuckoo_insert(self, key):
        # Input: a username
        # Output: True if the username is inserted, False if no available position can be found
        # An available position in either candidate bucket is used first.
        # Otherwise, the filter starts relocating fingerprints by repeatedly evicting one and placing it in its alternative bucket. 
        # The process stops with failure if all relocation attempts are exhausted.
        
        fp, idx1, idx2 = self._locate(key)
        
        # Try to insert without kicking first. 
        if len(self.buckets[idx1]) < self.bucket_size:
            self.buckets[idx1].append(fp)
            return True
        if len(self.buckets[idx2]) < self.bucket_size:
            self.buckets[idx2].append(fp)
            return True

            
        # If both buckets are full, randomly choose one of the two candidate buckets to start the relocation process.
        idx = self.rng.choice((idx1, idx2))
        current = fp
        swaps = []

        for _ in range(self.max_kicks):
            
            # A random fingerprint is selected from the chosen bucket to be evicted.
            pos = self.rng.randrange(self.bucket_size)
            evicted = self.buckets[idx][pos]
            self.buckets[idx][pos] = current
            # It records the previous value to allow for backtracking if the insertion fails.
            swaps.append((idx, pos, evicted))
            current = evicted
            # The alternative bucket for the evicted fingerprint is calculated, and the process continues.
            idx = self._alt_idx(idx, current)

            if len(self.buckets[idx]) < self.bucket_size:
                self.buckets[idx].append(current)
                return True
            
        # The previous values are restored if the insertion fails after all relocation attempts.
        for bucket, pos, evicted in reversed(swaps):
            self.buckets[bucket][pos] = evicted
        return False
    
    def cuckoo_delete(self, key):
        # Input: a username
        # Output: True if the username is deleted, False if it is not found
        # The username is converted into a fingerprint, and both candidate buckets are searched.
        # If a matching fingerprint is found, it is removed from the bucket.
        fp, idx1, idx2 = self._locate(key)
        if fp in self.buckets[idx1]:
            self.buckets[idx1].remove(fp)
            return True
        if fp in self.buckets[idx2]:
            self.buckets[idx2].remove(fp)
            return True
        return False