# Still needs to be checked.

import math
from operator import index
import random

class CuckooFilter:

    def __init__(
        self,
        expected_items,
        bucket_size=4,
        fingerprint_bits=16,
        max_kicks=500
    ):

        self.bucket_size = bucket_size
        self.fingerprint_bits = fingerprint_bits
        self.max_kicks = max_kicks

        # Keep the filter around 90% full at most.
        needed_buckets = math.ceil(
            expected_items
            / (bucket_size * 0.90)
        )

        self.num_buckets = 1

        while self.num_buckets < max(
            2,
            needed_buckets
        ):
            self.num_buckets *= 2

        self.mask = self.num_buckets - 1

        # Each bucket is simply a list of fingerprints.
        self.buckets = [
            []
            for _ in range(self.num_buckets)
        ]


    def _hash(self, value, seed):
        hash_value = seed

        for char in str(value):

            hash_value = (
                hash_value * 31
                + ord(char)
            )

        return hash_value


    def _fingerprint(self, key):
        return (
            self._hash(key, 1)
            % (2 ** self.fingerprint_bits)
        )


    def _index1(self, key):
        return (
            self._hash(key, 2)
            & self.mask
        )


    def _index2(
        self,
        index,
        fingerprint
    ):

        fingerprint_hash = (
            self._hash(
                fingerprint,
                3
            )
            & self.mask
        )

        return (
            index
                ^ fingerprint_hash
        )


    def contains(self, key):
        fingerprint = (
            self._fingerprint(key)
        )

        index1 = self._index1(key)

        index2 = self._index2(
            index1,
            fingerprint
        )

        return (
            fingerprint
            in self.buckets[index1]
            or
            fingerprint
            in self.buckets[index2]
        )


    def insert(self, key):
        fingerprint = (
            self._fingerprint(key)
        )

        index1 = self._index1(key)

        index2 = self._index2(
            index1,
            fingerprint
        )


        # First bucket has space.
        if (
            len(self.buckets[index1])
            < self.bucket_size
        ):

            self.buckets[index1].append(
                fingerprint
            )

            return True


        # Second bucket has space.
        if (
            len(self.buckets[index2])
            < self.bucket_size
        ):

            self.buckets[index2].append(
                fingerprint
            )

            return True


        # Both buckets are full.
        # Start kicking fingerprints.
        index = random.choice(
            [index1, index2]
        )

        current_fingerprint = (
            fingerprint
        )


        for _ in range(
            self.max_kicks
        ):

            # Choose one fingerprint to remove.
            position = random.randrange(
                self.bucket_size
            )

            # Swap fingerprints.
            (
                current_fingerprint,
                self.buckets[index][position]
            ) = (
                self.buckets[index][position],
                current_fingerprint
            )

            # Find the evicted fingerprint's
            # alternate bucket.
            index = self._index2(
                index,
                current_fingerprint
            )

            # Insert if there is space.
            if (
                len(self.buckets[index])
                < self.bucket_size
            ):

                self.buckets[index].append(
                    current_fingerprint
                )

                return True


        return False