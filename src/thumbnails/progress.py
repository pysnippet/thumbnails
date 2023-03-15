from rich.live import Live
from rich.status import Status


class Progress:
    def __init__(self, status, done="Process completed"):
        self.status = Status(status)
        self.live = Live(self.status)
        self.done = done

    def update(self, status):
        self.status.update(status)
        self.live.update(self.status)

    def __enter__(self):
        self.live.start()
        return self

    def __exit__(self, *_):
        self.live.update("[white]%s ... [/white][green]done[/green]" % self.done)
        self.live.stop()
