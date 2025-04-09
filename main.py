import os

root_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(root_dir, "Assets")
wordlist_dir = os.path.join(assets_dir, "wordlists")
upload_dir = os.path.join(root_dir, "Uploads")

if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

if not os.path.exists(wordlist_dir):
    os.makedirs(wordlist_dir)
