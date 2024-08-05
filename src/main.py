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
        print(
            f"the file {Fore.YELLOW}{ACCESS_TOKEN_FILE}{Fore.RESET} and run this program again."
        )
        print()
        input(f"Press {Fore.CYAN}[Enter]{Fore.RESET} to continue...")
    else:
        print("Make sure your access token has access to all the")
        print("repositories with read-write access to actions.")
        print()
        access_token = input("Access Token: ")
        set_access_token(access_token)

    github = Github(auth=Auth.Token(access_token))

    print()
    runs = analyze(github, personal=personal)
    print()

    if runs:
        input(
            f"Press {Fore.CYAN}[Enter]{Fore.RESET} to delete the old workflow runs..."
        )
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

        runs = repo.get_workflow_runs()

        # Skip repositories with no workflow runs
        if not runs.totalCount > 0:
            continue

        workflows = repo.get_workflows()
        for run in runs:
            if not any(run.workflow_id == workflow.id for workflow in workflows):
                if repo.full_name not in target_runs:
                    target_runs[repo.full_name] = []
                target_runs[repo.full_name].append(run)

    clear_previous_lines()
    print("Analysis complete! ", end="")

    if not target_runs:
        print("No old workflow runs found!")
        return target_runs
    print("Here are the repositories with old workflows runs to delete:")
    for repo, runs in target_runs.items():
        print(f"- {repo}: {len(runs)} runs to delete!")
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
                pass
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