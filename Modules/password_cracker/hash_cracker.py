import re
import hashlib
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
assets_dir = os.path.join(root_dir, "Assets")
wordlist_dir = os.path.join(assets_dir, "wordlists")
wordlist_file = os.path.join(wordlist_dir, "rockyou.txt")


def identify_hash_type(hash_string):
    # Specific patterns for common hash types
    if re.match(r"^\$2[aby]\$.{56}$", hash_string):  # bcrypt
        print(f"[!] BCRYPT is not supported by hashlib (use Hashcat).")
        return False
    elif re.match(r"^\$argon2(id|i|d)\$", hash_string):  # argon2
        print(f"[!] ARGON2 is not supported by hashlib (use Hashcat).")
        return False
    elif re.match(r"^[a-fA-F0-9]{32}$", hash_string):  # MD5
        print("[!] Detected 32-character hex hash (MD5 or NTLM). Defaulting to MD5.")
        return "md5"
    elif re.match(r"^[a-fA-F0-9]{40}$", hash_string):  # SHA1
        return "sha1"
    elif re.match(r"^[a-fA-F0-9]{64}$", hash_string):  # SHA256
        return "sha256"
    elif re.match(r"^[a-fA-F0-9]{128}$", hash_string):  # SHA512
        return "sha512"
    else:
        print("[!] Could not identify hash algorithm.")
        return False


def single_crack_hash(hash_to_crack):
    hash_to_crack = hash_to_crack.strip()
    algorithm = identify_hash_type(hash_to_crack)

    if not algorithm:
        print("[!] Unsupported hash type or algorithm could not be identified.")
        return None

    print(f"[~] Cracking using detected algorithm: {algorithm.upper()}")

    try:
        # Open the wordlist file
        with open(wordlist_file, "r", encoding="latin-1") as f:
            # Read the wordlist file line by line with index
            for idx, word in enumerate(f):
                word = word.strip()
                word_bytes = word.encode("utf-8")

                # Hashing based on algorithm
                if algorithm == "md5":
                    hashed = hashlib.md5(word_bytes).hexdigest()
                elif algorithm == "sha1":
                    hashed = hashlib.sha1(word_bytes).hexdigest()
                elif algorithm == "sha256":
                    hashed = hashlib.sha256(word_bytes).hexdigest()
                elif algorithm == "sha512":
                    hashed = hashlib.sha512(word_bytes).hexdigest()

                if hashed.lower() == hash_to_crack.lower():  # Compare in lowercase
                    # If a match is found, print the password and return it
                    print(f"[+] Password found: {word}")
                    return word

                if idx % 100000 == 0:  # Print progress every 100,000 attempts
                    print(f"[~] Tried {idx} passwords...")

        print("[-] Password not found.")
        return None

    except FileNotFoundError:  # Handle the case where the wordlist file is not found
        print("[!] rockyou.txt file not found!")
        return None
