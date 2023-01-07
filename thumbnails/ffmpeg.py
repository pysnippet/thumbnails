import concurrent.futures
import glob
import math
import os
import re
import subprocess
from datetime import timedelta
from tempfile import TemporaryDirectory

from PIL import Image
from imageio.v3 import immeta
from imageio_ffmpeg import get_ffmpeg_exe

from .thumbnails import _ThumbnailMixin

ffmpeg_bin = get_ffmpeg_exe()


class FFMpeg(_ThumbnailMixin):
    def __init__(self, filename):
        self.__compress = 1
        self.__interval = 1
        self.thumbnails = []
        duration, size = self._parse_metadata(filename)
        _ThumbnailMixin.__init__(self, size)
        self.tempdir = TemporaryDirectory()
        self.duration = int(duration + 1)
        self.filename = filename

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

    @staticmethod
    def calc_columns(frames_count, width, height):
        ratio = 16 / 9
        for col in range(1, frames_count):
            if (col * width) / (frames_count // col * height) > ratio:
                return col

    @staticmethod
    def _cross_platform_popen_params(bufsize=100000):
        popen_params = {
            "bufsize": bufsize,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "stdin": subprocess.DEVNULL,
        }
        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000
        return popen_params

    @staticmethod
    def _parse_duration(stdout):
        duration_regex = r"duration[^\n]+([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])"
        time = re.search(duration_regex, stdout, re.M | re.I).group(1)
        time = (float(part.replace(",", ".")) for part in time.split(":"))
        return sum(mult * part for mult, part in zip((3600, 60, 1), time))

    @staticmethod
    def _parse_size(stdout):
        size_regex = r"\s(\d+)x(\d+)[,\s]"
        match_size = re.search(size_regex, stdout, re.M)
        return tuple(map(int, match_size.groups()))

    def _parse_metadata(self, filename):
        meta = immeta(filename)
        duration, size = meta.get("duration"), meta.get("size")

        if not all((duration, size)):
            cmd = (ffmpeg_bin, "-hide_banner", "-i", filename)

            popen_params = self._cross_platform_popen_params()
            process = subprocess.Popen(cmd, **popen_params)
            _, stderr = process.communicate()
            stdout = stderr.decode("utf8", errors="ignore")

            duration = self._parse_duration(stdout)
            size = self._parse_size(stdout)

        return duration, size

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
        columns = self.calc_columns(frames_count, self.width, self.height)
        master_height = self.height * int(math.ceil(float(frames_count) / columns))
        master = Image.new(mode="RGBA", size=(self.width * columns, master_height))

        print("WEBVTT\n")

        for n, frame in enumerate(frames):
            with Image.open(frame) as image:
                x, y = self.width * column, self.height * line

                print("0%s.000 --> 0%s.000" % (
                    str(timedelta(seconds=n * self.get_interval())),
                    str(timedelta(seconds=(n + 1) * self.get_interval())),
                    # return the whole duration if n + 1 does not exist
                ))
                print(self.filename + ".png#xywh=%d,%d,%d,%d\n" % (x, y, self.width, self.height))

                image = image.resize((self.width, self.height), Image.ANTIALIAS)
                master.paste(image, (x, y))

                column += 1

                if column == columns:
                    line += 1
                    column = 0

        master.save(self.filename + ".png")
        self.tempdir.cleanup()
