# COSC 520 Assignment 1

This repository contains the implementation and experimental comparison of algorithms and data structures for the login checker problem.

The implemented methods are as follows:
- Linear Search
- Binary Search
- Hash Table
- Bloom Filter
- Cuckoo Filter
- Quotient Filter

All algorithms and data structures were implemented from scratch in Python.

## Requirements

- Python 3.12 or later
- matplotlib

Install matplotlib if necessary:

```bash
pip install matplotlib
```

## Run the Unit Tests

From the root directory of the repository, run:

```bash
python3 test.py
```

The unit tests check the search, insertion, and deletion operations where applicable.

## Run the Benchmark

Run:

```bash
python3 benchmark.py
```

The benchmark evaluates lookup runtime across the following dataset sizes:

```text
1,000
2,000
5,000
10,000
20,000
50,000
100,000
200,000
500,000
1,000,000
2,000,000
5,000,000
10,000,000
```

For each dataset size, 1,000 lookup queries are generated. Approximately 50% of the queries correspond to usernames that are present in the dataset, while the remaining 50% correspond to usernames that are absent.

The same query set is used for all methods at each dataset size.

Each set of 1,000 queries is executed five times for each method. The runtime of each repetition is divided by the number of queries, and the median of the five per-query runtimes is reported in microseconds per query.

## Generated Files

Running the benchmark generates the following files:

- `usernames_dataset.txt` — generated synthetic username dataset
- `benchmark_results.csv` — measured lookup runtimes
- `lookup_runtime.png` — runtime comparison of the five required methods
- `filter_runtime.png` — runtime comparison of the Bloom, Cuckoo, and Quotient filters

## Repository Structure

```text
COSC520-assignment1/
│
├── algorithms/
│   ├── linear_search.py
│   ├── binary_search.py
│   ├── hash_table.py
│   ├── bloom_filter.py
│   ├── cuckoo_filter.py
│   └── quotient_filter.py
│
├── utils/
│   └── hash_functions.py
│
├── benchmark.py
├── dataset.py
├── test.py
└── README.md
```

## Dataset

The experiments use a synthetic dataset of usernames. Each username follows the format `user_` followed by a 12-digit numeric identifier.

For example:

```text
user_000000000000
user_000000000001
user_000000000002
```

The usernames are generated in ascending numerical order and are therefore also lexicographically sorted.

The complete dataset used for the experiments is available at:

https://drive.google.com/file/d/1nz98OVoMo_rhDoDe5qlvcd9dyyD6iCeS/view?usp=sharing

## Implementation Details

The hash table uses:

- FNV-1a hashing
- Linear probing for collision resolution
- A target load factor of approximately 0.7

The Bloom filter uses:

- A target false-positive rate of 1%
- FNV-1a and DJB2 as base hash functions
- Double hashing to generate the required bit-array indices

The Cuckoo filter uses:

- A target false-positive rate of 1%
- Four fingerprint slots per bucket
- A target load factor of 0.90
- Up to 500 relocation attempts during insertion

The Quotient filter uses:

- A target false-positive rate of 1%
- A target load factor of 0.70
- A number of slots rounded up to the next power of two

## Author

Manami Yano  
M.Sc. in Computer Science  
The University of British Columbia, Okanagan Campus
