#!/usr/bin/env python
"""
Formatter script for moriarty code. Start with --help to see help.
"""

import argparse
import logging
import os
import subprocess
import sys
from typing import Iterable, Tuple

# Logging setup
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
CH = logging.StreamHandler()
CH.setLevel(logging.DEBUG)
LOGGER.addHandler(CH)

PROJECT_PATH = [os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".."))]


def get_modified_py_files(branch_name: str) -> Iterable[str]:
    """
    Return the list of modified python files in the repository
    """
    process = subprocess.run(
        ["git", "diff", branch_name, "--name-only"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    file_list = process.stdout.decode("utf-8").split("\n")
    return [py_file for py_file in file_list if py_file.endswith(".py")]


def get_args() -> argparse.Namespace:
    """
    Return a namespace with all the parsed arguments.

    This is the place where the valid arguments are declared.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", action="store_true", help="Increase logging level to output standard error in linting tools.",
    )
    parser.add_argument(
        "--fast", action="store", help="Only format the python files which differ when comparing to branch named FAST.",
    )
    parser.add_argument(
        "--dry",
        action="store_true",
        help="Only print the changes each tool would make to the files instead of modifying them.",
    )
    parser.add_argument(
        "filename",
        nargs="*",
        help=f"All filenames to format. Will format the whole project ({PROJECT_PATH[0]}) if not given.",
    )
    return parser.parse_args()


def run_black(file_list: Iterable[str], dry_run: bool = False) -> Tuple[str, str]:
    """
    Run black on each file/folder of FILE_LIST.
    No modification is made on the filesystem if DRY_RUN is true.

    Return the standard output and the standard error of the command.
    """
    black_command = ["black"]
    if dry_run:
        black_command += ["--check"]
    black_command += file_list
    process = subprocess.run(black_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stdout.decode("utf-8"), process.stderr.decode("utf-8")


def format_code(args: argparse.Namespace) -> None:
    """
    Format the code following the arguments given in the command line and parsed by get_args().
    """
    if args.fast:
        all_files = get_modified_py_files(args.fast)
        if not all_files:
            LOGGER.warning(
                "There are no python modified files between current working directory and %s Exiting.", args.fast,
            )
            sys.exit(0)
    elif args.filename:
        all_files = args.filename
    else:
        all_files = PROJECT_PATH

    if args.debug:
        LOGGER.setLevel(logging.DEBUG)

    LOGGER.info("Files or folder handled : %s", all_files)

    LOGGER.info("*" * 80 + "\nRunning Black\n" + "*" * 80)
    out, err = run_black(all_files, args.dry)
    LOGGER.info("*" * 10 + " Standard output :\n%s" + "*" * 10, out)
    LOGGER.debug("*" * 10 + " Standard error :\n%s" + "*" * 10, err)
    LOGGER.info("Done")


if __name__ == "__main__":
    format_code(get_args())
