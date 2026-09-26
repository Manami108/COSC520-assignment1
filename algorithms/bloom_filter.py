import math

from utils.hash_functions import fnv1a64, djb2_64


# ============================================================
# 4. BLOOM FILTER
# ============================================================

class BloomFilter:
    """
    Bloom filter implemented using a manually managed
    bit vector.

    No Bloom-filter library is used.
    """

    def __init__(
        self,
        expected_items,
        false_positive_rate=0.01
    ):

        if expected_items <= 0:
            raise ValueError(
                "expected_items must be positive"
            )

        if not 0 < false_positive_rate < 1:
            raise ValueError(
                "false_positive_rate must be between 0 and 1"
            )

        n = expected_items
        p = false_positive_rate

        # Standard Bloom-filter formula:
        #
        # m = -n ln(p) / (ln 2)^2

        self.m = max(
            8,
            math.ceil(
                -n
                * math.log(p)
                / (math.log(2) ** 2)
            )
        )

        # Optimal approximate number of hashes:
        #
        # k = (m/n) ln 2

        self.k = max(
            1,
            round(
                (self.m / n)
                * math.log(2)
            )
        )

        # Raw bit storage.
        self.bits = bytearray(
            (self.m + 7) // 8
        )


    def _positions(self, key):
        """
        Generate k Bloom-filter bit positions.

        Double hashing is used:

        position_i = h1 + i*h2 mod m
        """

        h1 = fnv1a64(
            key,
            0xA5A5A5A5
        )

        h2 = djb2_64(
            key,
            0x9E3779B9
        ) | 1

        for i in range(self.k):

            yield (
                h1 + i * h2
            ) % self.m


    def add(self, key):
        """
        Input:
            key: username

        Output:
            None

        Description:
            Sets k bits in the Bloom-filter bit array.
        """

        for position in self._positions(key):

            byte_index = position >> 3
            bit_index = position & 7

            self.bits[byte_index] |= (
                1 << bit_index
            )


    def contains(self, key):
        """
        Input:
            key: username

        Output:
            False -> definitely absent
            True  -> possibly present
        """

        for position in self._positions(key):

            byte_index = position >> 3
            bit_index = position & 7

            if not (
                self.bits[byte_index]
                & (1 << bit_index)
            ):
                return False

        return True