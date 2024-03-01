from colorama import Fore


def clear_previous_lines(lines: int = 1):
    LINE_UP = "\x1b[1A"
    LINE_CLEAR = "\x1b[2K"
    for i in range(lines):
        print(LINE_UP, end=LINE_CLEAR)


def color_combo_repo(owner_login: str, repo_name: str):
    return (
        f"{Fore.MAGENTA}{owner_login}{Fore.RESET}"
        + "/"
        + f"{Fore.BLUE}{repo_name}{Fore.RESET}"
    )