# import csv
# import math
# import random
# import statistics
# import time

# MASK64 = (1 << 64) - 1
# FNV_OFFSET = 1469598103934665603
# FNV_PRIME = 1099511628211


# # ============================================================
# # HASH FUNCTIONS
# # ============================================================

# def fnv1a64(text, seed=0):
#     """
#     Input:
#         text: string to hash
#         seed: optional integer seed

#     Output:
#         deterministic 64-bit hash value

#     Description:
#         Manual implementation of the FNV-1a hash algorithm.
#     """
#     h = (FNV_OFFSET ^ seed) & MASK64

#     for byte in text.encode("utf-8"):
#         h ^= byte
#         h = (h * FNV_PRIME) & MASK64

#     return h


# def djb2_64(text, seed=5381):
#     """
#     Input:
#         text: string to hash
#         seed: starting hash value

#     Output:
#         deterministic 64-bit hash value

#     Description:
#         Manual DJB2-style hash used as a second independent hash.
#     """
#     h = seed & MASK64

#     for byte in text.encode("utf-8"):
#         h = ((h << 5) + h + byte) & MASK64

#     return h


# def mix64(x):
#     """
#     Input:
#         integer x

#     Output:
#         mixed 64-bit integer

#     Description:
#         Improves bit distribution before selecting a Cuckoo bucket.
#     """
#     x &= MASK64

#     x ^= x >> 33
#     x = (x * 0xFF51AFD7ED558CCD) & MASK64

#     x ^= x >> 33
#     x = (x * 0xC4CEB9FE1A85EC53) & MASK64

#     x ^= x >> 33

#     return x & MASK64


# def next_power_of_two(x):
#     """
#     Input:
#         positive integer x

#     Output:
#         smallest power of two greater than or equal to x
#     """
#     if x <= 1:
#         return 1

#     return 1 << (x - 1).bit_length()


# # ============================================================
# # 1. LINEAR SEARCH
# # ============================================================

# def linear_search(values, target):
#     """
#     Input:
#         values: list of usernames
#         target: username to find

#     Output:
#         True if target exists, otherwise False

#     Complexity:
#         O(n)
#     """
#     for value in values:
#         if value == target:
#             return True

#     return False


# # ============================================================
# # 2. BINARY SEARCH
# # ============================================================

# def binary_search(values, target):
#     """
#     Input:
#         values: sorted list of usernames
#         target: username to find

#     Output:
#         True if target exists, otherwise False

#     Complexity:
#         O(log n)
#     """
#     low = 0
#     high = len(values) - 1

#     while low <= high:

#         mid = (low + high) // 2

#         if values[mid] == target:
#             return True

#         if values[mid] < target:
#             low = mid + 1

#         else:
#             high = mid - 1

#     return False


# # ============================================================
# # 3. HASH TABLE
# # ============================================================

# class HashTable:
#     """
#     Exact hash table implemented using open addressing
#     and linear probing.

#     Python dictionary/set implementations are not used.
#     """

#     def __init__(self, expected_items, max_load=0.65):

#         required = max(
#             2,
#             math.ceil(expected_items / max_load)
#         )

#         self.capacity = next_power_of_two(required)

#         self.mask = self.capacity - 1

#         self.slots = [None] * self.capacity

#         self.size = 0


#     def insert(self, key):
#         """
#         Input:
#             key: username

#         Output:
#             True if newly inserted
#             False if username already exists

#         Description:
#             Uses linear probing when collisions occur.
#         """

#         index = fnv1a64(key) & self.mask

#         for _ in range(self.capacity):

#             if self.slots[index] is None:

#                 self.slots[index] = key
#                 self.size += 1

#                 return True

#             if self.slots[index] == key:

#                 return False

#             index = (index + 1) & self.mask

#         raise RuntimeError("Hash table is full.")


#     def contains(self, key):
#         """
#         Input:
#             key: username

#         Output:
#             True if key exists, otherwise False
#         """

#         index = fnv1a64(key) & self.mask

#         for _ in range(self.capacity):

#             value = self.slots[index]

#             if value is None:
#                 return False

