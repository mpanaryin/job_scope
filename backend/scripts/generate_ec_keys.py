import os

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Path to the secrets directory
secrets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'secrets'))
private_key_path = os.path.join(secrets_dir, 'ec_private.pem')
public_key_path = os.path.join(secrets_dir, 'ec_public.pem')


if os.path.exists(private_key_path) or os.path.exists(public_key_path):
    print("[!] One or both key files already exist. Generation cancelled to avoid overwriting.")
    print(f"- Private: {private_key_path} {'(exists)' if os.path.exists(private_key_path) else ''}")
    print(f"- Public : {public_key_path} {'(exists)' if os.path.exists(public_key_path) else ''}")
else:
    private_key = ec.generate_private_key(ec.SECP256R1())

    with open(private_key_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    public_key = private_key.public_key()
    with open(public_key_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    print("Keys successfully generated")
