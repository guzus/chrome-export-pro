import subprocess

from os.path import expanduser
from platform import system
import time


def export_chrome_bookmarks(storage_path, name):
    print(f"\nExporting bookmarks for {name}...")

    profiles = subprocess.check_output(["ls", storage_path]).decode("utf-8").split("\n")

    for profile in profiles:
        bookmark_files = (
            subprocess.check_output(["ls", storage_path + "/" + profile])
            .decode("utf-8")
            .split("\n")
        )
        if "Bookmarks" not in bookmark_files:
            continue

        profile_path = f"{storage_path}/{profile}/Bookmarks"
        datetime = time.strftime("%Y-%m-%d-%H-%M-%S")
        output_file = f"output/{name}-{profile}-bookmarks-{datetime}.html"
        subprocess.call(
            ["python", "export-chrome-bookmarks", profile_path, output_file]
        )
        print("Exported bookmarks for profile: " + profile)


if __name__ == "__main__":
    # create output directory if it doesn't exist
    subprocess.call(["mkdir", "-p", "output"])

    if system() == "Linux":
        export_chrome_bookmarks(expanduser("~/.config/google-chrome"), "chrome")
        export_chrome_bookmarks(
            expanduser("~/.config/BraveSoftware/Brave-Browser"), "brave"
        )
    elif system() == "Darwin":
        export_chrome_bookmarks(
            expanduser("~/Library/Application Support/Google/Chrome"), "chrome"
        )
        export_chrome_bookmarks(
            expanduser("~/Library/Application Support/BraveSoftware/Brave-Browser"),
            "brave",
        )
