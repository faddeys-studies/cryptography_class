import random
import primes
import crypto_lib


def make_keypair():
    p = primes.get_random_prime()
    g = random.randrange(2, p - 1)
    x = random.randrange(2, p - 1)
    y = crypto_lib.fastmul(g, x, p)
    private_key = x
    public_key = p, g, y
    return private_key, public_key


def sign_number(t, private_key, public_key):
    x = private_key
    p, g, y = public_key

    r = p - 1
    while crypto_lib.gcd(r, p - 1) != 1:
        r = 2 * random.randrange(1, (p - 1) // 2) + 1
    c1 = crypto_lib.fastmul(g, r, p)
    c2, _ = crypto_lib.solve_diophantine(r, p-1)
    c2 = (c2 * (t - x * c1)) % (p - 1)
    assert (c2 * r + x * c1 - t) % (p - 1) == 0
    return (c1, c2), r


def check_number_signature(t, signature, public_key):
    p, g, y = public_key
    c1, c2 = signature
    yc1 = crypto_lib.fastmul(y, c1, p)
    c1c2 = crypto_lib.fastmul(c1, c2, p)
    gt = crypto_lib.fastmul(g, t, p)
    return (yc1 * c1c2 - gt) % p == 0, (yc1, c1c2, gt, p)
