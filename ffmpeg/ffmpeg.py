import os
import re
import subprocess
from functools import reduce

import imageio_ffmpeg
import numpy
from PIL import Image
from imageio.v3 import immeta

from sema import MemoSemaphore

FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()

semaphore = MemoSemaphore()


def memo_deco(func):
    def wrapper(*args, **kwargs):
        with semaphore:
            return func(*args, **kwargs)

    return wrapper


class FFMpeg:
    def __init__(self, filename):
        duration, size = self.parse_metadata(filename)
        self.area = reduce(int.__mul__, size)
        self.bytes = self.area * 4
        self.filename = filename
        self.duration = duration
        self.size = size

    @staticmethod
    def cross_platform_popen_params(bufsize=100000):
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
        time = [float(part.replace(",", ".")) for part in time.split(":")]
        return sum(mult * part for mult, part in zip((3600, 60, 1), time))

    @staticmethod
    def _parse_size(stdout):
        size_regex = r"\s(\d+)x(\d+)[,\s]"
        match_size = re.search(size_regex, stdout, re.M)
        return tuple(map(int, match_size.groups()))

    def parse_metadata(self, filename):
        meta = immeta(filename)
        duration, size = meta.get("duration"), meta.get("size")

        if not all([duration, size]):
            cmd = [FFMPEG_BINARY, "-hide_banner", "-i", filename]

            popen_params = self.cross_platform_popen_params()
            process = subprocess.Popen(cmd, **popen_params)
            _, stderr = process.communicate()
            stdout = stderr.decode("utf8", errors="ignore")

            process.terminate()
            del process

            duration = self._parse_duration(stdout)
            size = self._parse_size(stdout)

        return duration, size

    @staticmethod
    def frame_to_buffer(image):
        image = image.astype("uint8")
        return Image.fromarray(image)

    @memo_deco
    def get_frame(self, start_time):
        if start_time != 0:
            offset = min(1, start_time)
            i_arg = [
                "-ss", "%.06f" % (start_time - offset),
                "-i", self.filename,
                "-ss", "%.06f" % offset,
            ]
        else:
            i_arg = ["-i", self.filename]

        cmd = (
                [FFMPEG_BINARY]
                + i_arg
                + [
                    "-loglevel", "error",
                    "-f", "image2pipe",
                    "-vf", "scale=%d:%d" % tuple(self.size),
                    "-sws_flags", "bicubic",
                    "-pix_fmt", "rgba",
                    "-vcodec", "rawvideo", "-",
                ]
        )

        popen_params = self.cross_platform_popen_params(self.bytes + 100)
        process = subprocess.Popen(cmd, **popen_params)
        buffer = process.stdout.read(self.bytes)

        process.terminate()
        del process

        if hasattr(numpy, "frombuffer"):
            result = numpy.frombuffer(buffer, dtype="uint8")
        else:
            result = numpy.fromstring(buffer, dtype="uint8")

        result.shape = (*self.size[::-1], len(buffer) // self.area)

        return result
