import os
from pathlib import Path
import re
import subprocess

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CommitStats:
    sha: str
    dt: datetime
    words: int
    pages: int
    diagrams: int
    unique_files: int


def get_words(main_file: str) -> int:
    if not os.path.isfile(main_file):
        raise FileNotFoundError(f"Main file {main_file} not found")
    output = subprocess.check_output(["texcount", "-inc", main_file]).decode()
    words_in_texts = list(
        filter(lambda x: x.find("Words in text:") != -1, output.split("\n"))
    )
    words_string = words_in_texts[-1].split(" ")[-1]
    return int(words_string)


source_file_regex = r"\(\./([a-z0-9\-/\n]*\.([a-z\n]*))"
binary_file_regex = r"<\./(.*?)(?:>|,)"
dont_care_extensions = ["aux", "out", "nav", "nls", "ind", "bbl", "toc"]


def sanitise_file_name(file: str) -> str:
    return file.replace("\npdf", "").replace("\n", "").replace("//", "/")


def get_input_files(log_file: str) -> list[str]:
    # Check if the log file exists
    if not os.path.isfile(log_file):
        raise FileNotFoundError(f"Log file {log_file} not found!")
    # Read the log file
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        log_text = f.read()
    # Scrape for source and binary files, which are represented differently
    source_files = re.findall(source_file_regex, log_text)
    binary_files = re.findall(binary_file_regex, log_text)
    file_names = []
    # Discard source files we don't care about
    # Also get rid of duplicates
    for file in source_files:
        if file[1].replace("\n", "") not in dont_care_extensions:
            file_name = sanitise_file_name(file[0])
            file_names.append(file_name)
    for file in binary_files:
        file_name = sanitise_file_name(file)
        file_names.append(file_name)
    return file_names


def get_figures(files: list[str]) -> int:
    figures = list(
        set(
            (
                filter(
                    lambda x: "figures" in x
                    and "vars" not in x
                    and "defs" not in x
                    and "styles" not in x
                    and ".tikz" in x,
                    files,
                )
            )
        )
    )
    return len(figures)


def get_unique_files(files: list[str]) -> int:
    unique_files = list(set(files))
    return len(unique_files)


def get_pages(pdf_file: str) -> int:
    if not os.path.isfile(pdf_file):
        raise FileNotFoundError(f"Output pdf {pdf_file} not found")
    output = subprocess.check_output(
        ["pdftk", pdf_file, "dump_data", "output"]
    ).decode()
    for line in output.split("\n"):
        if "NumberOfPages" in line:
            offset = len("NumberOfPages: ")
            return int(line[offset:])
    raise Exception("No NumberOfPages item in pdftk output")


def get_commit_stats(
    main_file: str, log_file: str, pdf_file: str, sha: str, dt: datetime
) -> Optional[CommitStats]:
    words = get_words(main_file)
    pages = get_pages(pdf_file)
    files = get_input_files(log_file)
    diagrams = get_figures(files)
    unique_files = get_unique_files(files)
    commit_stats = CommitStats(sha, dt, words, pages, diagrams, unique_files)
    return commit_stats
