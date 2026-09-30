import csv
import random
import statistics
import time

from algorithms.linear_search import linear_search
from algorithms.binary_search import binary_search
from algorithms.hash_table import HashTable
from algorithms.bloom_filter import BloomFilter
from algorithms.cuckoo_filter import CuckooFilter
from dataset import make_dataset, save_dataset

# Use the same target false-positive rate
# for Bloom and Cuckoo filters.
TARGET_FPR = 0.01

def make_queries(n, count, seed=123):
    """Create shuffled queries with 50% present and 50% absent usernames."""
    rng = random.Random(seed)
    half = count // 2

    # Generate usernames that are already in the dataset.
    present = [
        f"user_{rng.randrange(n):012d}"
        for _ in range(half)
    ]

    # Dataset contains usernames 0 to n - 1,
    # so usernames beginning at n are absent.
    absent = [
        f"user_{n + i:012d}"
        for i in range(count - half)
    ]

    queries = present + absent
    rng.shuffle(queries)

    return queries

def median_time_per_query(search_function, queries, repeats):
    samples = []

    for _ in range(repeats):
        start = time.perf_counter()

        for query in queries:
            search_function(query)

        elapsed = time.perf_counter() - start
        samples.append(elapsed / len(queries))

    return statistics.median(samples)* 1_000_000

def build_structures(usernames):
    n = len(usernames)
    
    table = HashTable(n)
    bloom = BloomFilter(n, TARGET_FPR)
    cuckoo = CuckooFilter(n, TARGET_FPR)

    for username in usernames:
        table.insert(username)
        bloom.add(username)

        if not cuckoo.insert(username):
            raise RuntimeError("Cuckoo insertion failed. ")

    return table, bloom, cuckoo

def plot_results(rows):
    """Plot and save lookup runtime for all five methods."""
    import matplotlib.pyplot as plt

    methods = ["Linear", "Binary", "Hash", "Bloom", "Cuckoo"]

    plt.figure(figsize=(8, 5))

    for method in methods:
        points = [
            (n, runtime)
            for n, name, runtime in rows
            if name == method
        ]

        x = [n for n, _ in points]
        y = [runtime for _, runtime in points]

        plt.plot(x, y, label=method)

    plt.xscale("log")
    plt.yscale("log")

    plt.xlabel("Number of stored logins, n")
    plt.ylabel("Median lookup time (microseconds/query)")
    plt.title("Login Checker Lookup-Time Comparison")

    plt.legend()
    plt.tight_layout()
    plt.savefig("lookup_runtime.png")
    plt.close()


def benchmark(sizes, query_count=1000, repeats=5):
    
    rows = []
    # Generate the largest dataset once.
    largest_dataset = make_dataset(max(sizes))
    save_dataset(largest_dataset)

    for n in sizes:
        print(f"\nTesting n={n:,}")

        # The dataset is sorted, so it can be used for binary search.
        usernames = largest_dataset[:n]
        queries = make_queries(n, query_count)

        table, bloom, cuckoo = build_structures(usernames)

        methods = [
            ("Linear", lambda q: linear_search(usernames, q)),
            ("Binary", lambda q: binary_search(usernames, q)),
            ("Hash", lambda q: table.contains(q)),
            ("Bloom", lambda q: bloom.contains(q)),
            ("Cuckoo", lambda q: cuckoo.contains(q))
        ]

        for name, search_function in methods:
            runtime = median_time_per_query(
                search_function,
                queries,
                repeats
            )

            rows.append((n, name, runtime))

            print(
                f"{name:>7}: "
                f"{runtime:.3f} microseconds/query"
            )

    with open(
        "benchmark_results.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "n",
            "method",
            "microseconds_per_query"
        ])

        writer.writerows(rows)

    plot_results(rows)

    print("\nCreated:")
    print("  usernames_dataset.txt")
    print("  benchmark_results.csv")
    print("  lookup_runtime.png")


if __name__ == "__main__":

    SIZES = [
        1_000,
        5_000,
        10_000,
        50_000,
        100_000,
        200_000,
        500_000,
        1_000_000
    ]

    benchmark(SIZES)