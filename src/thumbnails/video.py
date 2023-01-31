import concurrent.futures
import glob
import math
import os
import subprocess
from datetime import timedelta
from tempfile import TemporaryDirectory

from imageio_ffmpeg import get_ffmpeg_exe

from .ffmpeg import _FFMpeg
from .frame import _Frame

ffmpeg_bin = get_ffmpeg_exe()


def arange(start, stop, step):
    """Roughly equivalent to numpy.arange."""

    def _generator():
        nonlocal start
        while start < stop:
            yield start
            start += step

    return tuple(_generator())


class Video(_FFMpeg, _Frame):
    """This class gives methods to extract the thumbnail frames of a video."""

    def __init__(self, filepath, compress, interval):
        self.__filepath = filepath
        self.__compress = float(compress)
        self.__interval = float(interval)

        if self.__compress <= 0 or self.__compress > 1:
            raise ValueError("Compress must be between 0 and 1.")

        self.tempdir = TemporaryDirectory()

        _FFMpeg.__init__(self, filepath)
        _Frame.__init__(self, self.size)

    @property
    def filepath(self):
        return self.__filepath

    @property
    def compress(self):
        return self.__compress

    @property
    def interval(self):
        return self.__interval

    @staticmethod
    def calc_columns(frames_count, width, height):
        """Calculates an optimal number of columns for 16:9 aspect ratio."""
        ratio = 16 / 9
        for col in range(1, frames_count):
            if (col * width) / (frames_count // col * height) > ratio:
                return col

    def _extract_frame(self, start_time):
        """Extracts a single frame from the video by the offset."""
        offset = str(timedelta(seconds=start_time))
        filename = "%s.png" % offset.replace(":", "-")
        output = os.path.join(self.tempdir.name, filename)
        os.close(os.open(output, os.O_CREAT, mode=0o664))

        cmd = (
            ffmpeg_bin,
            "-ss", offset,
            "-i", self.filepath,
            "-loglevel", "error",
            "-vframes", "1",
            output,
            "-y",
        )

        subprocess.Popen(cmd).wait()

    def extract_frames(self):
        """Extracts the frames from the video by given intervals."""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self._extract_frame, arange(0, self.duration, self.interval))

    def thumbnails(self, master_size=False):
        """This generator function yields a thumbnail data on each iteration.

        The thumbnail data is a tuple of fields describing the current frame.
        The structure of the thumbnail data is (frame, start, end, x, y).
            - frame: The filename of the current frame (usually in temp-files).
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