#             if value == key:
#                 return True

#             index = (index + 1) & self.mask

#         return False


# # ============================================================
# # 4. BLOOM FILTER
# # ============================================================

# class BloomFilter:
#     """
#     Bloom filter implemented using a manually managed
#     bit vector.

#     No Bloom-filter library is used.
#     """

#     def __init__(
#         self,
#         expected_items,
#         false_positive_rate=0.01
#     ):

#         if expected_items <= 0:
#             raise ValueError(
#                 "expected_items must be positive"
#             )

#         if not 0 < false_positive_rate < 1:
#             raise ValueError(
#                 "false_positive_rate must be between 0 and 1"
#             )

#         n = expected_items
#         p = false_positive_rate

#         # Standard Bloom-filter formula:
#         #
#         # m = -n ln(p) / (ln 2)^2

#         self.m = max(
#             8,
#             math.ceil(
#                 -n
#                 * math.log(p)
#                 / (math.log(2) ** 2)
#             )
#         )

#         # Optimal approximate number of hashes:
#         #
#         # k = (m/n) ln 2

#         self.k = max(
#             1,
#             round(
#                 (self.m / n)
#                 * math.log(2)
#             )
#         )

#         # Raw bit storage.
#         self.bits = bytearray(
#             (self.m + 7) // 8
#         )


#     def _positions(self, key):
#         """
#         Generate k Bloom-filter bit positions.

#         Double hashing is used:

#         position_i = h1 + i*h2 mod m
#         """

#         h1 = fnv1a64(
#             key,
#             0xA5A5A5A5
#         )

#         h2 = djb2_64(
#             key,
#             0x9E3779B9
#         ) | 1

#         for i in range(self.k):

#             yield (
#                 h1 + i * h2
#             ) % self.m


#     def add(self, key):
#         """
#         Input:
#             key: username

#         Output:
#             None

#         Description:
#             Sets k bits in the Bloom-filter bit array.
#         """

#         for position in self._positions(key):

#             byte_index = position >> 3
#             bit_index = position & 7

#             self.bits[byte_index] |= (
#                 1 << bit_index
#             )


#     def contains(self, key):
#         """
#         Input:
#             key: username

#         Output:
#             False -> definitely absent
#             True  -> possibly present
#         """

#         for position in self._positions(key):

#             byte_index = position >> 3
#             bit_index = position & 7

#             if not (
#                 self.bits[byte_index]
#                 & (1 << bit_index)
#             ):
#                 return False

#         return True


# # ============================================================
# # 5. CUCKOO FILTER
# # ============================================================

# class CuckooFilter:
#     """
#     Cuckoo filter using two candidate buckets per
#     fingerprint.

#     Each username is represented by a small fingerprint
#     rather than storing the entire username.
#     """

#     def __init__(
#         self,
#         expected_items,
#         bucket_size=4,
#         fingerprint_bits=16,
#         target_load=0.90,
#         max_kicks=500,
#         seed=7
#     ):

#         if expected_items <= 0:
#             raise ValueError(
#                 "expected_items must be positive"
#             )

#         needed = math.ceil(
#             expected_items
#             / (
#                 bucket_size
#                 * target_load
#             )
#         )

#         self.num_buckets = (
#             next_power_of_two(
#                 max(2, needed)
#             )
#         )

#         self.bucket_mask = (
#             self.num_buckets - 1
#         )

#         self.bucket_size = bucket_size

#         self.fp_mask = (
#             (1 << fingerprint_bits) - 1
#         )

#         self.max_kicks = max_kicks

#         # Fingerprint 0 means empty.
#         self.slots = (
#             [0]
#             * (
#                 self.num_buckets
#                 * bucket_size
#             )
#         )

#         self.size = 0

#         self.rng = random.Random(seed)


#     def _fingerprint(self, key):
#         """
#         Return a non-zero fingerprint for key.
#         """

#         fp = (
#             mix64(
#                 fnv1a64(
#                     key,
#                     0xC0FFEE
#                 )
#             )
#             & self.fp_mask
#         )

#         if fp == 0:
#             fp = 1

