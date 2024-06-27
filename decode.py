import enum
import datetime
import hashlib
import json
import pathlib
import time
from typing import MutableMapping

import deepdiff
import matplotlib.pyplot as plt
import numpy as np
import rich
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

PASSWORD: bytes = pathlib.Path("password.txt").open().read().encode("utf-8")
BLOCK_SIZE: int = 16
OUTFILE: pathlib.Path = "./decrypted.json"
INFILE: pathlib.PurePath = pathlib.Path(pathlib.Path("path.txt").open().read())


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
    ASYLUM = 8
    RIDGEVIEW = 9
    HIGHSCHOOL = 10
    TANGLEWOOD = 11
    WILLOW = 12
    # ??? = 13 # Possibly just a logical gap/sentinel? Maybe the tutorial?
    POINT_HOPE = 14


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

    playedmapsfixed = {
        MapID(int(k)).name: int(v)
        for k, v in dict(
            this.split(":") for this in map(str.strip, playedmaps.split(","))
        ).items()
    }

    mapping["playedMaps"]["value"] = playedmapsfixed

    return mapping


def handle_file_change(password):
    time.sleep(2)  # Wait for the file to be written to so we don't hog the inode

    with INFILE.open("rb") as f:
        decryptedbytes = decypher(f.read(), password)

    asjson: dict = fix_mapping(from_json(to_string(decryptedbytes)))

    try:
        with open(OUTFILE, "r") as f:
            lastjson = json.load(f)

            diff = deepdiff.DeepDiff(lastjson, asjson, ignore_order=True)

            if diff:
                rich.print(datetime.datetime.now())
                rich.print(diff)

            # for key, value in asjson.items():
            #     if key in lastjson and lastjson[key] == value:
            #         continue
            #     else:
            #         rich.print(f"{key} has changed from:")
            #         rich.print(lastjson[key] if key in lastjson else 'None')
            #         rich.print("to")
            #         rich.print(value)
            #         rich.print("")

    except FileNotFoundError:
        pass

    with open(OUTFILE, "w") as f:
        json.dump(asjson, f, indent=2)


class Event(LoggingEventHandler):
    def on_modified(self, event):
        handle_file_change(PASSWORD)


def main(password: bytes, filename: str = "SaveFile.txt"):
    # rich.print(asjson)

    observer = Observer()
    observer.schedule(Event(), INFILE.parent)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    ################################

    with INFILE.open("rb") as f:
        decryptedbytes = decypher(f.read(), password)

    asjson: dict = fix_mapping(from_json(to_string(decryptedbytes)))

    # plt.style.use('seaborn-v0_8-darkgrid')
    plt.style.use("bmh")

    fig, ax = plt.subplots()
    playedmaps = {
        k: v
        for k, v in sorted(
            asjson["playedMaps"]["value"].items(), key=lambda x: x[1], reverse=True
        )
    }
    playedmapsbars = ax.bar(playedmaps.keys(), playedmaps.values())
    playedmapsbarbar_colour = playedmapsbars[0].get_facecolor()
    for bar in playedmapsbars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            round(bar.get_height(), 1),
            horizontalalignment="center",
            color=playedmapsbarbar_colour,
            weight="bold",
        )
    # ax.grid(which="major", axis="y", zorder=-1.0)
    ax.set_title("Most Played Maps")
    ax.set_ylabel("Times Played")
    ax.set_xticklabels(
        (key.replace("_", " ").title() for key in playedmaps.keys()), rotation=90
    )
    fig.tight_layout()

    fig2, ax2 = plt.subplots()
    commonghosts = {
        k: v
        for k, v in sorted(
            asjson["mostCommonGhosts"]["value"].items(),
            key=lambda x: x[1],
            reverse=True,
        )
    }
    killedbyghosts = {
        k: v
        for k, v in sorted(
            asjson["ghostKills"]["value"].items(), key=lambda x: x[1], reverse=True
        )
    }
    ratioghosts = {
        k: v
        for k, v in sorted(
            {
                k: commonghosts.get(k, 0) / (killedbyghosts.get(k, 1) or 1)
                for k in set(commonghosts.keys()) | set(killedbyghosts.keys())
            }.items(),
            key=lambda x: x[1],
            reverse=True,
        )
    }

    ghostdata = {
        k: {
            "ratio": ratioghosts.get(k, 0),
            "occurrence": commonghosts.get(k, 0),
            "deaths": killedbyghosts.get(k, 0),
        }
        for k in ratioghosts.keys()
    }
    x = np.arange(len(ratioghosts.keys()))  # the label locations
    width = 0.4  # the width of the bars
    multiplier = 0
    data = {
        "occurrence": [x for x in commonghosts.values()],
        "deaths": [x for x in killedbyghosts.values()],
    }
    for attribute, measurement in data.items():
        offset = width * multiplier
        rects = ax2.bar(x + offset, measurement, width, label=attribute)
        # ax2.bar_label(rects, padding=0.5)
        multiplier += 1
        commonghostsbar_colour = rects[0].get_facecolor()
        for bar in rects:
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                round(bar.get_height(), 1),
                horizontalalignment="center",
                color=commonghostsbar_colour,
                weight="bold",
            )

    # commonghostsbars = ax2.bar(ghostdata.keys(), ghostdata.values())

    ax2.grid(which="major", axis="y", zorder=-1.0, alpha=0.33)
    ax2.set_title("Ghost Data")
    ax2.set_xlabel("Ghost")
    ax2.set_ylabel("Times Encountered")
    ax2.set_xticks(x + width, commonghosts.keys(), rotation=90)
    ax2.legend(loc="upper right")
    fig2.tight_layout()

    plt.show()


if __name__ == "__main__":
    main(PASSWORD)
