import os
import re
import time, copy
from termcolor import colored
import keyboard, threading, sys


class Utils:
    def new_line(num: int = 1) -> str:
        if num <= 0:
            return ""
        return "\n" * num

    def clear_screen() -> None:
        # Clear the terminal screen using ANSI escape code
        os.system("cls" if os.name == "nt" else "clear")

    def task_print(text: str, lenby: str = "") -> None:
        width: int = os.get_terminal_size().columns
        mid_text: str = f" {text} "
        mid_len_text: str = f" {lenby} "
        side_width: int = int((width - len(mid_text)) / 2)
        if lenby:
            side_width = int((width - len(f" {lenby} ")) / 2)

        sep_text = "─" * side_width
        print(Utils.new_line(5))
        print(f"{sep_text}{mid_text}{sep_text}")
        print(Utils.new_line())

    def bold(text: str) -> str:
        return "\033[1m" + text + "\033[0m"


root_folder = ""

old_info = ""
old_version = ""
with open(f"pyproject.toml", "r") as f:
    old_info = f.read()


def revert():
    with open(f"pyproject.toml", "w") as wf:
        wf.write(old_info)


def get_version() -> str:
    global old_version
    with open(f"pyproject.toml", "r") as rf:
        content = rf.read()
        content_list: list[str] = content.split('version = "')

        old_version = content_list[1][:5]
        return old_version


def __update_version(update_type: 0 or 1 or 2):
    current = get_version()
    __new_version = [int(current[0]), int(current[2]), int(current[4])]

    __new_version[abs(-2 + update_type)] += 1
    new_version = []

    if update_type == 0:
        pass

    elif update_type == 1:
        __new_version[2] = 0

    elif update_type == 2:
        __new_version[2] = 0
        __new_version[1] = 0

    new_version = [str(x) for x in __new_version]

    global old_info

    with open(os.path.join(root_folder, f"pyproject.toml"), "r+") as file:
        old_info = copy.copy(file.read())
        file.seek(0)
        version_replaced: str = file.read().replace(
            f'version = "{current}"', 'version = "' + ".".join(new_version) + '"'
        )
        file.seek(0)
        file.write(version_replaced)

    return ".".join(new_version)


def move_cursor_up(lines):
    sys.stdout.write(f"\033[{lines}A")


can_press: bool = True


def select_from_range(nums_dict: dict[int, str]):
    def key_timeout_daemon(_time):
        global can_press
        if not can_press:
            return

        def inner():
            global can_press
            can_press = False
            time.sleep(_time)
            can_press = True

        x = threading.Thread(target=inner)
        x.daemon = True
        x.start()

    current = 0
    l_c = -2

    keyslist = list(nums_dict.keys())

    def do_print():
        for i in range(len(keyslist)):
            if current == i:
                print(colored(f"> {nums_dict[keyslist[current]]}", attrs=["bold"]))
                continue
            print(colored(f"  {nums_dict[keyslist[i]]}", attrs=["dark"]))

    do_print()

    while not keyboard.is_pressed("Enter"):
        if not can_press:
            continue

        if keyboard.is_pressed("up_arrow"):
            current -= 1
            key_timeout_daemon(0.15)
        if keyboard.is_pressed("down_arrow"):
            current += 1
            key_timeout_daemon(0.15)

        prev = current - 1
        next = current + 1
        if current == -1:
            current = len(nums_dict) - 1
        if current == len(nums_dict):
            current = 0

        if current == l_c:
            continue

        l_c = current
        move_cursor_up(len(keyslist))

        do_print()

    move_cursor_up(len(keyslist))
    for i in range(len(keyslist)):
        print("                             ")
    move_cursor_up(len(keyslist))

    print(f"✔ {nums_dict[keyslist[current]]}")

    # Only here to eat all the other chars the user typed
    x = input("\033[8m")
    print("\033[0m", end="")

    return keyslist[current]


