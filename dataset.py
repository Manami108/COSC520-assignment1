# Create and save a dataset. 

def make_dataset(n):
    if n < 0:
        raise ValueError("n must be nonnegative")
    return [
        f"user_{i:012d}" 
        for i in range(n)
        ]
    
def save_dataset(values, path="usernames_dataset.txt"):
    with open(path, "w", encoding="utf-8") as file:
        for value in values:
            file.write(value + "\n")