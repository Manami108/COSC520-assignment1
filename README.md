# COSC 520 Assignment 1

Welcome! 

This repository contains the implementation and experimental comparison of algorithms and data structures for the login checker problem. The implemented algorithms are **Linear Search**, **Binary Search**, **Hash Table**, **Bloom Filter**, **Cuckoo Filter**, and **Quotient Filter**.

All algorithms and data structures were implemented from scratch in Python.

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

## Requirements and Running Instructions

This project was developed using Python 3.12. The benchmark also requires `matplotlib` for generating the runtime plots. If `matplotlib` is not installed, it can be installed using:

```bash
pip install matplotlib
```

To run the unit tests, execute the following command:

```bash
python3 test.py
```

To run the benchmark experiments, execute the following command:

```bash
python3 benchmark.py
```

The benchmark measures the lookup runtime of each method using dataset sizes from 1,000 to 10,000,000 usernames. You may want to adjust the maximum dataset size depending on your computer's performance and available resources.

## Generated Files

Running the benchmark generates the following files:

- `usernames_dataset.txt` for the generated synthetic username dataset
- `benchmark_results.csv` for the measured lookup runtimes
- `lookup_runtime.png` for the runtime comparison of the five required methods
- `filter_runtime.png` for the comparison of the Bloom, Cuckoo, and Quotient filters

## Dataset

The experiments use a synthetic dataset with usernames in the format `user_` followed by a 12-digit number.

For example:

```text
user_000000000000
user_000000000001
user_000000000002
```

The complete dataset used for the experiments is available at:
https://drive.google.com/file/d/1nz98OVoMo_rhDoDe5qlvcd9dyyD6iCeS/view?usp=sharing

## Results

If you would like to see the results without running the benchmark, you can directly check the generated plots:

- `lookup_runtime.png` — comparison of the five required methods
- `filter_runtime.png` — comparison of the Bloom, Cuckoo, and Quotient filters

Happy coding!
