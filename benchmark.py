import csv
import random
import statistics
import time

from algorithms.linear_search import linear_search
from algorithms.binary_search import binary_search
from algorithms.hash_table import HashTable
from algorithms.bloom_filter import BloomFilter
from algorithms.cuckoo_filter import CuckooFilter
from algorithms.quotient_filter import QuotientFilter
from dataset import make_dataset, save_dataset

# The same false positive rate is used for both Bloom and Cuckoo filters, and quatient filter.
p = 0.01
# It is number of non-existing usernames to measure the false positive rate. 
FPR_QUERIES = 100_000

# This code creates an equal mixture of existings and non existing usernames (about 50%, 50%). 
def make_queries(n, count, seed=123):
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
    
    # the queries are shuffled. 
    queries = present + absent
    rng.shuffle(queries)
    return queries

# This function measures the median lookup time per query. 
def median_time_per_query(search_fn, queries, repeats):
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        for query in queries:
            search_fn(query)
        elapsed = time.perf_counter() - start
        samples.append(elapsed / len(queries))
        
    # It multiplies by 1,000,000 to convert seconds to microseconds.
    return statistics.median(samples) * 1_000_000

# This function makes hash table, bloom filter, cuckoo filter, and quotient filter from a same dataset. 
def build_structures(usernames):
    n = len(usernames)
    table = HashTable(n)
    bloom = BloomFilter(n, p=p)
    cuckoo = CuckooFilter(n, p=p)
    quotient = QuotientFilter(n, p=p)

    for username in usernames:
        table.hash_insert(username)
        bloom.bloom_insert(username)
        cuckoo.cuckoo_insert(username)
        quotient.quotient_insert(username)
        
    return table, bloom, cuckoo, quotient

# This function calculates the false positive rate and false negatives. 
def measure_filter_accuracy(search_fn, usernames, count=FPR_QUERIES):
    n = len(usernames)
    fp = 0
    
    for i in range(count):
        query = f"user_{n + i:012d}"
        if search_fn(query):
            fp += 1
    fpr = fp / count
    fn = sum(not search_fn(username)
        for username in usernames)
    return fpr, fn

# this block is to plot results of the methods. 
def plot_results(rows):
    import matplotlib.pyplot as plt

    methods = ["Linear", "Binary", "Hash", "Bloom", "Cuckoo", "Quotient"]
    plt.figure(figsize=(8, 5))

    for method in methods:
        points = sorted((n, runtime) for n, name, runtime in rows if name == method)
        x, y = zip(*points)
        plt.plot(x, y, label=method)
        
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
# 1000 queries are used for each experiment.
def benchmark(sizes, query_count=1000, repeats=5):
    runtime_rows = []
    fpr_rows = []
    
    # It generates the largest dataset so that it can be reused. 
    largest_dataset = make_dataset(max(sizes))
    save_dataset(largest_dataset)

    for n in sizes:
        print(f"\nTesting n={n:,}")
        usernames = largest_dataset[:n]
        queries = make_queries(n, query_count)
        table, bloom, cuckoo, quotient = build_structures(usernames)

        methods = [
            ("Linear", lambda q: linear_search(usernames, q)),
            ("Binary", lambda q: binary_search(usernames, q)),
            ("Hash", table.hash_search),
            ("Bloom", bloom.bloom_search),
            ("Cuckoo", cuckoo.cuckoo_search),
            ("Quotient", quotient.quotient_search)
        ]

        for name, search_fn in methods:
            runtime = median_time_per_query(search_fn, queries, repeats)
            runtime_rows.append((n, name, runtime))

            print(f"{name:>8}: {runtime:.3f} microseconds/query")
            
        # For probabilisti fileters
        for name, search_fn in methods[3:]: 
            fpr, fn = measure_filter_accuracy(search_fn, usernames)
            fpr_rows.append((n, name, p, fpr, fn))

            print(
                f"{name:>8}: "
                f"target FPR={p:.2%}, "
                f"measured FPR={fpr:.4%}, "
                f"false negatives={fn}"
            )

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
    sizes = [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000]
    benchmark(sizes)