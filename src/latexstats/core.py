import os
from pathlib import Path


def change_dir(dir: str | Path) -> str:
    original_cwd = os.getcwd()
    os.chdir(dir)
    return original_cwd
