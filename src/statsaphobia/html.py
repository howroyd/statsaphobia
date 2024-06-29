import json
import pathlib

import json2html


def do_html(infile: pathlib.Path, outdir: pathlib.Path) -> pathlib.Path:
    outfile = outdir / "index.html"
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(json2html.json2html.convert(json.loads(infile.read_text())))
    return outfile
