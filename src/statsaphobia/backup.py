import pathlib
import shutil


def get_next_backup_path(path: pathlib.Path) -> pathlib.Path:
    """Get the next backup path."""
    i = 0
    while (next_backup := path.with_name(f"{path.stem}_{i}{path.suffix}")).exists():
        i += 1

    return next_backup


def do_backup(src: pathlib.Path, dest: pathlib.Path) -> pathlib.Path:
    """Backup the save file.  Returns the path to the new backup file."""
    dest = get_next_backup_path(dest / src.name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest
