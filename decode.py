import enum
import hashlib
import json
import pathlib
from typing import MutableMapping

import matplotlib.pyplot as plt
import rich
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PASSWORD: bytes = pathlib.Path("password.txt").open().read().encode("utf-8")
BLOCK_SIZE: int = 16
BYTES_PADDING: bytes = b"\x08"


@enum.unique
class MapID(enum.IntEnum):
    """Map IDs used in the save file to the maps' names."""

    SUNNY_REST = 0
    SUNNY = 1
    BLEASDALE = 2
    WOODWIND = 3
    MAPLE = 4
    EDGEFIELD = 5
    GRAFTON = 6
    PRISON = 7
    POINT_HOPE = 8
    RIDGEVIEW = 9
    HIGHSCHOOL = 10
    TANGLEWOOD = 11
    WILLOW = 12
    # ??? = 13 # Possibly just a logical gap/sentinel?
    ASYLUM = 14  # TODO Confirm this was remapped from 8??


def get_iv(raw_data: bytes) -> bytes:
    """Get the IV from the raw data."""
    return raw_data[:BLOCK_SIZE]


def get_cyphertext(raw_data: bytes) -> bytes:
    """Get the cyphertext from the raw data and remove padding."""
    ret = raw_data[BLOCK_SIZE:]
    retlen = len(ret) % BLOCK_SIZE
    if retlen != 0:
        ret = ret[:-retlen]
    return ret


def make_key(password: str, iv: bytes) -> bytes:
    """Make a key from a password and an IV."""
    return hashlib.pbkdf2_hmac("sha1", password, iv, 100, dklen=BLOCK_SIZE)


def decypher(rawdata: bytes, password: bytes) -> bytes:
    iv = get_iv(rawdata)
    cyphertext = get_cyphertext(rawdata)
    key = make_key(password, iv)

    cipher = Cipher(algorithms.AES128(key), modes.CBC(iv))

    decryptor = cipher.decryptor()

    return decryptor.update(cyphertext) + decryptor.finalize()


def to_string(data: bytes) -> str:
    """Convert bytes to a string, removing padding"""
    return data.rstrip(BYTES_PADDING).decode("utf-8").strip()


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

    playedmapsfixed = {
        MapID(int(k)).name: int(v)
        for k, v in dict(
            this.split(":") for this in map(str.strip, playedmaps.split(","))
        ).items()
    }

    mapping["playedMaps"]["value"] = playedmapsfixed

    return mapping


def main(password: bytes, filename: str = "SaveFile.txt"):
    decryptedbytes = decypher(
        pathlib.Path(filename or "SaveFile.txt").open("rb").read(), password
    )

    asjson = from_json(to_string(decryptedbytes))
    fix_mapping(asjson)

    rich.print(asjson)

    playedmaps = {
        k: v
        for k, v in sorted(
            asjson["playedMaps"]["value"].items(), key=lambda x: x[1], reverse=True
        )
    }
    plt.bar(playedmaps.keys(), playedmaps.values())
    plt.grid(which="major", axis="y", zorder=-1.0)

    plt.show()


if __name__ == "__main__":
    main(PASSWORD)
