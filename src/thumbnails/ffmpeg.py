import os
import re
import subprocess

from imageio.v3 import immeta
from imageio_ffmpeg import get_ffmpeg_exe

ffmpeg_bin = get_ffmpeg_exe()


class _FFMpeg:
    """This class is used to parse the metadata of a video file."""

    def __init__(self, filepath):
        self.duration, self.size = self._parse_metadata(filepath)

    @staticmethod
    def _parse_duration(stdout):
        """Parse the duration of a video from stdout."""
        duration_regex = r"duration[^\n]+([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])"
        time = re.search(duration_regex, stdout, re.M | re.I).group(1)
        time = (float(part.replace(",", ".")) for part in time.split(":"))
        return sum(mult * part for mult, part in zip((3600, 60, 1), time))

    @staticmethod
    def _parse_size(stdout):
        """Parse the size of a video from stdout."""
        size_regex = r"\s(\d+)x(\d+)[,\s]"
        match_size = re.search(size_regex, stdout, re.M)
        return tuple(map(int, match_size.groups()))

    def _parse_metadata(self, filepath):
        """Parse the metadata of a video file."""
        meta = immeta(filepath)
        duration, size = meta.get("duration"), meta.get("size")

        if not all((duration, size)):
            # Parse the metadata of the video formats
            # that are not supported by imageio.

            process = subprocess.Popen(
                (ffmpeg_bin, "-hide_banner", "-i", filepath),
                bufsize=100000,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                creationflags=0x08000000 if os.name == "nt" else 0,
            )
            _, stderr = process.communicate()
            stdout = (stderr or b"").decode("utf8", errors="ignore")

            duration = self._parse_duration(stdout)
            size = self._parse_size(stdout)

        return duration, size
