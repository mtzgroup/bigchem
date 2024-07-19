import subprocess
import sys
from datetime import datetime

import toml


def get_repo_url():
    """Get the repository URL from pyproject.toml or ask the user for it."""
    try:
        with open("pyproject.toml", "r") as file:
            pyproject = toml.load(file)
        repo_url = pyproject["tool"]["poetry"]["repository"]
        return repo_url
    except KeyError:
        return input("Enter the repository URL (e.g., https://github.com/user/repo): ")


def update_version_with_poetry(version):
    """Update the version in pyproject.toml using Poetry."""
    print("Updating version in pyproject.toml...")
    subprocess.run(["poetry", "version", version], check=True)


def update_changelog(version, repo_url):
    """Update the CHANGELOG.md file with the new version and today's date."""
    print("Updating CHANGELOG.md...")
    with open("CHANGELOG.md", "r") as file:
        lines = file.readlines()

    today = datetime.today().strftime("%Y-%m-%d")
    new_entry = f"\n## [{version}] - {today}\n"

    # Insert the new entry after the ## [unreleased] section
    for i, line in enumerate(lines):
        if line.startswith("## [unreleased]"):
            lines.insert(i + 1, new_entry)
            break

    # Update links at the bottom
    unreleased_link = f"[unreleased]: {repo_url}/compare/{version}...HEAD\n"
    new_version_link = f"[{version}]: {repo_url}/releases/tag/{version}\n"

    # Ensure the new version link is added right after the [unreleased] link
    for i, line in enumerate(lines):
        if line.startswith("[unreleased]:"):
            lines[i] = unreleased_link
            lines.insert(i + 1, new_version_link)
            break

    with open("CHANGELOG.md", "w") as file:
        file.writelines(lines)


def run_git_commands(version):
    """Run the git commands to commit the changes, create a new tag, and push."""
    print("Running git commands...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"Bumped version to {version}. Updated CHANGELOG."],
        check=True,
    )
    subprocess.run(["git", "tag", version], check=True)
    subprocess.run(["git", "push", "--tags"], check=True)
    subprocess.run(["git", "push"], check=True)


def confirm_version(version: str):
    """Ask the user to confirm the version number before proceeding."""
    while True:
        response = (
            input(f"Are you sure you want to release {version}? (Y/N): ")
            .strip()
            .lower()
        )
        if response in ["y", "n"]:
            return response == "y"
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")


def main():
    """Main entry point for the script."""
    from pathlib import Path

    if len(sys.argv) != 2:
        print("Usage: release.py <version>")
        sys.exit(1)

    version = sys.argv[1]

    original_pyproject = Path("pyproject.toml").read_text()
    original_changelog = Path("CHANGELOG.md").read_text()

    repo_url = get_repo_url()
    update_version_with_poetry(version)
    update_changelog(version, repo_url)
    if confirm_version(version):
        print("Proceeding with the release...")
    else:
        print("Reverting changes...")
        Path("pyproject.toml").write_text(original_pyproject)
        Path("CHANGELOG.md").write_text(original_changelog)
        sys.exit(1)
    run_git_commands(version)


if __name__ == "__main__":
    main()
