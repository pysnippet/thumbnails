import os
import re
import subprocess
from functools import reduce

import imageio_ffmpeg
import numpy
from PIL import Image
from imageio.v3 import immeta

FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()


def cross_platform_popen_params(popen_params):
    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000
    return popen_params


class Ffmpeg:

    def __init__(self, filename):

        self.filename = filename

        duration, size = image_meta(filename)
        self.area = reduce(int.__mul__, size)
        self.bytes = self.area * 4
        self.duration = duration
        self.size = size

    @staticmethod
    def frame_to_buffer(image):
        image = image.astype("uint8")
        return Image.fromarray(image)

    def get_frame(self, start_time=0):
        if start_time != 0:
            offset = min(1, start_time)
            i_arg = [
                "-ss",
                "%.06f" % (start_time - offset),
                "-i",
                self.filename,
                "-ss",
                "%.06f" % offset,
            ]
        else:
            i_arg = ["-i", self.filename]

        cmd = (
                [FFMPEG_BINARY]
                + i_arg
                + [
                    "-loglevel",
                    "error",
                    "-f",
                    "image2pipe",
                    "-vf",
                    "scale=%d:%d" % tuple(self.size),
                    "-sws_flags",
                    "bicubic",
                    "-pix_fmt",
                    "rgba",
                    "-vcodec",
                    "rawvideo",
                    "-",
                ]
        )
        popen_params = cross_platform_popen_params(
            {
                "bufsize": self.bytes + 100,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "stdin": subprocess.DEVNULL,
            }
        )

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


def convert_to_seconds(time):
    time = [float(part.replace(",", ".")) for part in time.split(":")]
    return sum(mult * part for mult, part in zip((3600, 60, 1), time))


def parse_duration(stdout):
    duration_regex = r"duration[^\n]+([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])"
    match_duration = re.search(duration_regex, stdout, re.M | re.I)
    return convert_to_seconds(match_duration.group(1))


def parse_size(stdout):
    size_regex = r"\s(\d+)x(\d+)[,\s]"
    match_size = re.search(size_regex, stdout, re.M)
    return tuple(map(int, match_size.groups()))


def image_meta(filename):
    meta = immeta(filename)
    duration, size = meta.get("duration"), meta.get("size")

    if not all([duration, size]):
        cmd = [FFMPEG_BINARY, "-hide_banner", "-i", filename]

        popen_params = cross_platform_popen_params(
            {
                "bufsize": 10 ** 5,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "stdin": subprocess.DEVNULL,
            }
        )

        process = subprocess.Popen(cmd, **popen_params)
        _, stderr = process.communicate()
        stdout = stderr.decode("utf8", errors="ignore")

        process.terminate()
        del process

        duration = parse_duration(stdout)
        size = parse_size(stdout)

    return duration, size