#         return fp


#     def _index1(self, key):
#         """
#         Calculate the first candidate bucket.
#         """

#         return (
#             mix64(
#                 fnv1a64(
#                     key,
#                     0x12345678
#                 )
#             )
#             & self.bucket_mask
#         )


#     def _alternate_index(
#         self,
#         index,
#         fingerprint
#     ):
#         """
#         Calculate the second candidate bucket.

#         XOR is used so applying the operation again
#         returns to the original bucket.
#         """

#         delta = (
#             mix64(fingerprint)
#             & self.bucket_mask
#         )

#         if delta == 0:
#             delta = 1

#         return index ^ delta


#     def _bucket_contains(
#         self,
#         index,
#         fingerprint
#     ):
#         """
#         Check whether a fingerprint exists in one bucket.
#         """

#         base = (
#             index
#             * self.bucket_size
#         )

#         for offset in range(
#             self.bucket_size
#         ):

#             if (
#                 self.slots[
#                     base + offset
#                 ]
#                 == fingerprint
#             ):
#                 return True

#         return False


#     def _place_if_empty(
#         self,
#         index,
#         fingerprint
#     ):
#         """
#         Insert fingerprint into the first empty position
#         in a bucket.
#         """

#         base = (
#             index
#             * self.bucket_size
#         )

#         for offset in range(
#             self.bucket_size
#         ):

#             slot = base + offset

#             if self.slots[slot] == 0:

#                 self.slots[slot] = (
#                     fingerprint
#                 )

#                 return True

#         return False


#     def contains(self, key):
#         """
#         Input:
#             key: username

#         Output:
#             False -> definitely absent
#             True  -> possibly present
#         """

#         fp = self._fingerprint(key)

#         i1 = self._index1(key)

#         i2 = self._alternate_index(
#             i1,
#             fp
#         )

#         return (
#             self._bucket_contains(
#                 i1,
#                 fp
#             )
#             or
#             self._bucket_contains(
#                 i2,
#                 fp
#             )
#         )


#     def insert(self, key):
#         """
#         Insert the fingerprint into the filter.

#         If both candidate buckets are full,
#         fingerprints are relocated.

#         If relocation fails, changes are rolled back.
#         """

#         fp = self._fingerprint(key)

#         i1 = self._index1(key)

#         i2 = self._alternate_index(
#             i1,
#             fp
#         )

#         if (
#             self._place_if_empty(
#                 i1,
#                 fp
#             )
#             or
#             self._place_if_empty(
#                 i2,
#                 fp
#             )
#         ):

#             self.size += 1
#             return True


#         # Both buckets are full.
#         index = (
#             i1
#             if self.rng.randrange(2) == 0
#             else i2
#         )

#         current_fp = fp

#         swaps = []


#         for _ in range(
#             self.max_kicks
#         ):

#             slot = (
#                 index
#                 * self.bucket_size
#                 + self.rng.randrange(
#                     self.bucket_size
#                 )
#             )

#             old_fp = (
#                 self.slots[slot]
#             )

#             self.slots[slot] = (
#                 current_fp
#             )

#             swaps.append(
#                 (
#                     slot,
#                     old_fp
#                 )
#             )

#             current_fp = old_fp

#             index = (
#                 self._alternate_index(
#                     index,
#                     current_fp
#                 )
#             )


#             if self._place_if_empty(
#                 index,
#                 current_fp
#             ):

#                 self.size += 1

#                 return True


#         # Restore the original filter if insertion failed.
#         for slot, old_fp in reversed(
#             swaps
#         ):

#             self.slots[slot] = old_fp


#         return False


#     def delete(self, key):
#         """
#         Delete one matching fingerprint if present.

#         Returns:
#             True if deleted
#             False otherwise
#         """

#         fp = self._fingerprint(key)

#         i1 = self._index1(key)

#         i2 = self._alternate_index(
#             i1,
#             fp
#         )


#         for index in (
#             i1,
#             i2
#         ):

#             base = (
#                 index
#                 * self.bucket_size
#             )

#             for offset in range(
#                 self.bucket_size
#             ):

