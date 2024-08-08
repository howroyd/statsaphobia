import pathlib
import time
from typing import NoReturn

from . import backup, decrypt, diff, html, watcher
from .phasmophobia import bot, decode, plot

BLOCK_SIZE: int = 16


def main(infile: pathlib.Path, outdir: pathlib.Path, backupdir: pathlib.Path, password: bytes) -> NoReturn:
    oldfile: pathlib.Path | None = None

    def on_change() -> None:
        nonlocal oldfile
        time.sleep(1)  # HACK: Hold off for a bit in case the file is written twice in quick succession
        backupfile: pathlib.Path = backup.do_backup(infile, backupdir)
        decryptedfile: pathlib.Path = decrypt.do_decrypt(backupfile, outdir / "decrypted", BLOCK_SIZE, password)
        jsonfile: pathlib.Path = decode.do_decode(decryptedfile, outdir / "decoded")
        if oldfile:
            diff.print_diff(oldfile, jsonfile)
        html.do_html(jsonfile, outdir)
        plot.do_plot(jsonfile, outdir / "graphs")
        bot.do_bot(jsonfile, outdir / "bot")
        oldfile = jsonfile

    on_change()

    with watcher.FileWatcher(on_change, infile):
        while True:
            time.sleep(1)
