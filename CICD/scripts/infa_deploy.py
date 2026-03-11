import requests
from infa_login import InfaLogin


class InfaDeploy:

    def __init__(self, username, password, pod_url, repository_id):
        self.login_client = InfaLogin(username, password, pod_url)
        self.repository_id = repository_id
        self.pod_url = pod_url

    def deploy_by_commit(self, commit_hash):

        session_id = self.login_client.login()

        url = f"{self.pod_url}/public/core/v3/git/pullByCommitHash"

        headers = {
            "Content-Type": "application/json",
            "INFA-SESSION-ID": session_id
        }

        payload = {
            "commitHash": commit_hash,
            "repositoryId": self.repository_id
        }

        response = requests.post(url, json=payload, headers=headers)

        response.raise_for_status()

        print("Deploy ejecutado correctamente")
        print(response.json())