import hashlib
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
upload_dir = os.path.join(root_dir, "Uploads")


def verify_file_checksum(file_path: str, expected_hash: str, hash_algorithm: str):
    print(f"\nVerifying checksum with {hash_algorithm.upper()}")

    expected_hash = expected_hash.lower().strip()
    hash_algorithm = hash_algorithm.lower().strip()

    try:
        # Select the correct hasher
        if hash_algorithm == "md5":
            hasher = hashlib.md5()
        elif hash_algorithm == "sha1":
            hasher = hashlib.sha1()
        elif hash_algorithm == "sha256":
            hasher = hashlib.sha256()
        elif hash_algorithm == "sha512":
            hasher = hashlib.sha512()
        else:
            print(f"Unsupported hash algorithm: {hash_algorithm}")
            return

        # Read file and update hash
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                hasher.update(chunk)

        actual_hash = hasher.hexdigest()

        print(f"Expected: {expected_hash}")
        print(f"Actual  : {actual_hash}")

        if actual_hash == expected_hash:
            print("File checksum matches. File is intact.")
        else:
            print("File checksum does NOT match. File may be corrupt or manipulated.")

    except Exception as e:
        print(f"Failed to compute hash: {e}")
