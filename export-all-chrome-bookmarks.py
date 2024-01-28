import subprocess

from os.path import expanduser
from platform import system


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

        profile_path = storage_path + "/" + profile + "/Bookmarks"
        output_file = "output/" + name + "-" + profile + "-bookmarks.html"
        subprocess.call(
            ["python", "export-chrome-bookmarks", profile_path, output_file]
        )
        print("Exported bookmarks for profile: " + profile)


if __name__ == "__main__":
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
