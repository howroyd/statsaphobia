import datetime
import json
import logging
import pathlib

import deepdiff
import rich.console as rconsole
import rich.panel as rpanel
import rich.pretty as rpretty


def print_diff(oldfile: pathlib.Path, newfile: pathlib.Path) -> None:
    diff = deepdiff.DeepDiff(json.loads(oldfile.read_text()), json.loads(newfile.read_text()), ignore_order=True)

    if diff:
        console = rconsole.Console(record=True)
        console.print("Difference detected:")
        console.print(rpanel.Panel.fit(str(diff), title=f"Difference at {datetime.datetime.now()}"))
        logging.info(console.export_text())
