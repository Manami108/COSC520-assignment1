import math
import random

from utils.hash_functions import (
    fnv1a64,
    mix64,
    next_power_of_two
)


# ============================================================
# 5. CUCKOO FILTER
# ============================================================

class CuckooFilter:
    """
    Cuckoo filter using two candidate buckets per
    fingerprint.

    Each username is represented by a small fingerprint
    rather than storing the entire username.
    """

    def __init__(
        self,
        expected_items,
        bucket_size=4,
        fingerprint_bits=16,
        target_load=0.90,
        max_kicks=500,
        seed=7
    ):

        if expected_items <= 0:
            raise ValueError(
                "expected_items must be positive"
            )

        needed = math.ceil(
            expected_items
            / (
                bucket_size
                * target_load
            )
        )

        self.num_buckets = (
            next_power_of_two(
                max(2, needed)
            )
        )

        self.bucket_mask = (
            self.num_buckets - 1
        )

        self.bucket_size = bucket_size

        self.fp_mask = (
            (1 << fingerprint_bits) - 1
        )

        self.max_kicks = max_kicks

        # Fingerprint 0 means empty.
        self.slots = (
            [0]
            * (
                self.num_buckets
                * bucket_size
            )
        )

        self.size = 0

        self.rng = random.Random(seed)


    def _fingerprint(self, key):
        """
        Return a non-zero fingerprint for key.
        """

        fp = (
            mix64(
                fnv1a64(
                    key,
                    0xC0FFEE
                )
            )
            & self.fp_mask
        )

        if fp == 0:
            fp = 1

        return fp


    def _index1(self, key):
        """
        Calculate the first candidate bucket.
        """

        return (
            mix64(
                fnv1a64(
                    key,
                    0x12345678
                )
            )
            & self.bucket_mask
        )


    def _alternate_index(
        self,
        index,
        fingerprint
    ):
        """
        Calculate the second candidate bucket.

        XOR is used so applying the operation again
        returns to the original bucket.
        """

        delta = (
            mix64(fingerprint)
            & self.bucket_mask
        )

        if delta == 0:
            delta = 1

        return index ^ delta


    def _bucket_contains(
        self,
        index,
        fingerprint
    ):
        """
        Check whether a fingerprint exists in one bucket.
        """

        base = (
            index
            * self.bucket_size
        )

        for offset in range(
            self.bucket_size
        ):

            if (
                self.slots[
                    base + offset
                ]
                == fingerprint
            ):
                return True

        return False


    def _place_if_empty(
        self,
        index,
        fingerprint
    ):
        """
        Insert fingerprint into the first empty position
        in a bucket.
        """

        base = (
            index
            * self.bucket_size
        )

        for offset in range(
            self.bucket_size
        ):

            slot = base + offset

            if self.slots[slot] == 0:

                self.slots[slot] = (
                    fingerprint
                )

                return True

        return False


    def contains(self, key):
        """
        Input:
            key: username

        Output:
            False -> definitely absent
            True  -> possibly present
        """

        fp = self._fingerprint(key)

        i1 = self._index1(key)

        i2 = self._alternate_index(
            i1,
            fp
        )

        return (
            self._bucket_contains(
                i1,
                fp
            )
            or
            self._bucket_contains(
                i2,
                fp
            )
        )


    def insert(self, key):
        """
        Insert the fingerprint into the filter.

        If both candidate buckets are full,
        fingerprints are relocated.

        If relocation fails, changes are rolled back.
        """

        fp = self._fingerprint(key)

        i1 = self._index1(key)

        i2 = self._alternate_index(
            i1,
            fp
        )

        if (
            self._place_if_empty(
                i1,
                fp
            )
            or
            self._place_if_empty(
                i2,
                fp
            )
        ):

            self.size += 1
            return True


        # Both buckets are full.
        index = (
            i1
            if self.rng.randrange(2) == 0
            else i2
        )

        current_fp = fp

        swaps = []


        for _ in range(
            self.max_kicks
        ):

            slot = (
                index
                * self.bucket_size
                + self.rng.randrange(
                    self.bucket_size
                )
            )

            old_fp = (
                self.slots[slot]
            )

            self.slots[slot] = (
                current_fp
            )

            swaps.append(
                (
                    slot,
                    old_fp
                )
            )

            current_fp = old_fp

            index = (
                self._alternate_index(
                    index,
                    current_fp
                )
            )


            if self._place_if_empty(
                index,
                current_fp
            ):

                self.size += 1

                return True


        # Restore the original filter if insertion failed.
        for slot, old_fp in reversed(
            swaps
        ):

            self.slots[slot] = old_fp


        return False


    def delete(self, key):
        """
        Delete one matching fingerprint if present.

        Returns:
            True if deleted
            False otherwise
        """

        fp = self._fingerprint(key)

        i1 = self._index1(key)

        i2 = self._alternate_index(
            i1,
            fp
        )


        for index in (
            i1,
            i2
        ):

            base = (
                index
                * self.bucket_size
            )

            for offset in range(
                self.bucket_size
            ):

                slot = base + offset

                if (
                    self.slots[slot]
                    == fp
                ):

                    self.slots[slot] = 0

                    self.size -= 1

                    return True


        return False