#                 slot = base + offset

#                 if (
#                     self.slots[slot]
#                     == fp
#                 ):

#                     self.slots[slot] = 0

#                     self.size -= 1

#                     return True


#         return False


# # ============================================================
# # DATASET
# # ============================================================

# def make_dataset(n):
#     """
#     Input:
#         n: number of usernames

#     Output:
#         list containing n unique usernames

#     The fixed-width numbers make the list already sorted.
#     """

#     return [
#         f"user_{i:012d}"
#         for i in range(n)
#     ]


# def save_dataset(
#     values,
#     path="usernames_dataset.txt"
# ):
#     """
#     Save generated usernames to disk.

#     The generated file can later be uploaded and linked
#     in the assignment report.
#     """

#     with open(
#         path,
#         "w",
#         encoding="utf-8"
#     ) as file:

#         for value in values:

#             file.write(
#                 value + "\n"
#             )


# # ============================================================
# # BENCHMARK QUERIES
# # ============================================================

# def make_queries(
#     n,
#     count=100,
#     seed=123
# ):
#     """
#     Create a query set containing:

#         50% existing usernames
#         50% nonexistent usernames
#     """

#     rng = random.Random(seed)

#     half = count // 2


#     present = [

#         f"user_{rng.randrange(n):012d}"

#         for _ in range(half)

#     ]


#     absent = [

#         f"user_{n + i + 1:012d}"

#         for i in range(
#             count - half
#         )

#     ]


#     queries = (
#         present
#         + absent
#     )


#     rng.shuffle(queries)

#     return queries


# def median_time_per_query(
#     search_function,
#     queries,
#     repeats=3
# ):
#     """
#     Measure lookup time several times.

#     Output:
#         median microseconds per query
#     """

#     samples = []


#     for _ in range(repeats):

#         start = (
#             time.perf_counter()
#         )


#         for query in queries:

#             search_function(
#                 query
#             )


#         elapsed = (
#             time.perf_counter()
#             - start
#         )


#         samples.append(
#             elapsed
#             / len(queries)
#         )


#     return (
#         statistics.median(
#             samples
#         )
#         * 1_000_000
#     )


# # ============================================================
# # BUILD ADVANCED STRUCTURES
# # ============================================================

# def build_structures(
#     usernames
# ):
#     """
#     Build:

#         Hash table
#         Bloom filter
#         Cuckoo filter
#     """

#     n = len(usernames)


#     table = HashTable(n)


#     bloom = BloomFilter(
#         n,
#         false_positive_rate=0.01
#     )


#     cuckoo = CuckooFilter(
#         n,
#         fingerprint_bits=16
#     )


#     for username in usernames:

#         table.insert(
#             username
#         )

#         bloom.add(
#             username
#         )


#         if not cuckoo.insert(
#             username
#         ):

#             raise RuntimeError(
#                 "Cuckoo insertion failed. "
#                 "Use a lower target_load "
#                 "or increase table size."
#             )


#     return (
#         table,
#         bloom,
#         cuckoo
#     )


# # ============================================================
# # PLOT RESULTS
# # ============================================================

# def plot_results(rows):
#     """
#     Create lookup_runtime.png.

#     Uses logarithmic axes because n and the running times
#     can differ by several orders of magnitude.
#     """

#     import matplotlib.pyplot as plt


#     methods = [

#         "Linear",
#         "Binary",
#         "Hash",
#         "Bloom",
#         "Cuckoo"

#     ]


#     for method in methods:

#         points = sorted(

#             (
#                 n,
#                 us
#             )

#             for n, name, us
#             in rows

#             if name == method

#         )


#         plt.plot(

#             [
#                 n
#                 for n, _
#                 in points
#             ],

#             [
#                 us
#                 for _, us
#                 in points
#             ],

#             marker="o",

#             label=method

#         )


#     plt.xscale("log")

#     plt.yscale("log")


#     plt.xlabel(
#         "Number of stored logins, n"
#     )

#     plt.ylabel(
#         "Median lookup time "
#         "(microseconds/query)"
#     )

