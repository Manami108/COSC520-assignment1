# Add more comments
import math
from utils.hash_functions import fnv1a64, mix64

class QuotientFilter:
    # The Quotient filter stores a short remainder of each fingerprint.
    # Metadata bits are used to organize the stored remainders.

    def __init__(self, expected_items, target_fpr=0.01, target_load=0.70):
        # Input: expected_items is the number of items to store
        #        target_fpr is the desired false positive rate
        #        target_load is the desired load factor
        # Output: a new Quotient filter
        # The number of slots and remainder bits are calculated from the expected number of items and target false positive rate.

        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not 0 < target_fpr < 1:
            raise ValueError("target_fpr must be between 0 and 1")
        if not 0 < target_load < 1:
            raise ValueError("target_load must be between 0 and 1")
        
        # This is to ensure that enough slots are available to store the expected number of items at the desired load factor.
        needed_slots = math.ceil(expected_items / target_load)
        
        # The number of slots is rounded up to the next power of two. 
        self.num_slots = 1
        while self.num_slots < max(2, needed_slots):
            self.num_slots *= 2

        self.slot_mask = self.num_slots - 1
        # The number of quotient bits is log2(number of slots).
        self.quotient_bits = self.num_slots.bit_length() - 1
        # The remainder length is selected so that the probability of two fingerprints sharing the same remainder is approximately bounded by the target false-positive rate.
        self.remainder_bits = max(1, math.ceil(math.log2(1 / target_fpr)))
        self.remainder_mask = (1 << self.remainder_bits) - 1
        
        # The total number of bits should not exceed 64. 
        if self.quotient_bits + self.remainder_bits > 64:
            raise ValueError("The Quotient filter requires more than 64 hash bits.")
        
        # One metadata bit is stored for each slot.
        metadata_bytes = (self.num_slots + 7) // 8
        self.occupied = bytearray(metadata_bytes)
        self.continuation = bytearray(metadata_bytes)
        self.shifted = bytearray(metadata_bytes)

        if self.remainder_bits <= 8:
            self.remainders = bytearray(self.num_slots)
        else:
            self.remainders = [0] * self.num_slots

        self.count = 0

    def _get_bit(self, bit_array, index):
        # Input: a bit array and slot index
        # Output: True if the selected bit is set
        # The function checks one metadata bit.
        # It finds the byte and bit corresponding to the selected slot.
        return bool(bit_array[index >> 3] & (1 << (index & 7)))

    def _set_bit(self, bit_array, index, value=True):
        # Input: a bit array, slot index, and value
        # Output: None
        # The selected metadata bit is set or cleared.

        byte_index = index >> 3
        bit_mask = 1 << (index & 7)

        if value:
            bit_array[byte_index] |= bit_mask
        else:
            bit_array[byte_index] &= (~bit_mask) & 0xFF

    def _next(self, index):
        # Input: a slot index
        # Output: the next slot index
        # The table is treated as a circular array.
        return (index + 1) & self.slot_mask

    def _previous(self, index):
        # Input: a slot index
        # Output: the previous slot index
        # The table is treated as a circular array, and it move to the previous slot.
        return (index - 1) & self.slot_mask

    def _locate(self, key):
        # Input: a username
        # Output: the quotient and remainder
        # The username is hashed and split into quotient bits and remainder bits.

        hash_value = mix64(fnv1a64(key))
        remainder = hash_value & self.remainder_mask
        quotient = (hash_value >> self.remainder_bits) & self.slot_mask
        return quotient, remainder

    def _scan(self, quotient, remainder, on_insert=False):
        # Input: a quotient, remainder, and insertion flag
        # Output: whether the fingerprint exists, its position, and the start of its run
        # The function finds the cluster and scans the run belonging to the quotient.

        run_exists = self._get_bit(self.occupied, quotient)

        if not run_exists and not on_insert:
            return False, quotient, None
        bucket = quotient
        
        # It move backwards to find the start of the cluster. 
        while self._get_bit(self.shifted, bucket):
            bucket = self._previous(bucket)
        position = bucket
        
        # It move forward to find the start of the run for the given quotient.
        while bucket != quotient:
            while True:
                position = self._next(position)
                if not self._get_bit(self.continuation, position):
                    break
            while True:
                bucket = self._next(bucket)
                if self._get_bit(self.occupied, bucket) or (
                    bucket == quotient and on_insert
                ):
                    break

        if run_exists:
            start_of_run = position

            while True:
                stored_remainder = self.remainders[position]
                if stored_remainder == remainder:
                    return True, position, start_of_run
                if stored_remainder > remainder:
                    break
                position = self._next(position)
                if not self._get_bit(self.continuation, position):
                    break
            return False, position, start_of_run
        return False, position, None

    def quotient_insert(self, key):
        # Input: a username
        # Output: True if a new fingerprint is inserted, False if it is already represented
        # The remainder is inserted into its run and existing entries are shifted when needed.
        quotient, remainder = self._locate(key)
        present, position, start_of_run = self._scan(quotient, remainder, on_insert=True)

        if present:
            return False
        if self.count >= self.num_slots:
            return False

        at_start_of_run = (start_of_run is not None and position == start_of_run)
        current_continuation = (self._get_bit(self.continuation, position) or at_start_of_run)
        current_remainder = self.remainders[position]
        current_used = (self._get_bit(self.occupied, position) or self._get_bit(self.shifted, position))
        self.remainders[position] = remainder

        if start_of_run is not None and not at_start_of_run:
            self._set_bit(self.continuation, position)
        if position != quotient:
            self._set_bit(self.shifted, position)
        start_position = position
        
        # Shift existing entries until an empty slot is found.
        while current_used:
            position = self._next(position)
            next_continuation = self._get_bit(self.continuation, position)
            next_remainder = self.remainders[position]
            next_used = (self._get_bit(self.occupied, position) or self._get_bit(self.shifted, position))

            self._set_bit(self.shifted, position)
            self._set_bit(self.continuation, position, current_continuation)
            self.remainders[position] = current_remainder
            
            current_continuation = next_continuation
            current_remainder = next_remainder
            current_used = next_used

            if position == start_position:
                raise RuntimeError("Quotient filter is full.")

        self._set_bit(self.occupied, quotient)
        self.count += 1
        return True

    def quotient_search(self, key):
        # Input: a username
        # Output: True if the username may be present, False otherwise
        # The correct run is located and searched for the username's remainder.
        quotient, remainder = self._locate(key)
        present, _, _ = self._scan(quotient, remainder)
        return present
    
