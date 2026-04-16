import os
import sys
import yaml
import re
import zipfile

# -------------------------
# LOAD CONFIG
# -------------------------

def load_mapping(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_lookup(mapping_list):
    lookup = {}

    for item in mapping_list:
        dev = item["DEV"]
        target = item["TARGET"]

        lookup[dev["name"]] = target["name"]
        lookup[str(dev["id"])] = str(target["id"])
        lookup[dev["federatedId"]] = target["federatedId"]

    return lookup


# -------------------------
# REPLACE ENGINE
# -------------------------

def replace_text(content, lookup):
    for k, v in lookup.items():
        content = re.sub(rf"\b{re.escape(k)}\b", v, content)
    return content


# -------------------------
# FILE PROCESSING
# -------------------------

def process_file(file_path, lookup):

    if file_path.endswith(".xml") or file_path.endswith(".json"):

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = replace_text(content, lookup)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    elif file_path.endswith(".zip"):
        process_zip(file_path, lookup)


def process_zip(zip_path, lookup):

    tmp_dir = zip_path + "_tmp"

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(tmp_dir)

    for root, _, files in os.walk(tmp_dir):
        for f in files:
            process_file(os.path.join(root, f), lookup)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(tmp_dir):
            for f in files:
                full = os.path.join(root, f)
                arc = os.path.relpath(full, tmp_dir)
                z.write(full, arc)


# -------------------------
# MAIN
# -------------------------

def main():

    mapping_file = os.getenv("RUNTIME_MAPPING_FILE")

    if not mapping_file:
        print("ERROR: RUNTIME_MAPPING_FILE not defined")
        sys.exit(1)

    print(f"Loading mapping: {mapping_file}")

    mapping = load_mapping(mapping_file)
    lookup = build_lookup(mapping["runtime_mapping"])

    files = os.getenv("CHANGED_FILES", "").splitlines()

    if not files:
        print("No files to process")
        return

    for f in files:
        if os.path.exists(f):
            print(f"Processing {f}")
            process_file(f, lookup)


if __name__ == "__main__":
    main()
