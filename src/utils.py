import requests


def delete_workflow_run(username: str, repo_name: str, run_id: int, access_token: str):
    requests.delete(
        f"https://api.github.com/repos/{username}/{repo_name}/actions/runs/{run_id}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {access_token}",
        },
    )