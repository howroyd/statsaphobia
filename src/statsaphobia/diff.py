import datetime
import json
import logging
import pathlib
import json
import deepdiff
import rich.console as rconsole
import rich.panel as rpanel
import rich.json as rjson

def print_diff(oldfile: pathlib.Path, newfile: pathlib.Path) -> None:
    """Print the difference between two files"""
    diff = deepdiff.DeepDiff(json.loads(oldfile.read_text()), json.loads(newfile.read_text()), ignore_order=True)

    if diff:
        console = rconsole.Console(record=True)
        with console.capture() as capture:
            console.print("Difference detected:")
            x = rjson.JSON.from_data(diff.to_json(), indent=2, ensure_ascii=True, highlight=False)
            console.print(x)
        logging.info(capture.get())
