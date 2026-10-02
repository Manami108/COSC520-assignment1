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

# The same false positive rate is used for both Bloom and Cuckoo filters.
TARGET_FPR = 0.01
FPR_QUERIES = 100_000

# This code creates an equal mixture of existings and non existing usernames. 
def make_queries(n, count, seed=123):
    if n <= 0:
        raise ValueError("n must be positive")
    if count <= 0:
        raise ValueError("count must be positive")

    rng = random.Random(seed)
    half = count // 2

    present = [
        f"user_{rng.randrange(n):012d}"
        for _ in range(half)
    ]

    absent = [
        f"user_{n + i:012d}"
        for i in range(count - half)
    ]

    queries = present + absent
    rng.shuffle(queries)
    return queries

# This function measures the median lookup time per query. 
def median_time_per_query(search_function, queries, repeats):
    if not queries:
        raise ValueError("queries must not be empty")
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        for query in queries:
            search_function(query)
        elapsed = time.perf_counter() - start
        samples.append(elapsed / len(queries))

    return (statistics.median(samples) * 1_000_000)

# This function makes hash table, bloom filter, and cuckoo filter from a same dataset. 
def build_structures(usernames):
    n = len(usernames)
    table = HashTable(n)
    bloom = BloomFilter(n, target_fpr=TARGET_FPR)
    cuckoo = CuckooFilter(n, target_fpr=TARGET_FPR)

    for username in usernames:
        table.hash_insert(username)
        bloom.bloom_insert(username)
        if not cuckoo.cuckoo_insert(username):
            raise RuntimeError(
                "Cuckoo insertion failed. "
                "Try a lower target_load."
            )
    return table, bloom, cuckoo

# This function calculates the false positive rate and false negatives. 
def measure_filter_accuracy(search_function, usernames, count=FPR_QUERIES):
    n = len(usernames)
    false_positives = 0
    
    for i in range(count):
        query = f"user_{n + i:012d}"
        if search_function(query):
            false_positives += 1
    false_positive_rate = false_positives / count
    false_negatives = sum(not search_function(username)
        for username in usernames)
    return false_positive_rate, false_negatives

# this block is to plot results of the methods. 
def plot_results(rows):
    import matplotlib.pyplot as plt

    methods = ["Linear", "Binary", "Hash", "Bloom", "Cuckoo"]
    plt.figure(figsize=(8, 5))

    for method in methods:
        points = sorted((n, runtime) for n, name, runtime in rows if name == method)
        x_values = [n for n, _ in points]
        y_values = [runtime for _, runtime in points]
        plt.plot(x_values, y_values, label=method)
        
    # logarithmic scale is used. 
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Number of stored logins, n")
    plt.ylabel("Median lookup time (microseconds/query)")
    plt.title("Login Checker Lookup-Time Comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig("lookup_runtime.png", dpi=200)
    plt.close()

# All methods over several dataset size. 
def benchmark(sizes, query_count=1000, repeats=5):
    if not sizes:
        raise ValueError("sizes must not be empty")
    if any(n <= 0 for n in sizes):
        raise ValueError("all dataset sizes must be positive")
    if query_count <= 0:
        raise ValueError("query_count must be positive")
    if repeats <= 0:
        raise ValueError("repeats must be positive")

    runtime_rows = []
    fpr_rows = []
    
    # It generates the largest dataset so that it can be reused. 
    largest_dataset = make_dataset(max(sizes))
    save_dataset(largest_dataset)

    for n in sizes:
        print(f"\nTesting n={n:,}")
        usernames = (largest_dataset[:n])
        queries = make_queries(n, query_count)
        (table, bloom, cuckoo) = build_structures(usernames)

        methods = [
            ("Linear", lambda q: linear_search(usernames,q)),
            ("Binary", lambda q: binary_search(usernames,q)),
            ("Hash", lambda q: table.hash_search(q)),
            ("Bloom", lambda q: bloom.bloom_search(q)),
            ("Cuckoo", lambda q: cuckoo.cuckoo_search(q))
        ]

        for (name, search_function) in methods:
            runtime = (median_time_per_query(search_function, queries, repeats))
            runtime_rows.append((n, name, runtime))

            print(f"{name:>7}: " f"{runtime:.3f} " "microseconds/query")

        for name,structure in [
            ("Bloom", bloom.bloom_search), ("Cuckoo", cuckoo.cuckoo_search)
            ]:
            fpr, false_negatives = measure_filter_accuracy(structure, usernames,)
            fpr_rows.append((n, name, TARGET_FPR, fpr, false_negatives))

            # print(
            #     f"{name:>7}: "
            #     f"target FPR={TARGET_FPR:.2%}, "
            #     f"measured FPR={fpr:.4%}, "
            #     f"false negatives={false_negatives}"
            # )

    # Save runtime results.
    with open("benchmark_results.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["n", "method", "microseconds_per_query"])
        writer.writerows(runtime_rows)

    # Save probabilistic-filter results.
    with open("fpr_results.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "n",
                "method",
                "target_false_positive_rate",
                "measured_false_positive_rate",
                "false_negatives"
            ]
        )
        writer.writerows(fpr_rows)
    plot_results(runtime_rows)

    print("\nCreated:")
    print("usernames_dataset.txt")
    print("benchmark_results.csv")
    print("fpr_results.csv")
    print("lookup_runtime.png")

if __name__ == "__main__":
    SIZES = [1_000, 5_000, 10_000, 50_000, 100_000, 200_000, 500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000]
    benchmark(SIZES)