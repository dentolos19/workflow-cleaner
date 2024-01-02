import requests
from colorama import Fore  # pip install colorama
from github import Github  # pip install PyGithub

ACCESS_TOKEN = "<ACCESS_TOKEN>"

client = Github(ACCESS_TOKEN)

user = client.get_user()

print("Looking into your repositories...")
print()

repos = user.get_repos()

target_runs = []

for repo in repos:
    if repo.owner.login != user.login:
        continue  # ignores repositories that is not owned by the user
    workflows = repo.get_workflows()
    runs = repo.get_workflow_runs()
    if (not workflows.totalCount > 0) and (not runs.totalCount > 0):
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
input("Press any key to delete the (red-colored) workflow runs...")
print()

for run in target_runs:  # deletes the workflow runs of deleted workflows
    print(
        f"Deleting: {run.head_repository.name} // {run.id} // {run.head_commit.message} ({run.run_number})"
    )
    requests.delete(
        f"https://api.github.com/repos/{user.login}/{run.head_repository.name}/actions/runs/{run.id}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"token {ACCESS_TOKEN}",
        },
    )