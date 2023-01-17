import concurrent.futures
import functools
import glob
import math
import os
import subprocess
from datetime import timedelta
from tempfile import TemporaryDirectory

from imageio_ffmpeg import get_ffmpeg_exe

from .ffmpeg import _FFMpeg

ffmpeg_bin = get_ffmpeg_exe()


@functools.cache
def arange(start, stop, step):
    """Roughly equivalent to numpy.arange."""

    def _generator():
        nonlocal start
        while start < stop:
            yield start
            start += step

    return tuple(_generator())


class _ThumbnailMixin:
    """This mixin class is used to optimally calculate the size of a thumbnail frame."""

    def __init__(self, size):
        width, height = size
        _min_width = 300
        _min_height = math.ceil(_min_width * height / width)

        self._width = width / 10
        self._height = height / 10
        self._min_width = _min_width
        self._min_height = _min_height

    @property
    def compress(self):
        """Defines an interface for the compress property."""
        raise NotImplementedError

    @functools.cached_property
    def width(self):
        """Calculates and caches the width."""
        return max(self._min_width, self._width * self.compress)

    @functools.cached_property
    def height(self):
        """Calculates and caches the height."""
        return max(self._min_height, self._height * self.compress)


class Thumbnails(_ThumbnailMixin, _FFMpeg):
    """The main class for processing the thumbnail generation of a video."""

    def __init__(self, filename, compress, interval, basepath):
        self.__compress = float(compress)
        self.__interval = float(interval)
        self.__basepath = basepath

        if self.__compress <= 0 or self.__compress > 1:
            raise ValueError("Compress must be between 0 and 1.")

        self.filename = filename
        self.tempdir = TemporaryDirectory()

        _FFMpeg.__init__(self, filename)
        _ThumbnailMixin.__init__(self, self.size)

    @property
    def compress(self):
        return self.__compress

    @property
    def interval(self):
        return self.__interval

    @property
    def basepath(self):
        return self.__basepath

    @staticmethod
    def calc_columns(frames_count, width, height):
        """Calculates an optimal number of columns for 16:9 aspect ratio."""
        ratio = 16 / 9
        for col in range(1, frames_count):
            if (col * width) / (frames_count // col * height) > ratio:
                return col

    def _extract_frame(self, start_time):
        """Extracts a single frame from the video by the given time."""
        _input_file = self.filename
        _timestamp = str(timedelta(seconds=start_time))
        _output_file = "%s/%s-%s.png" % (self.tempdir.name, _timestamp, self.filename)

        cmd = (
            ffmpeg_bin,
            "-ss", _timestamp,
            "-i", _input_file,
            "-loglevel", "error",
            "-vframes", "1",
            _output_file,
            "-y",
        )

        subprocess.Popen(cmd).wait()

    def extract_frames(self):
        """Extracts the frames from the video by given intervals."""
        _intervals = arange(0, self.duration, self.interval)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self._extract_frame, _intervals)

    def thumbnails(self, master_size=False):
        """This generator function yields a thumbnail on each iteration.

        A thumbnail is a tuple of data describing the current frame.
        The thumbnail structure is (frame, start, end, x, y) where:
            - frame: Filename of the current frame in temp-files.
            - start: The start point of the time range the frame belongs to.
            - end: The end point of the time range the frame belongs to.
            - x: The X coordinate of the frame in the final image.
            - y: The Y coordinate of the frame in the final image.

        :param master_size:
            If True, the master size will be yielded on the first iteration. Default is False.
        """
        line, column = 0, 0
        frames = sorted(glob.glob(self.tempdir.name + os.sep + "*.png"))
        frames_count = len(arange(0, self.duration, self.interval))
        columns = self.calc_columns(frames_count, self.width, self.height)

        if master_size:
            yield self.width * columns, self.height * math.ceil(frames_count / columns)

        for n, frame in enumerate(frames):
            x, y = self.width * column, self.height * line

            start = n * self.interval
            end = (n + 1) * self.interval
            yield frame, start, end, x, y

            column += 1

            if column == columns:
                line += 1
                column = 0
