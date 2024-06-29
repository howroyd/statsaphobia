import pathlib
import threading
from collections.abc import Callable

from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer


class Event(LoggingEventHandler):
    def __init__(self, eventhandler: Callable, *args, **kwargs) -> None:
        self.eventhandler = eventhandler
        super().__init__(*args, **kwargs)

    def on_modified(self, event):
        self.eventhandler()


class FileWatcher:
    def __init__(self, eventhandler: Callable, path: pathlib.Path) -> None:
        self.eventhandler = eventhandler
        self.path = path
        self.event = Event(eventhandler)
        self.thread = threading.Thread(target=self._thread)
        self.kill_event = threading.Event()

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.kill_event.set()
        self.thread.join()

    def _thread(self):
        observer = Observer()
        observer.schedule(self.event, self.path.parent)
        observer.start()
        print(f"Watching {self.path}")
        self.kill_event.wait()
        observer.stop()
        observer.join()
