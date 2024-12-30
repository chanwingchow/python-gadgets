import math
import os
import re
from pathlib import Path
from typing import Callable

from natsort import natsorted

"""
version:
    2024.12.30

dependencies:
    pip install natsort
"""


def files_rename(
        direction: str,
        oneach: Callable[[int, int, str], str] = lambda lenght, index, filepath: f"{index:0{lenght}d}",
        filter_regex: str = r"(~\$.*|\S*\.(DS_Store|tmp|temp|ini|lnk))",
):
    """Batch rename all files in a directory.

    The oneach parameter is a function that takes lenght (the recommended length of the filename),
    index(the current file subscript) and filepath, returns the new filename.
    The filter_regex parameter determines which files should be filtered when searching for files.
    """
    filepaths = []

    # Get all filepaths matched.
    for dirpath, _, filenames in os.walk(direction):
        for filename in filenames:
            if not re.match(filter_regex, filename):
                filepaths.append(str(os.path.join(dirpath, filename)))

    # Natural sorting by file name.
    filepaths = natsorted(filepaths)

    # Priority is based on modification time, followed by natural ordering.
    filepaths = sorted(
        filepaths,
        key=lambda p: (os.path.getmtime(p), filepaths.index(p)),
    )

    conflicts = {}
    # Recommended length of new filename.
    length = int(math.log10(len(filepaths))) + 1

    for (index, filepath) in enumerate(filepaths):
        path = Path(filepath)

        new_filepath = os.path.join(path.parent, oneach(length, index, filepath) + path.suffix)

        try:
            # Rename file.
            os.rename(filepath, new_filepath)
        except FileExistsError:
            # Conflicts in naming.
            conflicts[index] = new_filepath

    # Rename conflict files again.
    while len(conflicts) > 0:
        key = list(conflicts.keys())[0]
        try:
            os.rename(filepaths[key], conflicts[key])
            conflicts.pop(key)
        except FileExistsError:
            pass


if __name__ == "__main__":
    myDirection = input("Enter the directory where you want to batch rename files:\n")
    files_rename(myDirection)
