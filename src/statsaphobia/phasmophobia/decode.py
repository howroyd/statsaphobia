import json
import pathlib
from collections.abc import MutableMapping

from . import maps


def to_string(data: bytes) -> str:
    """Convert bytes to a string, removing padding"""
    return data.rsplit(b"}", 1)[0].decode("utf-8").strip() + "}"


def fix_string(data: str) -> str:
    trimmed = data.strip().replace("\r", "").replace("\n", "").replace("\t", "")

    playedmaps = trimmed.find("playedMaps")
    assert playedmaps != -1, "playedMaps not found"

    value = trimmed[playedmaps:].find("value")
    assert value != -1, "value not found"
    value += playedmaps

    openbracket = trimmed[value:].find("{")
    assert openbracket != -1, "openbracket not found"
    openbracket += value

    closebracket = trimmed[openbracket:].find("}")
    assert closebracket != -1, "closebracket not found"
    closebracket += openbracket

    firstchunk = trimmed[:openbracket]
    badchunk = trimmed[openbracket : closebracket + 1]
    lastchunk = trimmed[closebracket + 1 :]

    fixedchunk = '"' + badchunk[1:-1] + '"'

    return firstchunk + fixedchunk + lastchunk


def from_json(data: str) -> dict:
    """Convert a string to a JSON object."""
    try:
        return {k: v for k, v in sorted(json.loads(fix_string(data)).items())}
    except json.JSONDecodeError:
        pass
    data = fix_string(data)
    return {k: v for k, v in sorted(json.loads(fix_string(data)).items())}


def fix_mapping(mapping: MutableMapping) -> MutableMapping:
    playedmaps = mapping["playedMaps"]["value"]

    playedmapsfixed = {maps.MapID(int(k)).name: int(v) for k, v in dict(this.split(":") for this in map(str.strip, playedmaps.split(","))).items()}

    mapping["playedMaps"]["value"] = playedmapsfixed

    return mapping


def do_decode(infile: pathlib.Path, outdir: pathlib.Path) -> pathlib.Path:
    """Decode the save file."""
    decrypted_bytes: bytes = infile.read_bytes()
    decrypted_str: str = to_string(decrypted_bytes)
    decoded: dict = from_json(decrypted_str)
    fixed: dict = fix_mapping(decoded)
    outfile = outdir / (infile.stem + ".json")
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(json.dumps(fixed, indent=4))
    return outfile
