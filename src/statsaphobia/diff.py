import datetime
import json
import pathlib

import deepdiff
import rich


def print_diff(oldfile: pathlib.Path, newfile: pathlib.Path) -> None:
    diff = deepdiff.DeepDiff(json.loads(oldfile.read_text()), json.loads(newfile.read_text()), ignore_order=True)

    if diff:
        rich.print(datetime.datetime.now())
        rich.print(diff)
