import os
import requests
import time
import sys
import json

session_id = os.getenv("IICS_SESSION_ID")
pod_url = os.getenv("IICS_POD_URL")
commit_hash = os.getenv("COMMIT_HASH")

if not all([session_id, pod_url, commit_hash]):
    print("❌ Faltan variables necesarias")
    sys.exit(1)

headers = {
    "Content-Type": "application/json",
    "INFA-SESSION-ID": session_id
}

# ------------------------
# 1. LANZAR PULL
# ------------------------

pull_url = f"{pod_url}/saas/public/core/v3/pullByCommitHash"

payload = {
    "commitHash": commit_hash
}

print("====================================")
print("🚀 INICIO PULL BY COMMIT")
print("Commit:", commit_hash)
print("URL:", pull_url)
print("Session_ID:", session_id)
print("====================================")

try:
    response = requests.post(pull_url, json=payload, headers=headers)
except Exception as e:
    print("❌ Error de conexión al lanzar el pull:")
    print(str(e))
    sys.exit(1)

if response.status_code != 200:
    print("❌ Error en Pull (HTTP):", response.status_code)
    print("Respuesta completa:")
    print(response.text)
    sys.exit(1)

try:
    data = response.json()
except Exception:
    print("❌ No se pudo parsear la respuesta JSON")
    print(response.text)
    sys.exit(1)

print("📦 Respuesta del Pull:")
print(json.dumps(data, indent=2))

action_id = data.get("actionId") or data.get("id")

if not action_id:
    print("❌ No se recibió actionId en la respuesta")
    sys.exit(1)

print(f"✅ Pull lanzado correctamente. Action ID: {action_id}")

# ------------------------
# 2. POLLING STATUS
# ------------------------

status_url = f"{pod_url}/public/core/v3/activity/logs/{action_id}"

MAX_RETRIES = 30
BASE_SLEEP = 5  # segundos

print("====================================")
print("⏳ INICIO MONITOREO")
print("====================================")

for attempt in range(MAX_RETRIES):
    try:
        response = requests.get(status_url, headers=headers)
    except Exception as e:
        print("❌ Error de conexión al consultar status:")
        print(str(e))
        sys.exit(1)

    if response.status_code != 200:
        print("❌ Error consultando status (HTTP):", response.status_code)
        print("Respuesta completa:")
        print(response.text)
        sys.exit(1)

    try:
        data = response.json()
    except Exception:
        print("❌ Error parseando JSON de status")
        print(response.text)
        sys.exit(1)

    status = data.get("status") or data.get("state") or "UNKNOWN"

    print("------------------------------------")
    print(f"🔁 Intento {attempt + 1}/{MAX_RETRIES}")
    print("Status:", status)

    # Logging extendido útil
    if "message" in data:
        print("Mensaje:", data["message"])

    if "details" in data:
        print("Detalles:", data["details"])

    print("------------------------------------")

    if status.upper() in ["SUCCESS", "SUCCEEDED", "COMPLETED"]:
        print("✅ Pull completado correctamente")
        sys.exit(0)

    if status.upper() in ["FAILED", "ERROR"]:
        print("❌ Pull falló")
        print("Respuesta final completa:")
        print(json.dumps(data, indent=2))
        sys.exit(1)

    # 🔥 Backoff progresivo (máx 60s)
    sleep_time = min(60, BASE_SLEEP * (attempt + 1))

    print(f"⏱ Esperando {sleep_time} segundos antes del siguiente intento...\n")
    time.sleep(sleep_time)

print("❌ Timeout esperando finalización del Pull")
sys.exit(1)
