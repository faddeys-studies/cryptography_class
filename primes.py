import random
import os


DEFAULT_PRIMES_TXT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "primes.txt"
)


class RandomPrimeNumberGenerator:
    def __init__(self, primes):
        self.primes = primes

    @classmethod
    def load_from_file(cls, primes_txt_path):
        with open(primes_txt_path) as f:
            primes = list(map(int, f.readlines()))
        return cls(primes)

    def __call__(self, minimum=None, maximum=None):
        primes = self.primes
        if minimum is None:
            l = 0
        else:
            l = _bin_search(primes, minimum)
        if maximum is None:
            r = len(primes)
        else:
            r = _bin_search(primes, maximum)
        return primes[random.randrange(l, r)]


get_random_prime = RandomPrimeNumberGenerator.load_from_file(
    DEFAULT_PRIMES_TXT_PATH
)


def _bin_search(array, value):
    """
    Returns index of first item no less than given value.
    It is assumed that array items are unique and sorted in ascending order.
    """
    l, r = 0, len(array)
    m = l
    while l < r:
        m = (l + r) // 2
        m_val = array[m]
        if m_val == value:
            return m
        if m_val > value:
            r = m
        else:
            l = m + 1
    if array[m] < value:
        m += 1
    return m


if __name__ == "__main__":

    def _test_binsearch():
        for _ in range(1000):
            arr = sorted(random.sample(range(1000), 500))
            x = random.randint(-100, 1100)
            i = _bin_search(arr, x)
            msg = (x, i, arr[i - 1 : i + 2])
            assert 0 <= i <= len(arr), msg
            if i < len(arr):
                assert x <= arr[i], msg
            if i > 0:
                assert x > arr[i - 1], msg

    _test_binsearch()