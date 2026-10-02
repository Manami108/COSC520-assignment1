import unittest

from algorithms.linear_search import linear_search, linear_insert, linear_delete
from algorithms.binary_search import binary_search, binary_insert, binary_delete
from algorithms.hash_table import HashTable
from algorithms.bloom_filter import BloomFilter
from algorithms.cuckoo_filter import CuckooFilter
from dataset import make_dataset

# Checks that linear search works correctly.
class TestLinearSearch(unittest.TestCase):
    # Search
    def test_search(self):
        values = make_dataset(10)
        self.assertTrue(linear_search(values, "user_000000000006"))
        self.assertFalse(linear_search(values, "user_000000000028"))
        
    # Insert
    def test_insert(self):
        values = make_dataset(10)
        target = "user_000000000010"
        self.assertTrue(linear_insert(values, target))
        self.assertTrue(linear_search(values, target))
        self.assertFalse(linear_insert(values, target))
        
    # Delete
    def test_delete(self):
        values = make_dataset(10)
        target = "user_000000000006"
        self.assertTrue(linear_delete(values, target))
        self.assertFalse(linear_search(values, target))
        self.assertFalse(linear_delete(values, target))

# Checks that binary search works correctly.
class TestBinarySearch(unittest.TestCase):
    # Search
    def test_search(self):
        values = make_dataset(10)
        self.assertTrue(binary_search(values, "user_000000000006"))
        self.assertFalse(binary_search(values, "user_000000000028"))

    # Insert
    def test_insert(self):
        values = make_dataset(10)
        target = "user_000000000010"
        self.assertTrue(binary_insert(values, target))
        self.assertTrue(binary_search(values, target))
        self.assertEqual(values, sorted(values))
        self.assertFalse(binary_insert(values, target))
    # Delete
    def test_delete(self):
        values = make_dataset(10)
        target = "user_000000000006"
        self.assertTrue(binary_delete(values, target))
        self.assertFalse(binary_search(values, target))
        self.assertEqual(values, sorted(values))
        self.assertFalse(binary_delete(values, target))

# Checks that hash table works correctly.
class TestHashTable(unittest.TestCase):

    # Search
    def test_search(self):
        values = make_dataset(10)
        table = HashTable(len(values))
        for value in values:
            table.hash_insert(value)
        self.assertTrue(table.hash_search("user_000000000006"))
        self.assertFalse(table.hash_search("user_000000000028"))

    # Insert
    def test_insert(self):
        table = HashTable(10)
        target = "user_000000000010"
        self.assertTrue(table.hash_insert(target))
        self.assertTrue(table.hash_search(target))
        self.assertFalse(table.hash_insert(target))

    # Delete
    def test_delete(self):
        table = HashTable(10)
        target = "user_000000000006"
        table.hash_insert(target)
        self.assertTrue(table.hash_delete(target))
        self.assertFalse(table.hash_search(target))
        self.assertFalse(table.hash_delete(target))

# Checks that Bloom filter works correctly.
class TestBloomFilter(unittest.TestCase):

    # Search
    def test_search(self):
        values = make_dataset(100)
        bloom = BloomFilter(len(values))
        for value in values:
            bloom.bloom_insert(value)
        for value in values:
            self.assertTrue(bloom.bloom_search(value))

    # Insert
    def test_insert(self):
        bloom = BloomFilter(10)
        target = "user_000000000010"
        bloom.bloom_insert(target)
        self.assertTrue(bloom.bloom_search(target))

# Checks that Cuckoo filter works correctly.
class TestCuckooFilter(unittest.TestCase):

    # Search
    def test_search(self):
        values = make_dataset(100)
        cuckoo = CuckooFilter(len(values))
        for value in values:
            cuckoo.cuckoo_insert(value)
        for value in values:
            self.assertTrue(cuckoo.cuckoo_search(value))

    # Insert
    def test_insert(self):
        cuckoo = CuckooFilter(10)
        target = "user_000000000010"
        self.assertTrue(cuckoo.cuckoo_insert(target))
        self.assertTrue(cuckoo.cuckoo_search(target))


    # Delete
    def test_delete(self):
        cuckoo = CuckooFilter(10)
        target = "user_000000000006"
        cuckoo.cuckoo_insert(target)
        self.assertTrue(cuckoo.cuckoo_delete(target))
        self.assertFalse(cuckoo.cuckoo_search(target))
        self.assertFalse(cuckoo.cuckoo_delete(target))
        
if __name__ == "__main__":
    unittest.main()