# ============================================================
# DATASET
# ============================================================

def make_dataset(n):
    """
    Input:
        n: number of usernames

    Output:
        list containing n unique usernames

    The fixed-width numbers make the list already sorted.
    """

    return [
        f"user_{i:012d}"
        for i in range(n)
    ]


def save_dataset(
    values,
    path="usernames_dataset.txt"
):
    """
    Save generated usernames to disk.

    The generated file can later be uploaded and linked
    in the assignment report.
    """

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        for value in values:

            file.write(
                value + "\n"
            )