import json
import pathlib


def flatten_dict(data: dict, parent_key: str = "", sep: str = "_") -> dict:
    ret = {}

    for k, v in data.items():
        if isinstance(v, dict):
            if "value" in v:
                ret[k] = v["value"]
            else:
                nested = flatten_dict(v)
                if nested:
                    ret.update(nested)
        else:
            pass

    return ret


def do_bot(infile: pathlib.Path, outdir: pathlib.Path) -> dict[str, pathlib.Path]:
    outdir.mkdir(parents=True, exist_ok=True)

    data: dict = json.loads(infile.read_text())

    ret = flatten_dict(data)

    for k, v in ret.items():
        if isinstance(v, int | float | str | bool):
            with (outdir / f"{k.lower()}.txt").open("w") as f:
                f.write(str(v))
        else:
            print(f"Bot skipping {k} as it is not a simple type")

    return {"root": outdir}
