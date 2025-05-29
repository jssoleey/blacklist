# login.py
import os, json, hashlib

BASE_DIR = "/data/blacklist_data"

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login(name, password):
    user_dir = os.path.join(BASE_DIR, f"{name}_{hash_password(password)}")
    os.makedirs(user_dir, exist_ok=True)

    index_file = os.path.join(BASE_DIR, "index.json")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            index = json.load(f)
    else:
        index = {}

    key = f"{name}_{password[-4:]}"
    if key not in index:
        index[key] = os.path.basename(user_dir)
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    return user_dir