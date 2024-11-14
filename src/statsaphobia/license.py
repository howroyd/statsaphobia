import rich.console as rconsole
import rich.panel as rpanel


def license() -> str:
    """Make the license string"""
    return r"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License version 2 as published by
    the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    More information, source code and license terms can be found at:
    [link=https://github.com/howroyd/statsaphobia]https://github.com/howroyd/statsaphobia[/link]"""


def info() -> str:
    return r"""
    This software requires two files to be present in the same directory:

    - A file named `password.txt` containing the password to decrypt the save file.
    - A file named `path.txt` containing the path to the save file; e.g.
        C:\Users\Simon\AppData\LocalLow\Kinetic Games\Phasmophobia\SaveFile.txt

    We will copy the save file to a backup directory and use the copy to decrypt and decode the save file.

    At no point will we write to the games save file, we ONLY read it.
    No interrogation of the game is made.  No decompilation occurs.
    We only read the save file and decrypt it using the password you provide in `password.txt`.

    Press Ctrl+C to exit the programme."""


def info_rich() -> str:
    return r"""
    [yellow]This software requires two files to be present in the same directory as this .exe:

    - A file named `password.txt` containing the password to decrypt the save file.
    - A file named `path.txt` containing the path to the save file; e.g.
        C:\Users\Simon\AppData\LocalLow\Kinetic Games\Phasmophobia\SaveFile.txt
    [/]
    We will copy the save file to a backup directory and use the copy to decrypt
    and decode the save file.  Each time the save file changes, we will repeat this process.

    [red]At no point will we write to the games save file, we ONLY read it.
    No interrogation of the game memory or source code is made.  No decompilation occurs.
    We only read the save file and decrypt it using the password you provide in `password.txt`.[/]

    [green]Press Ctrl+C or close the window to exit the programme.[/]"""


def preamble_rich() -> None:
    console = rconsole.Console(record=True)
    console.print(rpanel.Panel.fit(license(), title="License"))
    console.print(rpanel.Panel.fit(info_rich(), title="Information"))
    return console.export_text()
