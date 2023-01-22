import json
import os
import shutil
from abc import ABCMeta, abstractmethod
from datetime import timedelta
from distutils.dir_util import copy_tree

from PIL import Image


def register_thumbnail(typename):
    """Register a new thumbnail formatter to the factory."""

    def _register_factory(cls):
        if not issubclass(cls, Thumbnail):
            raise ValueError("The formatter must implement the Thumbnail interface.")

        cls.extension = typename
        ThumbnailFactory.thumbnails[typename] = cls
        return cls

    return _register_factory


class Thumbnail(metaclass=ABCMeta):
    """Any thumbnail describing format should implement the base Formatter."""

    extension = None

    def __init__(self, video, base):
        self.video = video
        self.base = base

    def __getattr__(self, item):
        """Delegate all other attributes to the video."""
        return getattr(self.video, item)

    @property
    def file(self):
        """Return the name of the thumbnail file."""
        return "%s.%s" % (self.filename, self.extension)

    @abstractmethod
    def prepare_frames(self):
        """Prepare the thumbnails before generating the output."""

    @abstractmethod
    def generate(self):
        """Generate the thumbnails for the given video."""


class ThumbnailFactory:
    """A factory for creating thumbnail formatter."""

    thumbnails = {}

    @classmethod
    def create_thumbnail(cls, typename, *args, **kwargs) -> Thumbnail:
        """Create a new thumbnail formatter by the given typename."""
        try:
            return cls.thumbnails[typename](*args, **kwargs)
        except KeyError:
            raise ValueError("The formatter type '%s' is not registered." % typename)


@register_thumbnail("vtt")
class ThumbnailVTT(Thumbnail):
    """Implements the methods for generating thumbnails in the WebVTT format."""

    def __init__(self, video, base):
        super().__init__(video, base)
        self._master_name = self.filename + ".png"

    def prepare_frames(self):
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
        _img_src = self.base + self._master_name

        for frame, start, end, x, y in self.thumbnails():
            _thumbnail = "%s --> %s\n%s#xywh=%d,%d,%d,%d\n\n" % (
                _format_time(start), _format_time(end),
                _img_src, x, y, self.width, self.height
            )
            _lines.append(_thumbnail)

        with open(self.file, "w") as fp:
            fp.writelines(_lines)


@register_thumbnail("json")
class ThumbnailJSON(Thumbnail):
    """Implements the methods for generating thumbnails in the JSON format."""

    def __init__(self, video, base):
        super().__init__(video, base)
        self._outdir = "outdir"  # temp dirname

    def prepare_frames(self):
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
                    "src": self.base + frame,
                    "width": "%spx" % self.width,
                }
                _content[int(start)] = _thumbnail

        with open(self.file, "w") as fp:
            json.dump(_content, fp, indent=2)
