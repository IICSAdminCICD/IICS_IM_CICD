import requests
import os

session_id = os.environ['IICS_SESSION_ID']
pod_url = os.environ['IICS_POD_URL']
zip_path = os.environ['ZIP_FILE']

url = f"{pod_url}/public/core/v3/import/package"

headers = {
    "INFA-SESSION-ID": session_id
}

files = {
    "package": open(zip_path, "rb")
}

response = requests.post(url, headers=headers, files=files)

if response.status_code != 200:
    raise Exception(f"Upload failed: {response.text}")

print("ZIP uploaded successfully to IICS")
