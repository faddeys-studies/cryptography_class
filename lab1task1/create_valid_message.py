import sys
import base64
from lab1task1 import rsa_lib


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python -m lab1task1.create_valid_message "
            "[message_name] [message_contents]"
        )
        print("ERROR: not enough arguments")
        exit(1)
    msg_name = sys.argv[1]
    message = " ".join(sys.argv[2:])

    private_key = rsa_lib.load_private_key("lab1task1/private.key.txt")
    public_key = rsa_lib.load_public_key("lab1task1/public.key.txt")
    cipher = rsa_lib.encrypt(message.encode("utf-8"), public_key, private_key)

    with open("lab1task1/" + msg_name + ".message.txt", "wb") as f:
        f.write(base64.b64encode(cipher) + b"\n" + message.encode("utf-8"))


if __name__ == '__main__':
    main()
