import os
import zipfile
import tempfile
import shutil
import json
import re

# =========================
# CONFIG
# =========================

DEV_NAME = "AG_IICS_DEV_AZU_SLF"
QA_NAME = "AG_IICS_QA_AZU_SLF"

DEV_ID = "5YHmu7Kj5qBbUKsaUWa5uB"
QA_ID = "1L0QenaNUCYjwKyrwhjO6a"


# =========================
# JSON PROCESSING
# =========================

def process_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        def replace_values(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "runtimeEnvironmentId" and v == DEV_ID:
                        obj[k] = QA_ID
                    elif k == "runtimeEnvironmentName" and v == DEV_NAME:
                        obj[k] = QA_NAME
                    else:
                        replace_values(v)
            elif isinstance(obj, list):
                for item in obj:
                    replace_values(item)

        replace_values(data)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"[JSON] Updated: {file_path}")

    except Exception as e:
        print(f"[JSON] Skipped (error): {file_path} -> {e}")


# =========================
# XML PROCESSING
# =========================

def process_xml(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(
            r"<runtimeEnvironmentId>.*?</runtimeEnvironmentId>",
            f"<runtimeEnvironmentId>{QA_ID}</runtimeEnvironmentId>",
            content
        )

        content = re.sub(
            r"<runtimeEnvironmentName>.*?</runtimeEnvironmentName>",
            f"<runtimeEnvironmentName>{QA_NAME}</runtimeEnvironmentName>",
            content
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[XML] Updated: {file_path}")

    except Exception as e:
        print(f"[XML] Skipped (error): {file_path} -> {e}")


# =========================
# ZIP PROCESSING
# =========================

def process_zip(file_path):
    print(f"[ZIP] Processing: {file_path}")

    temp_dir = tempfile.mkdtemp()

    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Procesar contenido interno
        for root, _, files in os.walk(temp_dir):
            for file in files:
                full_path = os.path.join(root, file)

                if file.endswith(".json"):
                    process_json(full_path)
                elif file.endswith(".xml"):
                    process_xml(full_path)

        # Reempaquetar
        new_zip_path = file_path + ".tmp"

        with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, temp_dir)
                    zip_out.write(full_path, arcname)

        shutil.move(new_zip_path, file_path)

        print(f"[ZIP] Repacked: {file_path}")

    finally:
        shutil.rmtree(temp_dir)


# =========================
# MAIN
# =========================

def main():
    changed_files = os.environ.get("CHANGED_FILES", "").split()

    if not changed_files:
        print("No changed files found")
        return

    for file in changed_files:
        if not os.path.isfile(file):
            continue

        if file.endswith(".json"):
            process_json(file)

        elif file.endswith(".xml"):
            process_xml(file)

        elif file.endswith(".zip"):
            process_zip(file)


if __name__ == "__main__":
    main()
