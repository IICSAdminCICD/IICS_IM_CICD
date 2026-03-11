import requests
import os

URL = os.environ['IICS_LOGIN_URL']
DEV_USERNAME = os.environ['DEV_IICS_USERNAME']
DEV_PASSWORD = os.environ['DEV_IICS_PASSWORD']

QA_USERNAME = os.environ['QA_IICS_USERNAME']
QA_PASSWORD = os.environ['QA_IICS_PASSWORD']

BODY = {"username": DEV_USERNAME, "password": DEV_PASSWORD}

r = requests.post(url=URL, json=BODY)

if r.status_code != 200:
    raise Exception("Login DEV failed: " + r.text)

QA_BODY = {"username": QA_USERNAME, "password": QA_PASSWORD}

u = requests.post(url=URL, json=QA_BODY)

if u.status_code != 200:
    raise Exception("Login QA failed: " + u.text)

data = r.json()
qa_data = u.json()

sessionId = data['userInfo']['sessionId']
qa_sessionId = qa_data['userInfo']['sessionId']

print("DEV session obtained")
print("QA session obtained")

print(f"##vso[task.setvariable variable=sessionId;isOutput=true]{sessionId}")
print(f"##vso[task.setvariable variable=qa_sessionId;isOutput=true]{qa_sessionId}")
