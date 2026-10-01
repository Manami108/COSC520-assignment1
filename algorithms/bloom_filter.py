
import math
from utils.hash_functions import fnv1a64, djb2_64, mix64

class BloomFilter:
    """
    This class implements a Bloom filter for probabilistic membership
    testing. It stores bits instead of complete usernames, which reduces
    memory usage. A Bloom filter can produce false positives, but it
    should not produce false negatives for successfully inserted items.
    """
    def __init__(self, expected_items, target_fpr=0.01):
        """
        This method creates a Bloom filter for the expected number of
        items and the requested false-positive rate. It calculates the
        required number of bits and the number of hash positions used
        for each item.
        """
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not 0 < target_fpr < 1:
            raise ValueError("target_fpr must be between 0 and 1")

        n = expected_items
        self.size = math.ceil(-(n * math.log(target_fpr)) / (math.log(2) ** 2))
        self.hash_count = max(1, round((self.size / n) * math.log(2)))
 
        self.bit_array = bytearray((self.size + 7) // 8)

    def _hashes(self, key):
        
        """
        This method generates the Bloom filter positions associated with
        a key. It creates two base hash values and combines them using
        double hashing. It yields each position that should be checked
        or updated in the bit array.
        """
        h1 = mix64(fnv1a64(key))
        h2 = mix64(djb2_64(key)) | 1
        
        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size
 
    def bloom_insert(self, key):

        """
        This method adds a key to the Bloom filter. It generates all hash
        positions associated with the key and sets the corresponding bits
        in the bit array to one.
        """
        
        for position in self._hashes(key):
            self.bit_array[position >> 3] |= 1 << (position & 7)

    def bloom_search(self, key):
        """
        This method checks whether a key may exist in the Bloom filter.
        It checks every bit associated with the key. It returns False if
        at least one required bit is zero. It returns True if all required
        bits are one, although this result may be a false positive.
        """        

        for position in self._hashes(key):
            if not self.bit_array[position >> 3] & (1 << (position & 7)):
                return False
        return True
