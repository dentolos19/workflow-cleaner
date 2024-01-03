from os import path

from art import *
from colorama import Fore, just_fix_windows_console
from github import Github
from github.PaginatedList import PaginatedList
from github.WorkflowRun import WorkflowRun

from utils import delete_workflow_run

ACCESS_TOKEN_FILE = ".access_token"

################################################################################

access_token = ""

if path.exists(ACCESS_TOKEN_FILE):
    with open(ACCESS_TOKEN_FILE, "r") as file:
        access_token = file.read()

just_fix_windows_console()

print(text2art("Workflow Cleaner", font="small"))

if access_token:
    print("Your access token is already saved!")
    print()
    print("If you want to change your access token, delete ")
    print(
        f"the file {Fore.YELLOW}{ACCESS_TOKEN_FILE}{Fore.RESET} and run this program again."
    )
    print()
    input(f"Press {Fore.GREEN}[Enter]{Fore.RESET} to continue...")
else:
    print("Make sure your access token has access to all the")
    print("repositories with read-write access to actions.")
    print()
    access_token = input("Access Token: ")

################################################################################

client = Github(access_token)
user = client.get_user()
repos = user.get_repos()

# checks if the access token is valid
try:
    _ = user.name
except:
    print()
    print("You have an invalid access token! Please")
    print(f"delete {Fore.YELLOW}{ACCESS_TOKEN_FILE}{Fore.RESET} and try again.")
    print()
    input(f"Press {Fore.GREEN}[Enter]{Fore.RESET} to exit...")
    quit()

if not path.exists(ACCESS_TOKEN_FILE):
    with open(ACCESS_TOKEN_FILE, "w") as file:
        file.write(access_token)

print()
print("Looking into your repositories...")
print()

target_runs: PaginatedList[WorkflowRun] = []

for repo in repos:
    # ignores repositories that is not owned by the user
    if repo.owner.login != user.login:
        continue

    workflows = repo.get_workflows()
    runs = repo.get_workflow_runs()

    # TODO: check if actions read-write access is enabled

    # ignores repositories that has no workflows or workflow runs
    if (not workflows.totalCount > 0) or (not runs.totalCount > 0):
        continue

    new_target_runs: PaginatedList[WorkflowRun] = []

    for run in runs:
        # checks if the run's workflow is in the list of workflows of the repo
        if not any(run.workflow_id == workflow.id for workflow in workflows):
            new_target_runs.append(run)

    target_runs.extend(new_target_runs)

    # ignores repositories that has no workflow runs to delete
    if len(new_target_runs) > 0:
        print(
            f"{Fore.YELLOW}{repo.name}{Fore.RESET} has {Fore.RED}{len(new_target_runs)}{Fore.RESET} old workflow runs!"
        )
        for run in new_target_runs:
            print(f"  - {run.name} ({run.id})")

client.close()

if len(target_runs) > 0:
    print()
    input(f"Press {Fore.GREEN}[Enter]{Fore.RESET} to delete the old workflow runs...")
    print()

    print("Deleting old workflow runs...")
    for run in target_runs:
        delete_workflow_run(user.login, run.head_repository.name, run.id, access_token)

    print("Done!")
else:
    print("You have no old workflow runs to delete!")

print()
input(f"Press {Fore.GREEN}[Enter]{Fore.RESET} to exit...")
quit()