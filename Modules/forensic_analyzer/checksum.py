import hashlib
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
upload_dir = os.path.join(root_dir, "Uploads")


def verify_file_checksum(file_path: str, expected_hash: str, hash_algorithm: str):
    results = []
    expected_hash = expected_hash.lower().strip()
    hash_algorithm = hash_algorithm.lower().strip()

    results.append(f"**🔒 Verifying checksum with `{hash_algorithm.upper()}`**")

    try:
        if hash_algorithm == "md5":
            hasher = hashlib.md5()
        elif hash_algorithm == "sha1":
            hasher = hashlib.sha1()
        elif hash_algorithm == "sha256":
            hasher = hashlib.sha256()
        elif hash_algorithm == "sha512":
            hasher = hashlib.sha512()
        else:
            return [f"❌ Unsupported hash algorithm: {hash_algorithm}"]

        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                hasher.update(chunk)

        actual_hash = hasher.hexdigest()

        results.append(f"📥 Expected: `{expected_hash}`")
        results.append(f"📤 Actual  : `{actual_hash}`")

        if actual_hash == expected_hash:
            results.append("✅ File checksum matches. File is intact.")
        else:
            results.append(
                "❗ File checksum does NOT match. File may be corrupt or manipulated."
            )

    except Exception as e:
        results.append(f"❌ Failed to compute hash: {e}")

    return results
