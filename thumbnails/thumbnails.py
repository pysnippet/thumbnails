import concurrent.futures
import glob
import math
import os
import subprocess
from datetime import timedelta
from tempfile import TemporaryDirectory

from PIL import Image
from imageio_ffmpeg import get_ffmpeg_exe

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

    def get_compress(self):
        raise NotImplementedError

    @property
    def width(self):
        if not self._w:
            self._w = max(self._min_width, self._width * self.get_compress())
        return self._w

    @property
    def height(self):
        if not self._h:
            self._h = max(self._min_height, self._height * self.get_compress())
        return self._h


class Thumbnails(_ThumbnailMixin, _FFMpeg):
    def __init__(self, filename):
        self.__compress = 1
        self.__interval = 1
        self.__basepath = ""
        self.thumbnails = []
        self.tempdir = TemporaryDirectory()
        self.filename = filename
        self._vtt_name = filename + ".vtt"
        self._image_name = filename + ".png"

        _FFMpeg.__init__(self, filename)
        _ThumbnailMixin.__init__(self, self.size)

    def get_compress(self):
        return self.__compress

    def set_compress(self, compress):
        if type(compress) not in (int, float):
            raise TypeError("Compress must be a number.")
        self.__compress = compress

    def get_interval(self):
        return self.__interval

    def set_interval(self, interval):
        if not isinstance(interval, int):
            raise TypeError("Interval must be an integer.")
        self.__interval = interval

    def get_basepath(self):
        return self.__basepath

    def set_basepath(self, path):
        self.__basepath = str(path)

    @staticmethod
    def _calc_columns(frames_count, width, height):
        ratio = 16 / 9
        for col in range(1, frames_count):
            if (col * width) / (frames_count // col * height) > ratio:
                return col

    def _extract_frame(self, start_time):
        _input_file = self.filename
        _output_file = "%s/%d-%s.png" % (self.tempdir.name, start_time, self.filename)
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
        _intervals = range(0, self.duration, self.get_interval())
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self._extract_frame, _intervals)

    def join_frames(self):
        line, column = 0, 0
        frames = sorted(glob.glob(self.tempdir.name + os.sep + "*.png"))
        frames_count = len(range(0, self.duration, self.get_interval()))
        columns = self._calc_columns(frames_count, self.width, self.height)
        master_height = self.height * int(math.ceil(float(frames_count) / columns))
        master = Image.new(mode="RGBA", size=(self.width * columns, master_height))

        for n, frame in enumerate(frames):
            with Image.open(frame) as image:
                x, y = self.width * column, self.height * line

                start = n * self.get_interval()
                end = (n + 1) * self.get_interval()
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
        def _format_time(seconds):
            return "0%s.000" % str(timedelta(seconds=seconds))

        _lines = ["WEBVTT\n\n"]
        _img_src = self.get_basepath() + self._image_name

        for start, end, x, y in self.thumbnails:
            _thumbnail = "%s --> %s\n%s#xywh=%d,%d,%d,%d\n\n" % (
                _format_time(start), _format_time(end),
                _img_src, x, y, self.width, self.height
            )
            _lines.append(_thumbnail)

        with open(self._vtt_name, "w") as vtt:
            vtt.writelines(_lines)
