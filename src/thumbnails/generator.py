import concurrent.futures
import functools
import itertools
import os
import re

from .constants import DEFAULT_BASE
from .constants import DEFAULT_COMPRESS
from .constants import DEFAULT_FORMAT
from .constants import DEFAULT_INTERVAL
from .constants import DEFAULT_OUTPUT
from .constants import DEFAULT_SKIP
from .pathtools import listdir
from .progress import use_progress
from .thumbnail import ThumbnailExistsError
from .thumbnail import ThumbnailFactory
from .video import Video


class Generator:
    """High-level class for generating thumbnails."""

    def __init__(self, inputs):
        if all(map(os.path.isfile, inputs)):
            self.inputs = set(map(os.path.abspath, inputs))
        elif all(map(os.path.isdir, inputs)):
            self.inputs = set(itertools.chain(*map(listdir, inputs)))
        else:
            exit("Inputs must be all files or all directories.")

        self.base = DEFAULT_BASE
        self.skip = DEFAULT_SKIP
        self.output = DEFAULT_OUTPUT
        self.format = DEFAULT_FORMAT
        self.compress = DEFAULT_COMPRESS
        self.interval = DEFAULT_INTERVAL

        # Remove non-video files in case of input directory already contains other generated files.
        self.inputs = [file for file in self.inputs if re.match(r"^.*\.(?:(?!png|vtt|json).)+$", file)]

    @staticmethod
    def worker(video, fmt, base, skip, output):
        """Executes the required workflows for generating a thumbnail."""
        try:
            thumbnail = ThumbnailFactory.create_thumbnail(fmt, video, base, skip, output)
        except ThumbnailExistsError:
            return print("Skipping '%s'" % os.path.relpath(video.filepath))
        thumbnail.prepare_frames()
        thumbnail.generate()

    def __iter__(self):
        return self

    def __next__(self):
        """Returns the next video to be processed."""
        try:
            return Video(self.inputs.pop(), self.compress, self.interval)
        except IndexError:
            raise StopIteration

    @use_progress
    def generate(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(
                functools.partial(
                    self.worker,
                    fmt=self.format,
                    base=self.base,
                    skip=self.skip,
                    output=self.output,
                ),
                self,
            )
