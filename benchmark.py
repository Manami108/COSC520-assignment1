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


# ============================================================
# BENCHMARK QUERIES
# ============================================================

def make_queries(
    n,
    count=100,
    seed=123
):
    """
    Create a query set containing:

        50% existing usernames
        50% nonexistent usernames
    """

    rng = random.Random(seed)

    half = count // 2


    present = [

        f"user_{rng.randrange(n):012d}"

        for _ in range(half)

    ]


    absent = [

        f"user_{n + i + 1:012d}"

        for i in range(
            count - half
        )

    ]


    queries = (
        present
        + absent
    )


    rng.shuffle(queries)

    return queries


def median_time_per_query(
    search_function,
    queries,
    repeats=3
):
    """
    Measure lookup time several times.

    Output:
        median microseconds per query
    """

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


# ============================================================
# BUILD ADVANCED STRUCTURES
# ============================================================

def build_structures(
    usernames
):
    """
    Build:

        Hash table
        Bloom filter
        Cuckoo filter
    """

    n = len(usernames)


    table = HashTable(n)


    bloom = BloomFilter(n)


    cuckoo = CuckooFilter(
        n,
        fingerprint_bits=16
    )


    for username in usernames:

        table.insert(
            username
        )

        bloom.add(
            username
        )


        if not cuckoo.insert(
            username
        ):

            raise RuntimeError(
                "Cuckoo insertion failed. "
                "Use a lower target_load "
                "or increase table size."
            )


    return (
        table,
        bloom,
        cuckoo
    )


# ============================================================
# PLOT RESULTS
# ============================================================

def plot_results(rows):
    """
    Create lookup_runtime.png.

    Uses logarithmic axes because n and the running times
    can differ by several orders of magnitude.
    """

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


# ============================================================
# FULL BENCHMARK
# ============================================================

def benchmark(
    sizes,
    query_count=100,
    repeats=3
):
    """
    Compare all five methods.

    Outputs:
        usernames_dataset.txt
        benchmark_results.csv
        lookup_runtime.png
    """

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


        usernames = (
            largest_dataset[:n]
        )


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


        # --------------------------------------------
        # FALSE-POSITIVE EXPERIMENT
        # --------------------------------------------

        absent = [

            f"not_present_{i:012d}"

            for i in range(5000)

        ]


        bloom_fp = (

            sum(
                bloom.contains(q)
                for q in absent
            )

            / len(absent)

        )


        cuckoo_fp = (

            sum(
                cuckoo.contains(q)
                for q in absent
            )

            / len(absent)

        )


        print(
            "Bloom false-positive rate:  "
            f"{bloom_fp:.4%}"
        )


        print(
            "Cuckoo false-positive rate: "
            f"{cuckoo_fp:.4%}"
        )


    # --------------------------------------------
    # SAVE CSV RESULTS
    # --------------------------------------------

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


    # --------------------------------------------
    # CREATE GRAPH
    # --------------------------------------------

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


# ============================================================
# MAIN
# ============================================================

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

        200_000

    ]


    benchmark(

        SIZES,

        query_count=100,

        repeats=3

    )