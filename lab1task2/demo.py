from lab1task2 import elgamal_lib
import random


def main():
    private_key, public_key = elgamal_lib.make_keypair()

    print(f"private key: x = {private_key}")
    print(f"public key: (p, g, y) = {public_key}")

    t = random.randrange(public_key[0])
    print(f"message: t = {t}")

    signature, r = elgamal_lib.sign_number(t, private_key, public_key)
    print(f"signing with r = {r}")
    print(f"signature (c1, c2) = {signature}")

    ok, (yc1, c1c2, gt, p) = elgamal_lib.check_number_signature(
        t, signature, public_key
    )
    print(
        f"verifying: y^c1 * c1^c2 (mod p) = {yc1} * {c1c2} (mod {p}) = {(yc1*c1c2)%p}"
    )
    print(f"verifying: g^t(mod p) = {gt} (mod {p}) = {gt % p}")
    print("signature", "OK" if ok else "invalid!")


if __name__ == '__main__':
    main()