#     plt.title(
#         "Login Checker "
#         "Lookup-Time Comparison"
#     )


#     plt.legend()


#     plt.grid(
#         True,
#         which="both",
#         linestyle="--",
#         linewidth=0.5
#     )


#     plt.tight_layout()


#     plt.savefig(
#         "lookup_runtime.png",
#         dpi=200
#     )


#     plt.close()


# # ============================================================
# # FULL BENCHMARK
# # ============================================================

# def benchmark(
#     sizes,
#     query_count=100,
#     repeats=3
# ):
#     """
#     Compare all five methods.

#     Outputs:
#         usernames_dataset.txt
#         benchmark_results.csv
#         lookup_runtime.png
#     """

#     rows = []


#     largest_dataset = (
#         make_dataset(
#             max(sizes)
#         )
#     )


#     save_dataset(
#         largest_dataset
#     )


#     for n in sizes:

#         print(
#             f"\nTesting n={n:,}"
#         )


#         usernames = (
#             largest_dataset[:n]
#         )


#         queries = make_queries(
#             n,
#             query_count
#         )


#         table, bloom, cuckoo = (
#             build_structures(
#                 usernames
#             )
#         )


#         methods = [

#             (
#                 "Linear",

#                 lambda q,
#                 a=usernames:
#                 linear_search(
#                     a,
#                     q
#                 )
#             ),

#             (
#                 "Binary",

#                 lambda q,
#                 a=usernames:
#                 binary_search(
#                     a,
#                     q
#                 )
#             ),

#             (
#                 "Hash",
#                 table.contains
#             ),

#             (
#                 "Bloom",
#                 bloom.contains
#             ),

#             (
#                 "Cuckoo",
#                 cuckoo.contains
#             )

#         ]


#         for (
#             name,
#             search_function
#         ) in methods:

#             us = (
#                 median_time_per_query(
#                     search_function,
#                     queries,
#                     repeats
#                 )
#             )


#             rows.append(
#                 (
#                     n,
#                     name,
#                     us
#                 )
#             )


#             print(
#                 f"{name:>7}: "
#                 f"{us:10.3f} "
#                 "us/query"
#             )


#         # --------------------------------------------
#         # FALSE-POSITIVE EXPERIMENT
#         # --------------------------------------------

#         absent = [

#             f"not_present_{i:012d}"

#             for i in range(5000)

#         ]


#         bloom_fp = (

#             sum(
#                 bloom.contains(q)
#                 for q in absent
#             )

#             / len(absent)

#         )


#         cuckoo_fp = (

#             sum(
#                 cuckoo.contains(q)
#                 for q in absent
#             )

#             / len(absent)

#         )


#         print(
#             "Bloom false-positive rate:  "
#             f"{bloom_fp:.4%}"
#         )


#         print(
#             "Cuckoo false-positive rate: "
#             f"{cuckoo_fp:.4%}"
#         )


#     # --------------------------------------------
#     # SAVE CSV RESULTS
#     # --------------------------------------------

#     with open(
#         "benchmark_results.csv",
#         "w",
#         newline="",
#         encoding="utf-8"
#     ) as file:

#         writer = csv.writer(file)


#         writer.writerow(
#             [
#                 "n",
#                 "method",
#                 "microseconds_per_query"
#             ]
#         )


#         writer.writerows(
#             rows
#         )


#     # --------------------------------------------
#     # CREATE GRAPH
#     # --------------------------------------------

#     plot_results(rows)


#     print(
#         "\nCreated:"
#     )

#     print(
#         "  usernames_dataset.txt"
#     )

#     print(
#         "  benchmark_results.csv"
#     )

#     print(
#         "  lookup_runtime.png"
#     )


# # ============================================================
# # MAIN
# # ============================================================

# if __name__ == "__main__":

#     # Start with these values.
#     #
#     # Increase them if your computer has enough
#     # memory and the experiment finishes reasonably.

#     SIZES = [

#         1_000,

#         5_000,

#         10_000,

#         50_000,

#         100_000,

#         200_000

#     ]


#     benchmark(

#         SIZES,

#         query_count=100,

#         repeats=3

#     )