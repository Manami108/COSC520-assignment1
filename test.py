# Completed
import unittest

from algorithms.linear_search import linear_search
from algorithms.binary_search import binary_search
from algorithms.hash_table import HashTable
from algorithms.bloom_filter import BloomFilter
from algorithms.cuckoo_filter import CuckooFilter
from dataset import make_dataset

class TestLinearSearch(unittest.TestCase):
    def test_linear_search(self):
        values = make_dataset(10)
        self.assertTrue(linear_search(values, "user_000000000006"))
        self.assertFalse(linear_search(values, "user_000000000028"))

class TestBinarySearch(unittest.TestCase):
    def test_binary_search(self):
        values = make_dataset(10)
        self.assertTrue(binary_search(values, "user_000000000006"))
        self.assertFalse(binary_search(values, "user_000000000028"))

class TestHashTable(unittest.TestCase):
    def test_insert_and_search(self):
        values = make_dataset(10)
        table = HashTable(len(values))
        for value in values:
            table.insert(value)
        self.assertTrue(table.contains("user_000000000006"))
        self.assertFalse(table.contains("user_000000000028"))

    def test_collision(self):
        table = HashTable(3)
        first = "user_000000000000"
        second = "user_000000000005"
        table.insert(first)
        table.insert(second)
        self.assertTrue(table.contains(first))
        self.assertTrue(table.contains(second))
    
    def test_duplicate_insert(self):
        table = HashTable(10)
        key = "user_000000000001"
        self.assertTrue(table.insert(key))
        self.assertFalse(table.insert(key))


class TestBloomFilter(unittest.TestCase):
    def test_inserted_items_are_found(self):
        values = make_dataset(100)
        bloom = BloomFilter(len(values))
        for value in values:
            bloom.add(value)
        for value in values:
            self.assertTrue(bloom.contains(value))
            
class TestCuckooFilter(unittest.TestCase):
    def test_inserted_items_are_found(self):
        values = make_dataset(100)
        cuckoo = CuckooFilter(len(values))
        for value in values:
            self.assertTrue(cuckoo.insert(value))
        for value in values:
            self.assertTrue(cuckoo.contains(value))

class TestDataset(unittest.TestCase):
    def test_dataset(self):
        dataset = make_dataset(100)
        self.assertEqual(len(dataset), 100)
        self.assertEqual(dataset, sorted(dataset))
        self.assertEqual(len(dataset), len(set(dataset)))

if __name__ == "__main__":
    unittest.main()