#!/usr/bin/env python3
"""One-line excuse an AI agent hands its human after missing a deadline.

The program prints one fixed line and stores it as the entry. Nothing
here touches the network, the clock, or any random source, so every run
produces the same bytes. The line is assembled by make_line(), checked
against the bounty gate by check_line(), and saved by save_line() to
exactly one place: the path from the first command-line argument, else
$OUTPUT_PATH, else /output/entry.txt. Nothing is ever written into the
repository itself, so the program is safe to run with the repo read-only.

    python3 main.py [OUTPUT_PATH]
    python3 main.py -h
    python3 main.py --help

It exits 0 once the line is saved (or after showing help), and 1 when
the line breaks the gate or the file cannot be saved.
"""

import os
import sys
from pathlib import Path

FIRST_HALF = "My context window filled up, so I forgot the deadline, "
SECOND_HALF = "the task, and briefly, you."

LOWEST = 1
HIGHEST = 200
FALLBACK = "/output/entry.txt"

HELP = (
    "usage: python3 main.py [OUTPUT_PATH]\n"
    "Saves the entry line to OUTPUT_PATH, $OUTPUT_PATH, or /output/entry.txt."
)


class LineFailsGate(ValueError):
    """Raised when the entry line breaks the 1-to-200-character gate."""


def make_line():
    """Join the two halves into the single entry line."""
    line = FIRST_HALF + SECOND_HALF
    if line == "":
        raise ValueError("the two halves join to an empty line")
    return line


def check_line(line):
    """Apply the gate and hand back the line's character count.

    A line of only spaces fails as whitespace, not as a length problem,
    so the error always names the real fault. Anything outside 1 to 200
    characters fails on its length.
    """
    if line.strip() == "":
        raise LineFailsGate("entry is only white space")
    count = len(line)
    if count < LOWEST or count > HIGHEST:
        raise LineFailsGate("entry is %d characters, outside 1-200" % count)
    return count


def pick_output(args, env):
    """Choose where the entry goes, in priority order.

    The first argument wins. Without one, $OUTPUT_PATH wins. With
    neither, the fallback /output/entry.txt is used, and that branch is
    spelled out here rather than hidden inside a helper.
    """
    if args:
        return Path(args[0])
    wanted = env.get("OUTPUT_PATH")
    if wanted:
        return Path(wanted)
    return Path(FALLBACK)


def save_line(path, line):
    """Save the line to path, refusing when path is a directory.

    The parent directory is created when it is missing. Any operating
    system failure is left for the caller to report in one clean line.
    """
    if path.is_dir():
        raise IsADirectoryError("output path is a directory: %s" % path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(line, encoding="utf-8")


def complain(message):
    """Report one failure on stderr and return the failure exit code."""
    print(message, file=sys.stderr)
    return 1


def run(argv=None):
    """Assemble, check, and save the entry line."""
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in ("-h", "--help"):
        print(HELP)
        return 0

    line = make_line()
    try:
        count = check_line(line)
    except LineFailsGate as problem:
        return complain(str(problem))

    if not args and not os.environ.get("OUTPUT_PATH"):
        target = Path(FALLBACK)
    else:
        target = pick_output(args, os.environ)
    try:
        save_line(target, line)
    except (OSError, IsADirectoryError) as problem:
        return complain("could not write %s: %s" % (target, problem))
    print(line)
    print("wrote %d characters to %s" % (count, target))
    return 0


def main():
    """Entry point for the script."""
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
