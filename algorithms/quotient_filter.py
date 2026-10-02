import math
from utils.hash_functions import fnv1a64, mix64

class QuotientFilter:
    # The Quotient filter stores a short remainder of each fingerprint.
    # Metadata bits are used to organize the stored remainders.

    def __init__(self, n, p=0.01, load=0.70):
        # Input: n is the number of items to store
        #        p is the desired false positive rate
        #        load is the desired load factor
        # Output: a new Quotient filter

        # This is to ensure that enough slots are available to store the expected number of items at the desired load factor.
        n = math.ceil(n / load)
        
        # The number of slots is rounded up to the next power of two. 
        self.num_slots = 2
        while self.num_slots < n:
            self.num_slots *= 2

        self.mask = self.num_slots - 1
        # The remainder length is selected so that the probability of two fingerprints sharing the same remainder is approximately bounded by the target false-positive rate.
        # r = ceil(log2(1 / p)).
        self.r_bits = max(1, math.ceil(math.log2(1 / p)))
        self.r_mask = (1 << self.r_bits) - 1
        
        # It stores remainders and metadata.
        self.rs = [0] * self.num_slots
        self.occupied = [False] * self.num_slots
        self.continuation = [False] * self.num_slots
        self.shifted = [False] * self.num_slots

        self.count = 0

    def _next(self, idx):
        # Input: a slot index
        # Output: the next slot index
        # The table is treated as a circular array.
        return (idx + 1) & self.mask

    def _previous(self, idx):
        # Input: a slot index
        # Output: the previous slot index
        # The table is treated as a circular array, and it move to the previous slot.
        return (idx - 1) & self.mask

    def _locate(self, key):
        # Input: a username
        # Output: the quotient and remainder
        # The username is hashed and split into quotient bits and remainder bits.
        h = mix64(fnv1a64(key))
        r = h & self.r_mask
        q = (h >> self.r_bits) & self.mask
        return q, r

    def _scan(self, q, r, on_insert=False):
        # Input: a quotient, remainder, and insertion flag
        # Output: whether the fingerprint exists, its position, and the start of its run
        # The function finds the cluster and scans the run belonging to the quotient.
        run_exists = self.occupied[q]
        if not run_exists and not on_insert:
            return False, q, None
        bucket = q
        
        # It move backwards to find the start of the cluster. 
        while self.shifted[bucket]:
            bucket = self._previous(bucket)
        pos = bucket
        
        # It finds the run for this quotient.
        while bucket != q:
            pos = self._next(pos)
            while self.continuation[pos]:
                pos = self._next(pos)
            bucket = self._next(bucket)
            while not self.occupied[bucket]:
                if bucket == q and on_insert:
                    break
                bucket = self._next(bucket)

        if not run_exists:
            return False, pos, None
        start_of_run = pos

        # It searches the run for the requested remainder, and it is stored in sorted order.
        while True:
            if self.rs[pos] == r:
                return True, pos, start_of_run
            if self.rs[pos] > r:
                break
            pos = self._next(pos)
            if not self.continuation[pos]:
                break
        return False, pos, start_of_run


    def quotient_insert(self, key):
        # Input: a username
        # Output: True if a new fingerprint is inserted, False if it is already represented or cannot be inserted.
        # The remainder is inserted into its run and existing entries are shifted when needed.
        q, r = self._locate(key)
        present, pos, start = self._scan(q, r, on_insert=True)

        if present:
            return False
        if self.count >= self.num_slots:
            return False

        at_start = start is not None and pos == start
        current_continuation = (self.continuation[pos] or at_start)
        current_r = self.rs[pos]
        current_used = (self.occupied[pos] or self.shifted[pos])
        self.rs[pos] = r
        if start is not None and not at_start:
            self.continuation[pos] = True
        if pos != q:
            self.shifted[pos] = True
        first_pos = pos

        # It shifts existing values until an empty slot is found.
        while current_used:
            pos = self._next(pos)
            next_continuation = self.continuation[pos]
            next_r = self.rs[pos]
            next_used = (self.occupied[pos] or self.shifted[pos])
            
            self.shifted[pos] = True
            self.continuation[pos] = current_continuation
            self.rs[pos] = current_r

            current_continuation = next_continuation
            current_r = next_r
            current_used = next_used

            if pos == first_pos:
                return False

        self.occupied[q] = True
        self.count += 1
        return True

    def quotient_search(self, key):
        # Input: a username
        # Output: True if its fingerprint is represented, false otherwise. 
        q, r = self._locate(key)
        present, _, _ = self._scan(q, r)
        return present
    