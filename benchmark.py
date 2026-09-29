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

def make_queries(n, count, seed=123):
    rng = random.Random(seed)
    half = count // 2
    present = [
        f"user_{rng.randrange(n):012d}"
        for _ in range(half)
    ]

    absent = [
        f"user_{n + i + 1:012d}"
        for i in range(count - half)
    ]

    queries = (present + absent)

    rng.shuffle(queries)
    return queries

def median_time_per_query(
    search_function,
    queries,
    repeats
):

    samples = []
    for _ in range(repeats):
        start = (
            time.perf_counter()
        )

        for query in queries:
            search_function(
                query
            )

        elapsed = (
            time.perf_counter()
            - start
        )

        samples.append(
            elapsed
            / len(queries)
        )

    return (
        statistics.median(
            samples
        )
        * 1_000_000
    )

def build_structures(
    usernames
):
    n = len(usernames)
    table = HashTable(n)
    bloom = BloomFilter(n)
    cuckoo = CuckooFilter(n)

    for username in usernames:
        table.insert(username)
        bloom.add(username)
        if not cuckoo.insert(username):

            raise RuntimeError(
                "Cuckoo insertion failed. "
                "Use a lower target_load "
                "or increase table size."
            )
    return (table, bloom, cuckoo)

def plot_results(rows):
    import matplotlib.pyplot as plt


    methods = [

        "Linear",
        "Binary",
        "Hash",
        "Bloom",
        "Cuckoo"

    ]


    for method in methods:

        points = sorted(

            (
                n,
                us
            )

            for n, name, us
            in rows

            if name == method

        )


        plt.plot(

            [
                n
                for n, _
                in points
            ],

            [
                us
                for _, us
                in points
            ],

            marker="o",

            label=method

        )

# It can be not log scare
    plt.xscale("log")
    plt.yscale("log")


    plt.xlabel(
        "Number of stored logins, n"
    )

    plt.ylabel(
        "Median lookup time "
        "(microseconds/query)"
    )

    plt.title(
        "Login Checker "
        "Lookup-Time Comparison"
    )


    plt.legend()
    plt.grid(
        True,
        which="both",
        linestyle="--",
        linewidth=0.5
    )
    plt.tight_layout()


    plt.savefig(
        "lookup_runtime.png",
        dpi=200
    )
    plt.close()
    
def benchmark(
    sizes,
    query_count=1000,
    repeats=5
):
    rows = []


    largest_dataset = (
        make_dataset(
            max(sizes)
        )
    )


    save_dataset(
        largest_dataset
    )


    for n in sizes:

        print(
            f"\nTesting n={n:,}"
        )


        usernames = largest_dataset[:n]


        queries = make_queries(
            n,
            query_count
        )


        table, bloom, cuckoo = (
            build_structures(
                usernames
            )
        )


        methods = [

            (
                "Linear",

                lambda q,
                a=usernames:
                linear_search(
                    a,
                    q
                )
            ),

            (
                "Binary",

                lambda q,
                a=usernames:
                binary_search(
                    a,
                    q
                )
            ),

            (
                "Hash",
                table.contains
            ),

            (
                "Bloom",
                bloom.contains
            ),

            (
                "Cuckoo",
                cuckoo.contains
            )

        ]


        for (
            name,
            search_function
        ) in methods:

            us = (
                median_time_per_query(
                    search_function,
                    queries,
                    repeats
                )
            )


            rows.append(
                (
                    n,
                    name,
                    us
                )
            )


            print(
                f"{name:>7}: "
                f"{us:10.3f} "
                "us/query"
            )
            
    with open(
        "benchmark_results.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)
        writer.writerow(
            [
                "n",
                "method",
                "microseconds_per_query"
            ]
        )
        writer.writerows(
            rows
        )

    plot_results(rows)


    print(
        "\nCreated:"
    )

    print(
        "  usernames_dataset.txt"
    )

    print(
        "  benchmark_results.csv"
    )

    print(
        "  lookup_runtime.png"
    )

if __name__ == "__main__":

    # Start with these values.
    #
    # Increase them if your computer has enough
    # memory and the experiment finishes reasonably.

    SIZES = [
        1_000,
        5_000,
        10_000,
        50_000,
        100_000,
        200_000,
        500_000,
        1_000_000 ]

    benchmark(SIZES)