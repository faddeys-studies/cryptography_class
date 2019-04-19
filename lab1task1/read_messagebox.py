import os
from lab1task1 import rsa_lib
import base64


def main():
    public_key = rsa_lib.load_public_key("public.key.txt")
    for filename in os.listdir("."):
        if filename.endswith(".message.txt"):
            with open(filename, "rb") as f:
                contents_bytes = f.read()
            signature, _, contents_bytes = contents_bytes.partition(b"\n")
            contents = contents_bytes.decode("utf-8")
            signature_bytes = base64.b64decode(signature)

            sig_decrypt = rsa_lib.decrypt(signature_bytes, public_key)
            sig_decrypt = sig_decrypt.decode("utf-8")
            valid = sig_decrypt == contents

            print()
            print("File:", filename)
            print("Contents:", contents)
            print("Signature:", signature.decode("utf-8"))
            print("Signature OK" if valid else "Signature is invalid!")


if __name__ == '__main__':
    main()
