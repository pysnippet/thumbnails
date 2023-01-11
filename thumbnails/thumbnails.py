import concurrent.futures
import glob
import math
import os
import subprocess
from datetime import timedelta
from tempfile import TemporaryDirectory

from PIL import Image
from imageio_ffmpeg import get_ffmpeg_exe
from numpy import arange

from .ffmpeg import _FFMpeg

ffmpeg_bin = get_ffmpeg_exe()


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
    def __init__(self, filename):
        self.__compress = 1.
        self.__interval = 1.
        self.__basepath = ""
        self.thumbnails = []
        self.tempdir = TemporaryDirectory()
        self.filename = filename
        self._vtt_name = filename + ".vtt"
        self._image_name = filename + ".png"

        _FFMpeg.__init__(self, filename)
        _ThumbnailMixin.__init__(self, self.size)

    @property
    def compress(self):
        return self.__compress

    @compress.setter
    def compress(self, value):
        try:
            self.__compress = float(value)
        except ValueError:
            raise ValueError("Compress must be a number.")

    @property
    def interval(self):
        return self.__interval

    @interval.setter
    def interval(self, value):
        try:
            self.__interval = float(value)
        except ValueError:
            raise ValueError("Interval must be a number.")

    @property
    def basepath(self):
        return self.__basepath

    @basepath.setter
    def basepath(self, value):
        self.__basepath = value

    @staticmethod
    def _calc_columns(frames_count, width, height):
        ratio = 16 / 9
        for col in range(1, frames_count):
            if (col * width) / (frames_count // col * height) > ratio:
                return col

    def _extract_frame(self, start_time):
        _input_file = self.filename
        _output_file = "%s/%s-%s.png" % (self.tempdir.name, start_time, self.filename)
        _timestamp = str(timedelta(seconds=start_time))

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

    def join_frames(self):
        line, column = 0, 0
        frames = sorted(glob.glob(self.tempdir.name + os.sep + "*.png"))
        frames_count = len(arange(0, self.duration, self.interval))
        columns = self._calc_columns(frames_count, self.width, self.height)
        master_height = self.height * int(math.ceil(float(frames_count) / columns))
        master = Image.new(mode="RGBA", size=(self.width * columns, master_height))

        for n, frame in enumerate(frames):
            with Image.open(frame) as image:
                x, y = self.width * column, self.height * line

                start = n * self.interval
                end = (n + 1) * self.interval
                self.thumbnails.append((start, end, x, y))

                image = image.resize((self.width, self.height), Image.ANTIALIAS)
                master.paste(image, (x, y))

                column += 1

                if column == columns:
                    line += 1
                    column = 0

        master.save(self._image_name)
        self.tempdir.cleanup()

    def to_vtt(self):
        def _format_time(secs):
            delta = timedelta(seconds=secs)
            return ("0%s.000" % delta)[:12]

        _lines = ["WEBVTT\n\n"]
        _img_src = self.basepath + self._image_name

        for start, end, x, y in self.thumbnails:
            _thumbnail = "%s --> %s\n%s#xywh=%d,%d,%d,%d\n\n" % (
                _format_time(start), _format_time(end),
                _img_src, x, y, self.width, self.height
            )
            _lines.append(_thumbnail)

        with open(self._vtt_name, "w") as vtt:
            vtt.writelines(_lines)
