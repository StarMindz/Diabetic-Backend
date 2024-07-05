import os

def generate_hex(length=32):
    return os.urandom(length).hex()

print(generate_hex())
