import json
import pathlib

import matplotlib.pyplot as plt


def plot_played_maps(data: dict, outdir: pathlib.Path) -> pathlib.Path:
    maps: list[tuple[str, int]] = sorted(data["playedMaps"]["value"].items(), key=lambda x: x[1], reverse=True)
    map_names: list[str] = [map[0].replace("_", " ").title() for map in maps]
    map_counts: list[int] = [map[1] for map in maps]

    plt.style.use("bmh")
    fig, ax = plt.subplots()

    bars = ax.bar(map_names, map_counts)

    barcolour = bars[0].get_facecolor()

    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            round(bar.get_height(), 1),
            horizontalalignment="center",
            color=barcolour,
            weight="bold",
        )

    ax.set_title("Most Played Maps")
    ax.set_ylabel("Times Played")
    ax.xaxis.set_tick_params(rotation=90)

    fig.tight_layout()
    fig.savefig(outdir / "played_maps.png")

    return outdir / "played_maps.png"


def plot_common_ghosts(data: dict, outdir: pathlib.Path) -> pathlib.Path:
    common_ghosts: dict[str, int] = {k: v for k, v in sorted(data["mostCommonGhosts"]["value"].items(), key=lambda x: x[1], reverse=True)}
    ghost_kills: dict[str, int] = {k: v for k, v in sorted(data["ghostKills"]["value"].items(), key=lambda x: x[1], reverse=True)}
    ratio_ghosts: dict[str, float] = {
        k: v
        for k, v in sorted(
            {k: common_ghosts.get(k, 0) / (ghost_kills.get(k, 1) or 1) for k in set(common_ghosts.keys()) | set(ghost_kills.keys())}.items(),
            key=lambda x: x[1],
            reverse=False,
        )
    }

    ghost_data: dict[str, dict[str, int]] = {
        k: {
            "ratio": ratio_ghosts.get(k, 0),
            "occurrence": common_ghosts.get(k, 0),
            "deaths": ghost_kills.get(k, 0),
        }
        for k in ratio_ghosts.keys()
    }

    fig, ax = plt.subplots()

    x = range(len(ratio_ghosts.keys()))
    width = 0.4
    multiplier = 0

    data = {
        "occurrence": [ghost_data[k]["occurrence"] for k in ghost_data.keys()],
        "deaths": [ghost_data[k]["deaths"] for k in ghost_data.keys()],
    }

    for attribute, measurement in data.items():
        offset = width * multiplier
        rects = ax.bar([val + offset for val in x], measurement, width, label=attribute)
        multiplier += 1

        barcolour = rects[0].get_facecolor()

        for bar in rects:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                round(bar.get_height(), 1),
                horizontalalignment="center",
                color=barcolour,
                weight="bold",
            )

    ax.set_title("Most Common Ghosts")
    ax.set_ylabel("Occurrence/Deaths")
    ax.set_xticks([val + width for val in x], labels=ratio_ghosts.keys(), rotation=90)

    fig.tight_layout()
    fig.savefig(outdir / "common_ghosts.png")

    return outdir / "common_ghosts.png"


def do_plot(infile: pathlib.Path, outdir: pathlib.Path) -> pathlib.Path:
    outdir.mkdir(parents=True, exist_ok=True)

    data: dict = json.loads(infile.read_text())

    played_maps: pathlib.Path = plot_played_maps(data, outdir)
    common_ghosts: pathlib.Path = plot_common_ghosts(data, outdir)
