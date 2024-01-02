from os import path

import requests
from colorama import Fore
from github import Github

ACCESS_TOKEN_FILE = ".access_token"

################################################################################

access_token = ""

if path.exists(ACCESS_TOKEN_FILE):
    with open(ACCESS_TOKEN_FILE, "r") as file:
        access_token = file.read()

print("Workflow Cleaner")
print()
if access_token:
    print("Your access token is already saved.")
    print()
    print("If you want to change your access token, delete ")
    print(f"the file {ACCESS_TOKEN_FILE} and run this program again.")
    print()
    input("Press [Enter] to continue...")
else:
    print("Make sure your access token has access to all the")
    print("repositories with read-write access to actions.")
    print()
    access_token = input("Access Token: ")
    with open(ACCESS_TOKEN_FILE, "w") as file:
        file.write(access_token)

################################################################################

print()
print("Looking into your repositories...")
print()

user = Github(access_token).get_user()
repos = user.get_repos()
target_runs = []

for repo in repos:
    if repo.owner.login != user.login:
        continue  # ignores repositories that is not owned by the user
    workflows = repo.get_workflows()
    runs = repo.get_workflow_runs()
    if (not workflows.totalCount > 0) or (not runs.totalCount > 0):
        continue  # ignores repositories that has no workflows or workflow runs
    print(repo.name)
    if workflows.totalCount > 0:
        print("  workflows")
        for workflow in workflows:
            print(f"    - {workflow.name} ({workflow.id})")
    if runs.totalCount > 0:
        print("  runs")
        for run in runs:
            foreground = Fore.GREEN
            if not any(
                run.workflow_id == workflow.id for workflow in workflows
            ):  # checks if the workflow of the run is still available
                target_runs.append(run)
                foreground = Fore.RED
            print(
                foreground
                + f"    - {run.run_number}: {run.head_commit.message} ({run.id})"
                + Fore.RESET
            )

print()
input("Press [Enter] to delete the (red-colored) workflow runs...")
print()

for run in target_runs:
    print(
        f"Deleting: {run.head_repository.name} // {run.id} // {run.head_commit.message} ({run.run_number})"
    )
    requests.delete(
        f"https://api.github.com/repos/{user.login}/{run.head_repository.name}/actions/runs/{run.id}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {access_token}",
        },
    )