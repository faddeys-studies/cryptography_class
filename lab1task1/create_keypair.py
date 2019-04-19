from lab1task1 import rsa_lib


def main():
    private_key, public_key = rsa_lib.make_keypair()
    rsa_lib.save_private_key(private_key, 'private.key.txt')
    rsa_lib.save_public_key(public_key, 'public.key.txt')


if __name__ == '__main__':
    main()
