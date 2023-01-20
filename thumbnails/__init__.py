import json
import os
import shutil
from datetime import timedelta
from distutils.dir_util import copy_tree

from PIL import Image

from .formatter import FileFormatter
from .formatter import FormatterFactory
from .thumbnails import Thumbnails
from .thumbnails import arange

DEFAULT_AS = "vtt"
DEFAULT_COMPRESS = 1.
DEFAULT_INTERVAL = 1.
DEFAULT_BASEPATH = ""


def register_formatter(typename):
    """Register a new thumbnail formatter to the factory."""

    def _register_factory(cls):
        if not issubclass(cls, FileFormatter):
            raise ValueError("The formatter must implement the FileFormatter interface.")

        cls.extension = typename
        FormatterFactory.thumbnails[typename] = cls
        return cls

    return _register_factory


@register_formatter("vtt")
class VTTFormatter(FileFormatter):
    """Implements the methods for generating thumbnails in the WebVTT format."""

    def __init__(self, video):
        super().__init__(video)
        self._master_name = self.filename + ".png"

    def prepare_thumbnails(self):
        _thumbnails = self.thumbnails(True)
        master = Image.new(mode="RGBA", size=next(_thumbnails))

        for frame, start, end, x, y in self.thumbnails():
            with Image.open(frame) as image:
                image = image.resize((self.width, self.height), Image.ANTIALIAS)
                master.paste(image, (x, y))

        master.save(self._master_name)
        self.tempdir.cleanup()

    def generate(self):
        def _format_time(secs):
            delta = timedelta(seconds=secs)
            return ("0%s.000" % delta)[:12]

        _lines = ["WEBVTT\n\n"]
        _img_src = self.basepath + self._master_name

        for frame, start, end, x, y in self.thumbnails():
            _thumbnail = "%s --> %s\n%s#xywh=%d,%d,%d,%d\n\n" % (
                _format_time(start), _format_time(end),
                _img_src, x, y, self.width, self.height
            )
            _lines.append(_thumbnail)

        with open(self.thumbnail_file, "w") as fp:
            fp.writelines(_lines)


@register_formatter("json")
class JSONFormatter(FileFormatter):
    """Implements the methods for generating thumbnails in the JSON format."""

    def __init__(self, video):
        super().__init__(video)
        self._outdir = "outdir"  # temp dirname

    def prepare_thumbnails(self):
        if os.path.isdir(self._outdir):
            shutil.rmtree(self._outdir)
        copy_tree(self.tempdir.name, self._outdir)
        self.tempdir.cleanup()

    def generate(self):
        _content = {}

        for frame, start, end, x, y in self.thumbnails():
            frame = self._outdir + os.sep + os.path.split(frame)[1]
            with Image.open(frame) as image:
                image.resize((self.width, self.height), Image.ANTIALIAS).save(frame)
                _thumbnail = {
                    "src": self.basepath + frame,
                    "width": "%spx" % self.width,
                }
                _content[int(start)] = _thumbnail

        with open(self.thumbnail_file, "w") as fp:
            json.dump(_content, fp, indent=2)


__version__ = "v1.0"
__all__ = (
    "register_formatter",
    "FormatterFactory",
    "FileFormatter",
    "JSONFormatter",
    "VTTFormatter",
    "Thumbnails",
)
