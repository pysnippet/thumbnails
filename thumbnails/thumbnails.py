import concurrent.futures
import glob
import math
import os
import subprocess
from datetime import timedelta
from tempfile import TemporaryDirectory

from imageio_ffmpeg import get_ffmpeg_exe

from .ffmpeg import _FFMpeg

ffmpeg_bin = get_ffmpeg_exe()


def arange(start, stop, step):
    def _generator():
        nonlocal start
        while start < stop:
            yield start
            start += step

    return tuple(_generator())


class _ThumbnailMixin:
    def __init__(self, size):
        self._w = None
        self._h = None

        width, height = size
        _min_width = 300
        _min_height = math.ceil(_min_width * height / width)

        self._width = width / 10
        self._height = height / 10
        self._min_width = _min_width
        self._min_height = _min_height

    @property
    def compress(self):
        raise NotImplementedError

    @property
    def width(self):
        if not self._w:
            self._w = max(self._min_width, self._width * self.compress)
        return self._w

    @property
    def height(self):
        if not self._h:
            self._h = max(self._min_height, self._height * self.compress)
        return self._h


class Thumbnails(_ThumbnailMixin, _FFMpeg):
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
        ratio = 16 / 9
        for col in range(1, frames_count):
            if (col * width) / (frames_count // col * height) > ratio:
                return col

    def _extract_frame(self, start_time):
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
        _intervals = arange(0, self.duration, self.interval)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self._extract_frame, _intervals)

    def thumbnails(self, master_size=False):
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
