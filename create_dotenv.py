import os
from cryptography.fernet import Fernet
def create():
    key = Fernet.generate_key()
    key=key.decode()
    with open("Usersdb/.env", "w") as f:
        f.write(f"SECRET={key}")