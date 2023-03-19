import functools

from rich.progress import Progress as RichProgress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn


class Progress:
    _running = False
    _instance = RichProgress(SpinnerColumn(finished_text="*"),
                             TextColumn("[white]{task.description}{task.fields[status]}"))

    def __init__(self, description):
        if self._running:
            self.task = self._instance.add_task(description, status=" ... [yellow]processing")
        self.description = description

    def update(self, description, status=" ... [yellow]processing"):
        if self._running:
            self._instance.update(self.task, description=description, status=status, refresh=True)

    @classmethod
    def start(cls):
        cls._running = True
        cls._instance.start()

    @classmethod
    def stop(cls):
        cls._running = False
        cls._instance.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, _):
        # Set finished time to 0 to hide the spinner
        self._instance.tasks[self.task].finished_time = 0
        if exc_type is not None:
            return self.update(exc_val, status=" ... [red]failure")
        self.update(self.description, status=" ... [green]success")


def use_progress(func):
    """Decorator for using the progress bar."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        Progress.start()
        try:
            func(*args, **kwargs)
        finally:
            Progress.stop()

    return wrapper
