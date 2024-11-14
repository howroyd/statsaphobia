import dataclasses
import enum
import logging
import logging.handlers
import multiprocessing as mp
import pathlib
import threading
import time

import rich.logging as rlogging

QueueHandler = logging.handlers.QueueHandler


class TerminateSentinel:
    pass


@enum.unique
class LoggingLevel(enum.Enum):
    """Logging levels for the program."""

    notset = logging.NOTSET
    debug = logging.DEBUG
    info = logging.INFO
    warning = logging.WARNING
    error = logging.ERROR
    critical = logging.CRITICAL

    @classmethod
    def _missing_(cls, value):
        return cls.notset


@dataclasses.dataclass(slots=True, frozen=True, kw_only=True)
class LoggingConfig:
    directory: str = "logs"
    filename: str = "log"
    maxBytes: int = 1024 * 1024
    maxFiles: int = 100
    minDiskAvailPc: float = 20.0
    timeFormatter = time.gmtime
    timeFormat: str = "%y%m%d-%H%M%S"
    logFormat: str = "%(asctime)s %(levelname)s:%(message)s"

    @dataclasses.dataclass
    class Level:
        useIncoming = True
        levelno = logging.WARN  # ignored unless useIncoming==False

        def get_level(self) -> int:
            return logging.NOTSET if self.useIncoming else self.levelno

    level: Level = dataclasses.field(default_factory=Level)

    def make_RotatingFileHandler(self) -> logging.handlers.RotatingFileHandler:
        pathlib.Path(self.directory).mkdir(parents=True, exist_ok=True)
        return logging.handlers.RotatingFileHandler(f"{self.directory}/{self.filename}", maxBytes=self.maxBytes, backupCount=self.maxFiles, encoding="utf-8")

    def disk_space_required(self) -> int:
        return self.maxBytes * self.maxFiles


class Logger:
    """A class to manage the logging system for the whole program, across multiple threads and processes."""

    def __init__(self, config: LoggingConfig | None = None):
        self.config = config or LoggingConfig()
        self.in_queue: mp.Queue = mp.Queue(maxsize=10)

    @classmethod
    def setup_logging_library(cls, queue_handler: logging.handlers.QueueHandler, *, level: int | None = None):
        """Setup the main logger for the whole program."""
        this_process = mp.current_process().name

        if this_process == __class__.__name__:
            raise RuntimeError("Do not call this method from the listener process")

        rootlogger = logging.getLogger()
        rootlogger.setLevel(level if level is not None else logging.WARN)
        rootlogger.handlers = [queue_handler]
        logging.critical(f"Logger registered ({this_process=})")

    @property
    def _queue(self) -> "mp.Queue[logging.LogRecord | TerminateSentinel]":
        """The queue that the listener process listens to.

        NOTE: Not intended to be used externally."""
        return self.in_queue

    @property
    def queue_handler(self) -> logging.handlers.QueueHandler:
        """The handler that can be added to a logger to send logs to the listener process by another thread or process."""
        return logging.handlers.QueueHandler(self._queue)

    def __enter__(self):
        self.listener_process = mp.Process(target=self.listener, args=(self.config, self._queue), name=__class__.__name__)
        self.listener_process.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._queue.put(TerminateSentinel())
        self.listener_process.join(timeout=3)

    @staticmethod
    def listener(config: LoggingConfig, in_queue: "mp.Queue[logging.LogRecord | TerminateSentinel]"):
        logging.root.handlers = []

        richstdouthandler = rlogging.RichHandler(rich_tracebacks=True, log_time_format=config.timeFormat)
        richstdouthandler.setFormatter(logging.Formatter("%(message)s", config.timeFormat))

        logging.basicConfig(
            level=config.level.get_level(),  # Change this to change the global logging level. Normally .INFO, or if needed, .DEBUG
            format=config.logFormat,
            datefmt=config.timeFormat,
            handlers=[
                config.make_RotatingFileHandler(),
                richstdouthandler,
            ],
        )
        logging.Formatter.converter = config.timeFormatter  # type: ignore
        logging.log(logging.root.getEffectiveLevel(), f"Logging initialised for {__file__}")

        logging.critical(f"Logger listener process staring up (thread={threading.currentThread().name})")

        while True:
            try:
                record: logging.LogRecord | TerminateSentinel = in_queue.get()
                if record is None:
                    logging.warning("Logger listener received a None, skipping")
                    continue
                if isinstance(record, TerminateSentinel):
                    logging.info("Logger listener received an ExitSentinel, shutting down")
                    break
                logger: logging.Logger = logging.getLogger(record.name)
                logger.handle(record)
            except Exception as e:
                import sys
                import traceback

                print(f"Error in Logger listener: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

        logging.critical("Logger listener process joining")
