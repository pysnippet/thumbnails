from rich.progress import Progress as RichProgress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn


class Progress:
    _instance = RichProgress(SpinnerColumn(), TextColumn("[white]{task.description}{task.fields[status]}"))

    def __init__(self, description, done="Process completed"):
        self.task = self._instance.add_task(description, status=" ... [yellow]processing")
        self.done = done

    def update(self, description, status=" ... [yellow]processing"):
        self._instance.update(self.task, description=description, status=status, refresh=True)

    @classmethod
    def start(cls):
        cls._instance.start()

    @classmethod
    def stop(cls):
        cls._instance.stop()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.update(self.done, status=" ... [green]done")
