import unittest

from algorithms.linear_search import linear_search
from algorithms.binary_search import binary_search
from algorithms.hash_table import HashTable
from algorithms.bloom_filter import BloomFilter
from algorithms.cuckoo_filter import CuckooFilter


class LoginCheckerTests(unittest.TestCase):

    def setUp(self):

        self.values = [
            "alice",
            "bob",
            "charlie",
            "diana",
        ]

        self.sorted_values = sorted(
            self.values
        )


    def test_linear_search(self):

        self.assertTrue(
            linear_search(
                self.values,
                "bob",
            )
        )

        self.assertFalse(
            linear_search(
                self.values,
                "zoe",
            )
        )


    def test_binary_search(self):

        self.assertTrue(
            binary_search(
                self.sorted_values,
                "charlie",
            )
        )

        self.assertFalse(
            binary_search(
                self.sorted_values,
                "zoe",
            )
        )


    def test_hash_table(self):

        table = HashTable(
            len(self.values)
        )

        for value in self.values:

            self.assertTrue(
                table.insert(value)
            )


        for value in self.values:

            self.assertTrue(
                table.contains(value)
            )


        self.assertFalse(
            table.contains("zoe")
        )


        # Duplicate should not be inserted.
        self.assertFalse(
            table.insert("alice")
        )


    def test_bloom_filter_has_no_false_negatives_for_inserted_items(
        self
    ):

        bloom = BloomFilter(
            len(self.values),
            false_positive_rate=0.01,
        )


        for value in self.values:

            bloom.add(value)


        for value in self.values:

            self.assertTrue(
                bloom.contains(value)
            )


    def test_cuckoo_filter_has_no_false_negatives_for_inserted_items(
        self
    ):

        cuckoo = CuckooFilter(
            len(self.values),
            fingerprint_bits=16,
        )


        for value in self.values:

            self.assertTrue(
                cuckoo.insert(value)
            )


        for value in self.values:

            self.assertTrue(
                cuckoo.contains(value)
            )


    def test_cuckoo_delete(self):

        cuckoo = CuckooFilter(
            10,
            fingerprint_bits=24,
        )


        self.assertTrue(
            cuckoo.insert("alice")
        )


        self.assertTrue(
            cuckoo.contains("alice")
        )


        self.assertTrue(
            cuckoo.delete("alice")
        )


        self.assertFalse(
            cuckoo.contains("alice")
        )


if __name__ == "__main__":

    unittest.main()