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


_default_prime_numbers_generator = RandomPrimeNumberGenerator.load_from_file(
    DEFAULT_PRIMES_TXT_PATH
)


def make_keypair(get_random_prime=None):
    if get_random_prime is None:
        get_random_prime = _default_prime_numbers_generator
    p = get_random_prime()
    q = get_random_prime()
    n = p * q
    m = (p - 1) * (q - 1)
    e = get_random_prime(maximum=m)
    assert e <= m - 1
    d, _ = _solve_diophantine(e, m)
    if d < 0:
        d += m
    assert ((e * d) % m) == 1
    pubkey = n, e
    private_key = d
    return private_key, pubkey


def save_private_key(private_key, filename):
    with open(filename, "w") as f:
        print(private_key, file=f)


def save_public_key(public_key, filename):
    n, e = public_key
    with open(filename, "w") as f:
        print(n, e, file=f)


def load_private_key(filename):
    with open(filename) as f:
        return int(f.read())


def load_public_key(filename):
    with open(filename) as f:
        return tuple(map(int, f.read().split()))


def encrypt(message: bytes, pubkey, private_key) -> bytes:
    d = private_key
    n, e = pubkey
    block_size = n.bit_length() // 8
    header = len(message).to_bytes(block_size, "little")
    blocks = _message_to_blocks(header + message, block_size)
    ciphered_blocks = [_fastmul(b, d, n) for b in blocks]
    return b"".join(_blocks_to_bytes_chunks(ciphered_blocks, block_size + 1))


def decrypt(cipher: bytes, pubkey) -> bytes:
    n, e = pubkey
    block_size = n.bit_length() // 8
    ciphered_blocks = _message_to_blocks(cipher, block_size + 1)
    blocks = [_fastmul(b, e, n) for b in ciphered_blocks]
    message = b"".join(_blocks_to_bytes_chunks(blocks, block_size))
    length = int.from_bytes(message[:block_size], "little")
    return message[block_size : block_size + length]


def _message_to_blocks(message, block_size):
    return [
        int.from_bytes(message[i : i + block_size], "little")
        for i in range(0, len(message), block_size)
    ]


def _blocks_to_bytes_chunks(blocks, block_size):
    return [b.to_bytes(block_size, byteorder="little") for b in blocks]


def _fastmul(x, d, mod):
    r = 1
    p = x
    mask = 1
    for bit in range(d.bit_length()):
        if mask & d:
            r *= p
            r %= mod
        mask <<= 1
        p *= p
        p %= mod
    return r


def _solve_diophantine(a, b):
    # assume that gcd(a, b) == 1
    if a > b:
        a, b = b, a
    if a == 0:
        return 0, 1
    x1, y1 = _solve_diophantine(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return x, y


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

    def _test_fastmul():
        for _ in range(1000):
            x = random.randint(1, 1000)
            d = random.randint(1, 1000)
            mod = random.randint(11, 1009)
            actual = _fastmul(x, d, mod)
            expected = (x ** d) % mod
            assert actual == expected, (x, d, mod, actual, expected)

    _test_fastmul()

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

    def _test_encrypt_decrypt():
        private_key, public_key = make_keypair()
        for _ in range(1000):
            message = bytes(random.choices(range(256), k=1000))
            cipher = encrypt(message, public_key, private_key)
            deciphered = decrypt(cipher, public_key)
            # if message != deciphered:
            #     cipher = encrypt(message, public_key, private_key)
            #     deciphered = decrypt(cipher, public_key)
            assert message == deciphered, (message, deciphered)

    _test_encrypt_decrypt()

"""
from lab1task1.rsa_lib import *
private_key, public_key = make_keypair()
while True:
    message = bytes(random.choices(range(256), k=1000))
    cipher = encrypt(message, public_key, private_key)
    deciphered = decrypt(cipher, public_key)
    if message != deciphered:
        break
"""
