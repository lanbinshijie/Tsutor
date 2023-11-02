import os
import hashlib
import shutil
import json

# Helper Functions
def create_cache():
    if not os.path.exists("cache"):
        os.mkdir("cache")

def compute_md5(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
        return hashlib.md5(content).hexdigest()[:10]

def extract_filename_category(filename):
    file_name, category = filename.rsplit("_", 1)[0], filename.rsplit("_", 1)[1].rsplit(".", 1)[0]
    return file_name, category

def save_to_json(data, filename="lists.json"):
    with open(filename, "w") as file:
        json.dump(data, file)

def load_from_json(filename="lists.json"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return []

# Main Functions
def list_and_cache_passages(rebuild=False):
    if not rebuild:
        return load_from_json()
    
    create_cache()
    base_dir = "passages"
    files = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f)) and f.endswith(".md")]
    extracted_data = []

    for f in files:
        file_name, category = extract_filename_category(f)
        file_hash = compute_md5(os.path.join(base_dir, f))
        
        # Copy the file to cache with the hash as the filename
        shutil.copy(os.path.join(base_dir, f), os.path.join("cache", f"{file_hash}.md"))
        extracted_data.append({"filename": file_name, "category": category, "hash": file_hash})
    
    save_to_json(extracted_data)
    return extracted_data

def get_file_path_by_hash(file_hash):
    return os.path.join("cache", f"{file_hash}.md")

def read_file_content(file_path):
    with open(file_path, 'r', encoding="utf-8") as file:
        title = file.readline().strip()  # Assuming first line is the title
        content = file.read().strip()  # Rest of the file is the content
    return title, content

def getByIndex(index):
    data = list_and_cache_passages()
    if int(index) < len(data):
        file_hash = data[int(index)]["hash"]
        file_path = get_file_path_by_hash(file_hash)
        return read_file_content(file_path)
    else:
        return None, None

def getById(file_hash):
    file_path = get_file_path_by_hash(file_hash)
    if os.path.exists(file_path):
        return read_file_content(file_path)
    else:
        return None, None

def getByName(filename):
    data = list_and_cache_passages()
    matched_files = [item for item in data if item["filename"] == filename]
    if matched_files:
        file_hash = matched_files[0]["hash"]
        file_path = get_file_path_by_hash(file_hash)
        return read_file_content(file_path)
    else:
        return None, None