def main():
    try:
        os.system("cls" if os.name == "nt" else "clear")

        new_v: str = ""
        publish_to_pypi: bool = False
        pypi_test: bool = True

        Utils.task_print("Publish New Version")

        get_version()

        print(f"{colored('Updating Version', attrs=['bold'])} | Current: {old_version}")

        UT_dict = {0: "Patch", 1: "Minor", 2: "Major", 3: "Amend", 4: "Chore"}
        print(colored("\nSelect update type", attrs=["dark"]))
        update_type: int = select_from_range(UT_dict)

        option_dict = {3: "Corrected", 4: "Chore"}

        if update_type <= 2 and update_type >= 0:
            new_v = __update_version(update_type)
            print(
                f"\nVersison updated: {old_version} ⟹  {colored(str(new_v), attrs=['bold'])}"
            )
            time.sleep(0.4)

            cf = input("\n\nPublish to PyPi? [y/n]\n> ")
            if cf.lower() in ["y", "yes"]:
                publish_to_pypi = True
                move_cursor_up(2)
                print(colored("Publish to PyPi? [y/n]", attrs=["dark"]))
                print(f"✔ Publishing to PyPi\n")

            if publish_to_pypi:
                print("Publish to PyPi Test Branch? [y/n]")
                print(colored('"yes" by default', attrs=["dark"]))
                cf2 = input("> ")
                move_cursor_up(3)
                print(colored("Publish to PyPi Test Branch? [y/n]", attrs=["dark"]))
                if cf2.lower() in ["n", "no"]:
                    pypi_test = False
                    print(
                        f"✔ Publishing to PyPi {colored('LIVE BRANCH', attrs=['bold'])}"
                    )
                else:
                    print(
                        f"✔ Publishing to PyPi Test Branch"
                    )
                print("                 ")


        elif update_type <= 4 and update_type >= 3:
            new_v = option_dict[update_type]
        else:
            raise ValueError

        print(f"\n\n{colored('Setting Commit Message', attrs=['bold'])} / Title\n")
        print(colored("Set commit title", attrs=["dark"]))
        commit_title: str = input("> ")
        if commit_title == "":
            raise ValueError
        print(f"\nCommit title set to: {commit_title}")
        time.sleep(0.4)

        print(
            f"\n\n\n{colored('Setting Commit Message', attrs=['bold'])} / Description\n"
        )
        print(colored("Set commit description", attrs=["dark"]))
        commit_description: str = input(f"> ")
        print(f"\nCommit description set to: {commit_description}")
        time.sleep(0.4)

        amend_text = ""
        if update_type == 3:
            amend_text = " --amend"

        Utils.task_print("Confirm Commit Settings")

        print(f"{colored('Commit title:', attrs=['dark'])}\n\"{commit_title}\"")
        print(
            f"\n{colored('Commit description:', attrs=['dark'])}\n\"{commit_description}\""
        )
        if new_v != "":
            print(f"\n{colored('New commit version/type:', attrs=['dark'])}\n{new_v}")

        confirm = input("\n\nPublish commit? [y/n]\n> ")
        if confirm.lower() not in ["y", "yes"]:
            print("\n\n\033[1mCommit Aborted\033[0m\n\n\n")
            revert()
            return

        Utils.task_print("Pushing to Github")

        print(colored("> git add .", attrs=["dark"]))
        os.system("git add .")
        print(
            colored(
                f'> git commit{amend_text} -m "{new_v} | {commit_title}" -m "{commit_description}"',
                attrs=["dark"],
            )
        )
        os.system(
            f'git commit{amend_text} -m "{new_v} | {commit_title}" -m "{commit_description}"'
        )
        print(colored("> git push", attrs=["dark"]))
        try:
            os.system("git push")
        except:
            print("Failed to push to current branch")

        if not publish_to_pypi:
            return

        Utils.task_print("Pushing to PyPi")

        print(colored("> python -m build", attrs=["dark"]))
        os.system("python -m build")

        if pypi_test:
            print(colored("> python -m twine upload --verbose --repository testpypi dist/*", attrs=["dark"]))
            os.system("python -m twine upload --verbose --repository testpypi dist/*")
        else:
            print(colored("> python -m twine upload --verbose dist/*", attrs=["dark"]))
            os.system("python -m twine upload --verbose dist/*")
        




    except ValueError:
        revert()
        print("\nIncorrect input :(")
    except KeyboardInterrupt:
        revert()
        print("\nWorkflow stopped by KeyboardInterrupt")


if __name__ == "__main__":
    main()
