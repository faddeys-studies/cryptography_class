import sys
import base64
import random
from lab1task1 import rsa_lib


def _generate_valid_block(n, e, block_size):
    target_bitlen = 8 * block_size
    while True:
        c = random.choice(range(n))
        b = rsa_lib._fastmul(c, e, n)
        if b.bit_length() <= target_bitlen:
            return c


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m lab1task1.create_malicious_message [message_name]")
        print("ERROR: not enough arguments")
        exit(1)
    msg_name = sys.argv[1]

    pub_n, pub_e = public_key = rsa_lib.load_public_key("public.key.txt")

    block_size = pub_n.bit_length() // 8

    # cipher_blocks = random.choices(range(pub_n), k=101 * (block_size+1))
    cipher_blocks = [
        _generate_valid_block(pub_n, pub_e, block_size)
        for _ in range(50)
    ]
    cipher = b"".join(rsa_lib._blocks_to_bytes_chunks(cipher_blocks, block_size + 1))

    text = rsa_lib.decrypt(cipher, public_key)

    with open(msg_name + ".message.txt", "wb") as f:
        f.write(base64.b64encode(cipher) + b"\n" + text)


if __name__ == "__main__":
    main()
