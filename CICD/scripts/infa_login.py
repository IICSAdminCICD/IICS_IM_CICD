import requests
import os

URL = os.environ['IICS_LOGIN_URL']

QA_USERNAME = os.environ['QA_IICS_USERNAME']
QA_PASSWORD = os.environ['QA_IICS_PASSWORD']

QA_BODY = {"username": QA_USERNAME, "password": QA_PASSWORD}

u = requests.post(url=URL, json=QA_BODY)

if u.status_code != 200:
    raise Exception("Login QA failed: " + u.text)

qa_data = u.json()

qa_sessionId = qa_data['userInfo']['sessionId']

print("QA session obtained")

print(f"##vso[task.setvariable variable=qa_sessionId;isOutput=true]{qa_sessionId}")
