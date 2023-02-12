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
from .pathtools import metadata_path
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

    @staticmethod
    def worker(video, fmt, base, skip, output):
        """Executes the required workflows for generating a thumbnail."""
        try:
            thumbnail = ThumbnailFactory.create_thumbnail(fmt, video, base, skip, output)
        except ThumbnailExistsError:
            return print("Skipping '%s'" % os.path.relpath(video.filepath))
        thumbnail.prepare_frames()
        thumbnail.generate()

    def generate(self):
        self.inputs = [file for file in self.inputs if re.match(r"^.*\.(?:(?!png|vtt|json).)+$", file)]
        self.inputs = dict(zip(map(lambda i: metadata_path(i, self.output, self.format), self.inputs), self.inputs))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            videos = executor.map(
                functools.partial(
                    Video,
                    compress=self.compress,
                    interval=self.interval,
                ),
                self.inputs.values(),
            )

        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(
                functools.partial(
                    self.worker,
                    fmt=self.format,
                    base=self.base,
                    skip=self.skip,
                    output=self.output,
                ),
                videos,
            )
