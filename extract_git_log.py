import git
import os
import csv
from git import Repo
from collections import defaultdict
from tqdm import tqdm
from extract_comments import (
    extract_python_comments,
    extract_cpp_comments,
    extract_fortran_comments,
)

file_comments = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
error_details = []


# Function to checkout all versions of a file and save to CSV
def checkout_file_versions(repo, repo_dir, relative_file_path, files_type):
    # Construct the absolute file path
    absolute_file_path = os.path.join(repo_dir, relative_file_path)

    try:
        for commit in reversed(list(repo.iter_commits(paths=relative_file_path))):
            # Checkout using the relative file path
            repo.git.checkout(commit.hexsha, relative_file_path)

            current_comments = (
                set(extract_python_comments(absolute_file_path))
                if files_type == "python"
                else (
                    set(extract_cpp_comments(absolute_file_path))
                    if files_type == "cpp"
                    else (
                        set(extract_fortran_comments(absolute_file_path))
                        if files_type == "fortran"
                        else set()
                    )
                )
            )

            previous_comments = file_comments[absolute_file_path].get(
                "current_comments", set()
            )

            # Find newly introduced comments
            introduced = current_comments - previous_comments
            for comment in introduced:
                file_comments[absolute_file_path][comment][
                    "introduced"
                ] = commit.committed_datetime

            # Find removed comments
            removed = previous_comments - current_comments
            for comment in removed:
                file_comments[absolute_file_path][comment][
                    "removed"
                ] = commit.committed_datetime

            # Update the current state of comments for the file
            file_comments[absolute_file_path]["current_comments"] = current_comments
    except git.exc.GitCommandError as e:
        error_info = {
            "file_path": relative_file_path,
            "commit_hash": commit.hexsha,
            "error_message": str(e),
        }
        error_details.append(error_info)


# Function to save defaultdict to CSV
def save_defaultdict_to_csv(csv_file_name):
    with open(csv_file_name, "w", newline="", encoding="utf-8") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["File Path", "Comment", "Introduced", "Removed"])

        for file_path, comments in file_comments.items():
            for comment_text, dates in comments.items():
                if comment_text != "current_comments":
                    # Extracting introduced and removed dates, if they exist
                    introduced = dates.get("introduced")
                    removed = dates.get("removed")
                    # Writing to CSV
                    csv_writer.writerow([file_path, comment_text, introduced, removed])


def save_errors_to_csv(csv_file_name):
    with open(csv_file_name, "w", newline="", encoding="utf-8") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["File Path", "Commit Hash", "Error Message"])

        for error in error_details:
            csv_writer.writerow(
                [error["file_path"], error["commit_hash"], error["error_message"]]
            )


# Modify the analyze_repo function accordingly
def analyze_git_directory(dir, tag=None):
    repo = git.Repo(dir)
    # Checkout to the specified tag, if provided
    if tag:
        repo.git.checkout(tag)
    # List all Python files in the latest version of the repo
    python_files = [f for f in repo.git.ls_files().split("\n") if f.endswith(".py")]
    # List all Fortran files in the latest version of the repo
    fortran_files = [f for f in repo.git.ls_files().split("\n") if f.endswith(".F90")]
    # List all C++ files in the latest version of the repo
    cpp_files = [
        f for f in repo.git.ls_files().split("\n") if f.endswith((".cpp", ".h", ".hpp"))
    ]

    # Using tqdm to show progress bar
    for relative_file_path in tqdm(cpp_files, desc=f"Processing c++ files in {dir}"):
        checkout_file_versions(repo, dir, relative_file_path, "cpp")

    # Using tqdm to show progress bar
    for relative_file_path in tqdm(
        fortran_files, desc=f"Processing fortran files in {dir}"
    ):
        checkout_file_versions(repo, dir, relative_file_path, "fortran")

    # Using tqdm to show progress bar
    for relative_file_path in tqdm(
        python_files, desc=f"Processing python files in {dir}"
    ):
        checkout_file_versions(repo, dir, relative_file_path, "python")


directories = [
    ("../../Projects/Elmer", None),
    ("../../Projects/MOOSE", None),
]

for directory, tag in directories:
    analyze_git_directory(directory, tag)
save_defaultdict_to_csv("all_new_projects_comments.csv")
save_errors_to_csv("all_new_projects_errors.csv")
