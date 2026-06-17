# crawler/bloom_filter.py
import math
import hashlib

class BloomFilter:
    """
    Tracks which URLs we've already visited.
    Uses very little memory even for millions of URLs.
    """

    def __init__(self, capacity=1_000_000, error_rate=0.001):
        self.capacity = capacity
        self.error_rate = error_rate

        # How many bits do we need?
        self.size = int(
            -capacity * math.log(error_rate) / (math.log(2) ** 2)
        )

        # How many hash functions to use?
        self.hash_count = max(1, int(
            self.size / capacity * math.log(2)
        ))

        # The actual storage — a big array of 0s
        self.bits = bytearray(self.size // 8 + 1)

        # Counter for how many URLs added
        self.count = 0

    def _get_positions(self, url):
        """Figure out which bit positions this URL maps to."""
        h1 = int(hashlib.sha256(url.encode()).hexdigest(), 16) % self.size
        h2 = int(hashlib.md5(url.encode()).hexdigest(), 16) % self.size
        return [(h1 + i * h2) % self.size for i in range(self.hash_count)]

    def add(self, url):
        """Add a URL to the filter."""
        for pos in self._get_positions(url):
            self.bits[pos // 8] |= (1 << (pos % 8))
        self.count += 1

    def __contains__(self, url):
        """
        Check if URL was already added.
        True = probably seen before
        False = definitely never seen (100% accurate)
        """
        return all(
            self.bits[pos // 8] & (1 << (pos % 8))
            for pos in self._get_positions(url)
        )

    def __repr__(self):
        return (f"BloomFilter(capacity={self.capacity:,}, "
                f"size_bits={self.size:,}, "
                f"hash_count={self.hash_count}, "
                f"urls_added={self.count:,})")


# This only runs when you run this file directly
if __name__ == "__main__":
    print("Creating Bloom Filter...")
    bf = BloomFilter(capacity=1000, error_rate=0.01)
    print(bf)

    bf.add("https://python.org")
    bf.add("https://wikipedia.org")
    bf.add("https://github.com")

    print("\nChecking URLs:")
    print(f"python.org:    {'SEEN' if 'https://python.org' in bf else 'NEW'}")
    print(f"wikipedia.org: {'SEEN' if 'https://wikipedia.org' in bf else 'NEW'}")
    print(f"google.com:    {'SEEN' if 'https://google.com' in bf else 'NEW'}")
    print(f"github.com:    {'SEEN' if 'https://github.com' in bf else 'NEW'}")

    print("\nBloom Filter working correctly!")