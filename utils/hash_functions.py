def fnv1a64(value):
    """Return a 64-bit FNV-1a hash."""
    hash_value = 0xcbf29ce484222325
    fnv_prime = 0x00000100000001b3

    for byte in str(value).encode("utf-8"):
        hash_value ^= byte
        hash_value *= fnv_prime
        hash_value &= 0xFFFFFFFFFFFFFFFF

    return hash_value


def djb2_64(value):
    """Return a 64-bit DJB2 hash."""
    hash_value = 5381

    for byte in str(value).encode("utf-8"):
        hash_value = (
            (hash_value * 33) + byte
        ) & 0xFFFFFFFFFFFFFFFF

    return hash_value