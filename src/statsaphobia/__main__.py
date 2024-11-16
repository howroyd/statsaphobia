import logging
import pathlib

from . import main, mylogging


class MissingFilesError(Exception):
    pass


if __name__ == "__main__":
    ret: int = 0

    with mylogging.Logger() as logger:
        logger.setup_logging_library(logger.queue_handler, level=mylogging.logging.INFO)
        try:
            PASSWORD_FILE: pathlib.Path = pathlib.Path("password.txt")
            INFILE_FILE: pathlib.Path = pathlib.Path("path.txt")

            if not PASSWORD_FILE.exists():
                raise MissingFilesError(f"{PASSWORD_FILE} file does not exist!")
            if not INFILE_FILE.exists():
                raise MissingFilesError(f"{INFILE_FILE} does not exist!")

            PASSWORD: bytes = PASSWORD_FILE.read_bytes()
            INFILE: pathlib.PurePath = pathlib.Path(INFILE_FILE.read_text())
            OUTDIR: pathlib.Path = pathlib.Path("./")
            BACKUPDIR: pathlib.Path = pathlib.Path("./backup/")

            main.main(INFILE, OUTDIR, BACKUPDIR, PASSWORD)

        except MissingFilesError as e:
            logging.error(e)
            exit(1)

    logging.shutdown()
