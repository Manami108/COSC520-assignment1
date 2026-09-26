MASK64 = (1 << 64) - 1
FNV_OFFSET = 1469598103934665603
FNV_PRIME = 1099511628211


# ============================================================
# HASH FUNCTIONS
# ============================================================

def fnv1a64(text, seed=0):
    """
    Input:
        text: string to hash
        seed: optional integer seed

    Output:
        deterministic 64-bit hash value

    Description:
        Manual implementation of the FNV-1a hash algorithm.
    """
    h = (FNV_OFFSET ^ seed) & MASK64

    for byte in text.encode("utf-8"):
        h ^= byte
        h = (h * FNV_PRIME) & MASK64

    return h


def djb2_64(text, seed=5381):
    """
    Input:
        text: string to hash
        seed: starting hash value

    Output:
        deterministic 64-bit hash value

    Description:
        Manual DJB2-style hash used as a second independent hash.
    """
    h = seed & MASK64

    for byte in text.encode("utf-8"):
        h = ((h << 5) + h + byte) & MASK64

    return h


def mix64(x):
    """
    Input:
        integer x

    Output:
        mixed 64-bit integer

    Description:
        Improves bit distribution before selecting a Cuckoo bucket.
    """
    x &= MASK64

    x ^= x >> 33
    x = (x * 0xFF51AFD7ED558CCD) & MASK64

    x ^= x >> 33
    x = (x * 0xC4CEB9FE1A85EC53) & MASK64

    x ^= x >> 33

    return x & MASK64


def next_power_of_two(x):
    """
    Input:
        positive integer x

    Output:
        smallest power of two greater than or equal to x
    """
    if x <= 1:
        return 1

    return 1 << (x - 1).bit_length()