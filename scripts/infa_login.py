import requests
import os

URL = os.environ['IICS_LOGIN_URL']
USERNAME = os.environ['IICS_USERNAME']
PASSWORD = os.environ['IICS_PASSWORD']

UAT_USERNAME = os.environ['UAT_IICS_USERNAME']
UAT_PASSWORD = os.environ['UAT_IICS_PASSWORD']

BODY = {"username": USERNAME, "password": PASSWORD}

r = requests.post(url=URL, json=BODY)

if r.status_code != 200:
    raise Exception("Login DEV failed: " + r.text)

UAT_BODY = {"username": UAT_USERNAME, "password": UAT_PASSWORD}

u = requests.post(url=URL, json=UAT_BODY)

if u.status_code != 200:
    raise Exception("Login UAT failed: " + u.text)

data = r.json()
uat_data = u.json()

sessionId = data['userInfo']['sessionId']
uat_sessionId = uat_data['userInfo']['sessionId']

print("DEV session obtained")
print("UAT session obtained")

# Export variables to Azure DevOps pipeline
print(f"##vso[task.setvariable variable=sessionId]{sessionId}")
print(f"##vso[task.setvariable variable=uat_sessionId]{uat_sessionId}")
