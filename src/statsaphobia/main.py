import pathlib
import time

from rich import print

from . import backup, decrypt, diff, html, watcher
from .phasmophobia import decode, plot

BLOCK_SIZE: int = 16


def license() -> str:
    """Make the license string"""
    return """\tThis program is free software; you can redistribute it and/or modify
\tit under the terms of the GNU General Public License version 2 as published by
\tthe Free Software Foundation.

\tThis program is distributed in the hope that it will be useful,
\tbut WITHOUT ANY WARRANTY; without even the implied warranty of
\tMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
\tGNU General Public License for more details.

\tYou should have received a copy of the GNU General Public License along
\twith this program; if not, write to the Free Software Foundation, Inc.,
\t51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

\tMore information, source code and license terms can be found at:
\t[link=https://github.com/howroyd/statsaphobia]https://github.com/howroyd/statsaphobia[/link]
"""


def preamble() -> None:
    print(license())
    print(
        r"""
    [yellow]This software requires two files to be present in the same directory:

    - A file named `password.txt` containing the password to decrypt the save file.
    - A file named `path.txt` containing the path to the save file; e.g.
        C:\Users\Simon\AppData\LocalLow\Kinetic Games\Phasmophobia\SaveFile.txt"
    [/]
    We will copy the save file to a backup directory and use the copy to decrypt and decode the save file.

    [red]At no point will we write to the games save file, we ONLY read it.
    No interrogation of the game is made.  No decompilation occurs.
    We only read the save file and decrypt it using the password you provide in `password.txt`.[/]

    [green]Press Ctrl+C to exit the programme.[/]"""
    )
    print()


def main(infile: pathlib.Path, outdir: pathlib.Path, backupdir: pathlib.Path, password: bytes) -> None:
    preamble()

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
        graphfiles: dict[str, pathlib.Path] = plot.do_plot(jsonfile, outdir / "graphs")
        oldfile = jsonfile

    on_change()

    with watcher.FileWatcher(on_change, infile):
        while True:
            time.sleep(1)
