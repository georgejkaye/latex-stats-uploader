import os
import shutil
import subprocess
import sys

from git import Commit, Repo
import requests
from latexstats.core import change_dir
from latexstats.stats import get_commit_stats
from latexstats.upload import upload


def check_working_dir(output_dir: str):
    if os.path.isdir(output_dir):
        overwrite = input(
            "Directory " + output_dir + " already exists, overwrite? (y/N) "
        )
        if not overwrite == "y":
            exit(1)
        shutil.rmtree(output_dir)


def clone_repo(clone_link: str, working_dir: str):
    Repo.clone_from(clone_link, working_dir)


def initialise_submodules(working_dir: str):
    cwd = change_dir(working_dir)
    subprocess.run(["git", "submodule", "update", "--init"])
    change_dir(cwd)


def get_commits(repo: Repo) -> list[Commit]:
    return list(repo.iter_commits("main"))


def checkout(working_dir: str, repo: Repo, commit: Commit):
    try:
        repo.git.stash()
        repo.git.checkout(commit.hexsha)
        cwd = change_dir(working_dir)
        subprocess.run(["git", "submodule", "update"])
        change_dir(cwd)
    except Exception as e:
        print(e)
        return False
    return True


def compile_latex(working_dir: str, main_file: str) -> bool:
    cwd = change_dir(working_dir)
    pdf_file = f"{main_file}.pdf"
    if os.path.isfile(pdf_file):
        os.remove(pdf_file)
    subprocess.run(
        ["latexmk", "-pdf", main_file, "-halt-on-error", "-interaction=nonstopmode"]
    )
    success = os.path.isfile(pdf_file)
    change_dir(cwd)
    return success


def populate_one_commit(
    working_dir: str,
    repo: Repo,
    commit: Commit,
    main_file: str,
    endpoint: str,
    user: str,
    password: str,
):
    checked_out = checkout(working_dir, repo, commit)
    if not checked_out:
        print("Could not check out...")
        return
    latex_compiled = compile_latex(working_dir, main_file)
    if not latex_compiled:
        print("Could not compile latex...")
        return
    stats = get_commit_stats(working_dir, commit, main_file)
    if not stats:
        print("Could not get stats...")
        return
    upload(stats, endpoint, user, password)


def get_uploaded(endpoint: str) -> list[str]:
    url = f"{endpoint}/commits"
    response = requests.get(url)
    commits = response.json()
    return list(map(lambda c: c["commit_sha"], commits))


def populate(
    repo_link: str,
    working_dir: str,
    main_file: str,
    endpoint: str,
    user: str,
    password: str,
):
    uploaded = get_uploaded(endpoint)
    check_working_dir(working_dir)
    clone_repo(repo_link, working_dir)
    repo = Repo(working_dir)
    initialise_submodules(working_dir)
    commits = get_commits(repo)
    for commit in commits:
        if commit.hexsha in uploaded:
            print(f"Skipping commit {commit.hexsha[0:8]}...")
        else:
            print(f"Populating {commit.hexsha[0:8]}")
            populate_one_commit(
                working_dir, repo, commit, main_file, endpoint, user, password
            )


if __name__ == "__main__":
    if not len(sys.argv) == 7:
        print(
            "Args: <repo_link> <working_dir> <main_file> <endpoint> <user> <password>"
        )
        exit(1)
    populate(
        sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
    )
