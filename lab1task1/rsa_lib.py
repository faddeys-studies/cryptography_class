import random
import primes
import crypto_lib


def make_keypair():
    p = primes.get_random_prime()
    q = primes.get_random_prime()
    n = p * q
    m = (p - 1) * (q - 1)
    e = primes.get_random_prime(maximum=m)
    assert e <= m - 1
    d, _ = crypto_lib.solve_diophantine(e, m)
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
    blocks = crypto_lib.message_to_blocks(header + message, block_size)
    ciphered_blocks = [crypto_lib.fastmul(b, d, n) for b in blocks]
    return b"".join(crypto_lib.blocks_to_bytes_chunks(ciphered_blocks, block_size + 1))


def decrypt(cipher: bytes, pubkey) -> bytes:
    n, e = pubkey
    block_size = n.bit_length() // 8
    ciphered_blocks = crypto_lib.message_to_blocks(cipher, block_size + 1)
    blocks = [crypto_lib.fastmul(b, e, n) for b in ciphered_blocks]
    message = b"".join(crypto_lib.blocks_to_bytes_chunks(blocks, block_size))
    length = int.from_bytes(message[:block_size], "little")
    return message[block_size : block_size + length]


if __name__ == "__main__":

    def _test_encrypt_decrypt():
        private_key, public_key = make_keypair()
        for _ in range(1000):
            message = bytes(random.choices(range(256), k=1000))
            cipher = encrypt(message, public_key, private_key)
            deciphered = decrypt(cipher, public_key)
            assert message == deciphered, (message, deciphered)

    _test_encrypt_decrypt()
