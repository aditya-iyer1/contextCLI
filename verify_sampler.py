
import sys
import os

# Ensure src is in path if running directly
sys.path.insert(0, os.path.abspath("src"))

from contextcliff.data.sampler import balance_samples

print("Running sampler verification with buffer_size=20")
try:
    # Use a very small buffer to verify logic quickly
    # Note: balance_samples default is 2000, but we pass buffer_size if the function accepts it.
    # Looking at code: balance_samples(n_per_bin: int = 10, buffer_size: int = 2000)
    samples = balance_samples(n_per_bin=2, buffer_size=20)
    print(f"Successfully generated {len(samples)} samples.")
    
    if os.path.exists("manifest.json"):
        print("manifest.json created.")
        with open("manifest.json", "r") as f:
            content = f.read()
            if len(content) > 10:
                print("manifest.json has content.")
            else:
                print("manifest.json is empty!")
    else:
        print("manifest.json NOT created.")

except Exception as e:
    print(f"Verification failed: {e}")
