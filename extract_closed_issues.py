import os
import time
import pandas as pd
from github import Github, RateLimitExceededException


# Function to check rate limit and sleep if necessary
def check_rate_limit(g):
    rate_limit = g.get_rate_limit().core
    remaining = rate_limit.remaining
    reset = rate_limit.reset.timestamp()
    now = time.time()

    if remaining < 10:
        sleep_time = reset - now + 1  # add 1 second buffer
        print(f"Rate limit exceeded. Sleeping for {sleep_time:.2f} seconds.")
        time.sleep(sleep_time)


# Initialize the GitHub API client
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise ValueError("Please set the GITHUB_TOKEN environment variable")
g = Github(token)


# Function to collect all closed issues from a given repository and save as CSV
def collect_closed_issues(repo_name, output_file):
    repo = g.get_repo(repo_name)
    closed_issues = []
    try:
        for issue in repo.get_issues(state="closed"):
            check_rate_limit(g)
            closed_issues.append(
                {
                    "id": issue.id,
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "state": issue.state,
                    "created_at": issue.created_at,
                    "closed_at": issue.closed_at,
                    "labels": [label.name for label in issue.labels],
                }
            )
    except RateLimitExceededException:
        check_rate_limit(g)

    df = pd.DataFrame(closed_issues)
    df.to_csv(output_file, index=False)
    print(f"Saved {len(closed_issues)} closed issues to {output_file}")


if __name__ == "__main__":
    repo_name = "ESCOMP/CTSM"  # Name of the repository
    output_file = "closed_issues.csv"  # Output file name
    collect_closed_issues(repo_name, output_file)
