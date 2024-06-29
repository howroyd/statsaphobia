#!./.venv/bin/python3
import importlib.metadata
import pathlib
import platform

import PyInstaller.__main__ as pyinstaller

VERSION = importlib.metadata.version("statsaphobia")
DIRPATH = pathlib.Path().absolute()
ENTRYPOINT = f'{DIRPATH / "run.py"}'
SEPARATOR = ";" if platform.platform().startswith("Windows") else ":"
NAME = f"statsaphobia-{VERSION.replace('.', '_')}"

DATAFILES = [
    f'{DIRPATH / "README.md"}{SEPARATOR}.',
    f'{DIRPATH / "LICENSE"}{SEPARATOR}.',
    f'{DIRPATH / "CONTRIBUTING.md"}{SEPARATOR}.',
    f'{DIRPATH / "CODE_OF_CONDUCT.md"}{SEPARATOR}.',
]

ICON = f'{DIRPATH / "assets" / "icon.png"}'


def build():
    add_data = (("--add-data", item) for item in DATAFILES)
    add_data = [item for tup in add_data for item in tup]

    pyinstaller.run(
        [
            ENTRYPOINT,
            # '--clean',
            "-n",
            NAME,
            "--onefile",
            "--noconfirm",
            "--log-level",
            "WARN",
            *add_data,
            "-i",
            ICON,
        ]
    )


if __name__ == "__main__":
    build()
