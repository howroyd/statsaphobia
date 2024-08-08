import pathlib

from rich import print as rprint

from . import license, main

if __name__ == "__main__":
    rprint(license.rich_preamble())

    PASSWORD_FILE: pathlib.Path = pathlib.Path("password.txt")
    INFILE_FILE: pathlib.Path = pathlib.Path("path.txt")

    assert PASSWORD_FILE.exists(), f"{PASSWORD_FILE} file does not exist!"
    assert INFILE_FILE.exists(), f"{INFILE_FILE} does not exist!"

    PASSWORD: bytes = PASSWORD_FILE.read_bytes()
    INFILE: pathlib.PurePath = pathlib.Path(INFILE_FILE.read_text())
    OUTDIR: pathlib.Path = pathlib.Path("./")
    BACKUPDIR: pathlib.Path = pathlib.Path("./backup/")

    main.main(INFILE, OUTDIR, BACKUPDIR, PASSWORD)
