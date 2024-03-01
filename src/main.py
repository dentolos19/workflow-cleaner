import time
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List

from art import text2art
from colorama import Fore, just_fix_windows_console
from github import Auth, Github
from github.Repository import Repository
from github.WorkflowRun import WorkflowRun
from utils import clear_previous_lines, color_combo_repo

ACCESS_TOKEN_FILE = Path(".accesstoken")


def main():
    parser = ArgumentParser()
    parser.add_argument("-m", "--mine-only", action="store_true")
    parser.add_argument("-d", "--dry-run", action="store_true")
    args = parser.parse_args()
    args_mine_only = args.mine_only
    args_dry_run = args.dry_run

    just_fix_windows_console()
    print(text2art("Workflow Cleaner", font="small"))
    print("Your current options:")
    print("- Mine Only:", f"{Fore.GREEN}On{Fore.RESET}" if args_mine_only else f"{Fore.RED}No{Fore.RESET}")
    print("- Dry Run:", f"{Fore.GREEN}On{Fore.RESET}" if args_dry_run else f"{Fore.RED}No{Fore.RESET}")
    print()

    access_token = get_access_token()

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
        set_access_token(access_token)

    github = Github(auth=Auth.Token(access_token))

    print()
    runs = analyze(github, mine_only=args_mine_only)
    print()
    if runs:
        input(f"Press {Fore.GREEN}[Enter]{Fore.RESET} to delete the old workflow runs...")
        print()
        delete(runs)
        print()
    input(f"Press {Fore.GREEN}[Enter]{Fore.RESET} to exit...")
    quit()


def analyze(github: Github, mine_only: bool = False):
    print("Analyzing your repositories...")
    user = github.get_user()
    repos = user.get_repos()
    target_runs: Dict[Repository, List[WorkflowRun]] = {}
    for repo in repos:
        if mine_only and not repo.owner.login == user.login:
            continue
        clear_previous_lines()
        print(f"Analyzing: {color_combo_repo(repo.owner.login, repo.name)}")
        runs = repo.get_workflow_runs()
        if not runs.totalCount > 0:
            continue
        workflows = repo.get_workflows()
        for run in runs:
            if not any(run.workflow_id == workflow.id for workflow in workflows):
                if repo.name not in target_runs:
                    target_runs[repo] = []
                target_runs[repo].append(run)
    clear_previous_lines(1)
    print("Analysis complete! ", end="")
    if not target_runs:
        print("No old workflow runs found!")
        return {}
    print("Here are the repositories with old workflows runs to delete:")
    for repo, runs in target_runs.items():
        print(
            f"- {color_combo_repo(repo.owner.login, repo.name)}: {Fore.RED}{len(runs)}{Fore.RESET} runs to delete!"
        )
    return target_runs


def delete(runs: Dict[Repository, List[WorkflowRun]], dry_run: bool = False):
    print("Deleting...")
    for repo, runs in runs.items():
        deleted_count = 0
        for run in runs:
            clear_previous_lines()
            if dry_run:
                # run.delete() # TODO: uncomment this line
                pass
            else:
                time.sleep(1)
            print(
                f"Deleted {Fore.RED}{deleted_count}{Fore.RESET} runs from {color_combo_repo(repo.owner.login, repo.name)}..."
            )
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
    main()