from datetime import datetime
import os
import sys
import requests

from latexstats.stats import CommitStats, get_commit_stats


def get_token(endpoint: str, user: str, password: str) -> str:
    url = f"{endpoint}/token"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"username": user, "password": password}
    response = requests.post(url, headers=headers, data=data)
    token = response.json()["access_token"]
    return token


def post_stats(endpoint: str, token: str, stats: CommitStats):
    url = f"{endpoint}/commit"
    headers = {"accept": "application/json", "Authorization": f"Bearer {token}"}
    params = {
        "commit_sha": stats.sha,
        "commit_datetime": stats.dt.isoformat(),
        "words": stats.words,
        "pages": stats.pages,
        "diagrams": stats.diagrams,
        "files": stats.unique_files,
    }
    response = requests.post(url, headers=headers, params=params)
    print(response)


def upload(stats: CommitStats, endpoint: str, user: str, password: str):
    token = get_token(endpoint, user, password)
    post_stats(endpoint, token, stats)


def get_stats_from_compiled(
    main_file: str,
    sha: str,
    dt: datetime,
    endpoint: str,
    user: str,
    password: str,
):
    stats = get_commit_stats(main_file, sha, dt)
    if stats is not None:
        upload(stats, endpoint, user, password)


if __name__ == "__main__":
    if not len(sys.argv) == 7:
        print("Args: <main_file> <sha> <datetime> <endpoint> <user> <password>")
        exit(1)
    get_stats_from_compiled(
        sys.argv[1],
        sys.argv[2],
        datetime.fromisoformat(sys.argv[3]),
        sys.argv[4],
        sys.argv[5],
        sys.argv[6],
    )
