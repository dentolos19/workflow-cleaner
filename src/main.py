import time
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List

from art import text2art
from colorama import Fore, just_fix_windows_console
from github import Auth, Github
from github.WorkflowRun import WorkflowRun

from utils import clear_previous_lines

ACCESS_TOKEN_FILE = Path(".accesstoken")


def init():
    parser = ArgumentParser()
    parser.add_argument("-p", "--personal", action="store_true")
    parser.add_argument("-t", "--test", action="store_true")
    args = parser.parse_args()
    main(
        personal=args.personal,
        test=args.test,
    )


def main(personal: bool, test: bool):
    just_fix_windows_console()
    print(text2art("Workflow Cleaner", font="small"))

    access_token = get_access_token()
    if access_token:
        print("Your access token is already saved!")
        print()
        print("If you want to change your access token, delete ")
        print(f"the file {Fore.YELLOW}{ACCESS_TOKEN_FILE}{Fore.RESET} and run this program again.")
        print()
        input(f"Press {Fore.CYAN}[Enter]{Fore.RESET} to continue...")
    else:
        print("Make sure your access token has access to all the")
        print("repositories with read-write access to actions and read access to contents.")
        print()
        access_token = input("Access Token: ")
        set_access_token(access_token)

    github = Github(auth=Auth.Token(access_token))

    print()
    runs = analyze(github, personal=personal)
    print()

    if runs:
        input(f"Press {Fore.CYAN}[Enter]{Fore.RESET} to delete the old workflow runs...")
        print()
        delete(runs, test=test)
        print()

    input(f"Press {Fore.CYAN}[Enter]{Fore.RESET} to exit...")
    quit()


def analyze(github: Github, personal: bool = False):
    print("Analyzing your repositories...")

    user = github.get_user()
    repos = user.get_repos()
    target_runs: Dict[str, List[WorkflowRun]] = {}

    for repo in repos:
        # Skip archived repositories
        if repo.archived:
            continue

        # Skip repositories that are not owned by the user
        if personal and not repo.owner.login == user.login:
            continue

        clear_previous_lines()
        print(f"Analyzing: {repo.full_name}")

        workflow_runs = repo.get_workflow_runs()

        # Skip repositories with no workflow runs
        if not workflow_runs.totalCount > 0:
            continue

        # Get all workflow files in the repository
        workflows = repo.get_workflows()

        # Build a map of workflow IDs to their file paths
        workflow_paths = {}
        for workflow in workflows:
            workflow_paths[workflow.id] = workflow.path

        # Check each workflow run to see if its workflow file still exists
        for run in workflow_runs:
            should_delete = False

            # Check if workflow ID is not in the list of active workflows
            if run.workflow_id not in workflow_paths:
                should_delete = True
            else:
                # Even if the workflow ID exists, check if the actual file exists
                try:
                    repo.get_contents(run.path)
                except Exception as e:
                    # Only delete if we get a 404 (file not found), not 403 (forbidden)
                    if hasattr(e, "status") and e.status == 404:
                        should_delete = True

            if should_delete:
                if repo.full_name not in target_runs:
                    target_runs[repo.full_name] = []
                target_runs[repo.full_name].append(run)

    clear_previous_lines()
    print("Analysis complete! ", end="")

    if not target_runs:
        print("No old workflow runs found!")
        return target_runs

    print("Here are the repositories with old workflows runs to delete:")

    for repo, workflow_runs in target_runs.items():
        print(f"- {repo}: {len(workflow_runs)} runs to delete!")

    return target_runs


def delete(target_runs: Dict[str, List[WorkflowRun]], test: bool = False):
    print("Deleting...")

    for repo, runs in target_runs.items():
        deleted_count = 1
        for run in runs:
            clear_previous_lines()
            if test:
                time.sleep(1)
            else:
                run.delete()
            print(f"Deleted {Fore.RED}{deleted_count}{Fore.RESET} runs from {repo}...")
            deleted_count += 1

    clear_previous_lines()
    print("Deleted all old workflow runs!")


def get_access_token():
    if ACCESS_TOKEN_FILE.exists():
        return ACCESS_TOKEN_FILE.read_text().strip()
    return None


def set_access_token(access_token: str):
    ACCESS_TOKEN_FILE.write_text(access_token)


if __name__ == "__main__":
    init()