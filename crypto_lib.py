import random


def message_to_blocks(message, block_size):
    return [
        int.from_bytes(message[i : i + block_size], "little")
        for i in range(0, len(message), block_size)
    ]


def blocks_to_bytes_chunks(blocks, block_size):
    return [b.to_bytes(block_size, byteorder="little") for b in blocks]


def fastpow(x, d, mod):
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


def solve_diophantine(a, b):
    # assume that gcd(a, b) == 1
    if a > b:
        a, b = b, a
    if a == 0:
        return 0, 1
    x1, y1 = solve_diophantine(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return x, y


def inverse_in_group(a, n):
    return solve_diophantine(a, n)[0]


def gcd(a, b):
    if a < b:
        a, b = b, a
    while b != 0:
        a, b = b, a % b
    return a


if __name__ == "__main__":

    def _test_fastmul():
        for _ in range(1000):
            x = random.randint(1, 1000)
            d = random.randint(1, 1000)
            mod = random.randint(11, 1009)
            actual = fastpow(x, d, mod)
            expected = (x ** d) % mod
            assert actual == expected, (x, d, mod, actual, expected)

    _test_fastmul()
