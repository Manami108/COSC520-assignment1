MASK64 = 0xFFFFFFFFFFFFFFFF
 
def fnv1a64(value):
    # It generates a 64-bit FNV-1a hash value from the input.
    # The below is the standard 64-bit offset basis and FNV prime.  
    h = 0xcbf29ce484222325
    fnv_prime = 0x00000100000001b3
 
    for byte in str(value).encode("utf-8"):
        # First, it applies XOR.
        h ^= byte
        # Then, the result is multiplied by the FNV prime, and the result is limitted to 64 bits.
        h = (h * fnv_prime) & MASK64
    return h
 
 
def djb2_64(value):
    # It generates a 64-bit DJB2 hash value from the input.
    # DJB2 traditionally starts with a hash value of 5381.
    h = 5381
 
    for byte in str(value).encode("utf-8"):
        # Each step multiplies the current hash by 33 and adds the next byte. 
        h = (h * 33 + byte) & MASK64
    return h
 
def mix64(x):
    # It mixes the bits of a 64-bit integer.
    x &= MASK64
    x ^= x >> 33
    x = (x * 0xff51afd7ed558ccd) & MASK64
    x ^= x >> 33
    x = (x * 0xc4ceb9fe1a85ec53) & MASK64
    x ^= x >> 33
    return x