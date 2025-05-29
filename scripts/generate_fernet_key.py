from cryptography.fernet import Fernet

def generate_fernet_key():
    """Generate a Fernet key for Airflow."""
    key = Fernet.generate_key()
    print(f"Generated Fernet key: {key.decode()}")
    return key.decode()

if __name__ == "__main__":
    generate_fernet_key() 